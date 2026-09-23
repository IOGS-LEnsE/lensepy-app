#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Détection robuste d'un cercle englobant une figure d'interférence Zygo.

Principe
--------
1. Réduction de l'image (pour le temps réel).
2. Génération de plusieurs échelles de l'image.
3. Détection de cercles candidats par Hough sur les échelles fines.
4. Score des candidats sur plusieurs échelles, basé notamment sur :
   - cohérence de la direction du gradient radial ;
   - support angulaire ;
   - persistance multi-échelle.
5. Sélection du cercle final.
6. Marge optionnelle pour fabriquer le masque utilisé ensuite par le
   déroulement de phase.
7. En mode --track, recherche locale autour du cercle précédent.

Dépendances:
    pip install opencv-python numpy

Exemple:
    python detect_pupil.py interfero_zygo.png --show

Pour une caméra:
    appeler detect_circle(frame, state) à chaque image.
"""

import argparse
import math
from dataclasses import dataclass
from typing import Optional, Tuple, List
from matplotlib import pyplot as plt

import cv2
import numpy as np


@dataclass
class Circle:
    x: float
    y: float
    r: float
    score: float = 0.0


@dataclass
class DetectorState:
    circle: Optional[Circle] = None


class MultiScaleCircleDetector:
    def __init__(
        self,
        downsample=4,
        sigmas=(1.5, 3.0, 6.0),
        ntheta=360,
        hough_param2=24,
        max_candidates=12,
        mask_margin=0.99,
    ):
        self.downsample = downsample
        self.sigmas = tuple(sigmas)
        self.ntheta = ntheta
        self.hough_param2 = hough_param2
        self.max_candidates = max_candidates
        self.mask_margin = mask_margin

        theta = np.linspace(0, 2 * np.pi, ntheta, endpoint=False)
        self.cos_t = np.cos(theta).astype(np.float32)
        self.sin_t = np.sin(theta).astype(np.float32)

    # ------------------------------------------------------------
    # Préparation multi-échelle
    # ------------------------------------------------------------
    def _prepare_scales(self, gray_small):
        fields = []

        for sigma in self.sigmas:
            blur = cv2.GaussianBlur(
                gray_small, (0, 0), sigmaX=sigma, sigmaY=sigma
            )

            gx = cv2.Sobel(blur, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(blur, cv2.CV_32F, 0, 1, ksize=3)
            mag = cv2.magnitude(gx, gy)

            # Seuil de référence pour mesurer le support du contour.
            threshold = float(np.percentile(mag, 85))

            fields.append((gx, gy, threshold))

        return fields

    # ------------------------------------------------------------
    # Score d'un cercle
    #
    # Un bord réel de pupille présente généralement une direction
    # de gradient radiale cohérente sur une grande partie du cercle.
    # Les franges ont, elles, des gradients de polarité alternée.
    # ------------------------------------------------------------
    def _score_circle(self, fields, x, y, r):
        if r <= 2:
            return -1.0

        scores = []

        # On autorise quelques pixels d'incertitude sur le rayon.
        radial_offsets = (-3, -2, -1, 0, 1, 2, 3)

        for gx, gy, threshold in fields:
            radial_derivatives = []

            for dr in radial_offsets:
                rr = r + dr

                xs = x + rr * self.cos_t
                ys = y + rr * self.sin_t

                xs = xs.astype(np.float32)[None, :]
                ys = ys.astype(np.float32)[None, :]

                gxv = cv2.remap(
                    gx, xs, ys, cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_CONSTANT
                )[0]

                gyv = cv2.remap(
                    gy, xs, ys, cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_CONSTANT
                )[0]

                # dérivée dans la direction radiale
                dr_value = gxv * self.cos_t + gyv * self.sin_t
                radial_derivatives.append(dr_value)

            arr = np.stack(radial_derivatives, axis=0)

            # On prend, pour chaque angle, le contour le plus marqué
            # dans la petite bande radiale.
            idx = np.argmax(np.abs(arr), axis=0)
            v = arr[idx, np.arange(self.ntheta)]

            abs_v = np.abs(v)

            # Cohérence de polarité :
            # 1 -> presque tous les gradients pointent dans la même direction
            # 0 -> polarités mélangées, typique de nombreuses franges.
            polarity = abs(np.sum(v)) / (np.sum(abs_v) + 1e-6)

            # Fraction du cercle avec un gradient significatif.
            support = float(np.mean(abs_v > threshold))

            # Force robuste du gradient.
            strength = float(
                np.median(abs_v) / (threshold + 1e-6)
            )

            # Pondération volontairement favorable à la cohérence de polarité.
            scale_score = (
                0.65 * polarity
                + 0.25 * support
                + 0.10 * np.tanh(strength)
            )

            scores.append(scale_score)

        return float(np.mean(scores))

    # ------------------------------------------------------------
    # Hough = générateur de candidats, pas décision finale.
    # ------------------------------------------------------------
    def _hough_candidates(self, gray_small):
        h, w = gray_small.shape
        min_dim = min(h, w)

        min_r = max(10, int(0.25 * min_dim))
        max_r = max(min_r + 5, int(0.49 * min_dim))

        candidates = []

        # Les petites échelles sont utilisées pour générer des candidats.
        for sigma in self.sigmas[:2]:
            blur = cv2.GaussianBlur(
                gray_small, (0, 0), sigmaX=sigma, sigmaY=sigma
            )

            circles = cv2.HoughCircles(
                blur,
                cv2.HOUGH_GRADIENT,
                dp=1.2,
                minDist=max(20, int(0.20 * min_dim)),
                param1=70,
                param2=self.hough_param2,
                minRadius=min_r,
                maxRadius=max_r,
            )

            if circles is None:
                continue

            for x, y, r in circles[0]:
                candidates.append(Circle(float(x), float(y), float(r)))

        # Suppression des doublons grossiers.
        candidates.sort(key=lambda c: c.r, reverse=True)

        unique = []
        for c in candidates:
            duplicate = False

            for u in unique:
                dc = math.hypot(c.x - u.x, c.y - u.y)
                dr = abs(c.r - u.r)

                if dc < 0.05 * min_dim and dr < 0.05 * min_dim:
                    duplicate = True
                    break

            if not duplicate:
                unique.append(c)

        return unique[: self.max_candidates]

    # ------------------------------------------------------------
    # Recherche locale autour d'un cercle candidat.
    # ------------------------------------------------------------
    def _refine(self, fields, c):
        best = Circle(c.x, c.y, c.r, self._score_circle(fields, c.x, c.y, c.r))

        # Recherche grossière puis fine.
        for span, step in ((4.0, 1.0), (1.5, 0.5)):
            bx, by, br = best.x, best.y, best.r

            xs = np.arange(bx - span, bx + span + 1e-6, step)
            ys = np.arange(by - span, by + span + 1e-6, step)
            rs = np.arange(br - span, br + span + 1e-6, step)

            for x in xs:
                for y in ys:
                    for r in rs:
                        score = self._score_circle(fields, x, y, r)

                        if score > best.score:
                            best = Circle(float(x), float(y), float(r), score)

        return best

    # ------------------------------------------------------------
    # Détection globale
    # ------------------------------------------------------------
    def detect(self, gray):
        if gray.ndim != 2:
            raise ValueError("L'image doit être en niveaux de gris.")

        h, w = gray.shape

        # Réduction pour accélérer la détection.
        small_w = max(64, int(round(w / self.downsample)))
        small_h = max(64, int(round(h / self.downsample)))

        gray_small = cv2.resize(
            gray,
            (small_w, small_h),
            interpolation=cv2.INTER_AREA
        )

        fields = self._prepare_scales(gray_small)
        candidates = self._hough_candidates(gray_small)

        if not candidates:
            return None, None

        # Hough fournit la géométrie grossière. On ne laisse pas
        # l'optimisation locale dériver librement vers une frange :
        # le raffinement est volontairement limité à +/- 1 px
        # dans l'image réduite.
        scored = []
        for c in candidates:
            c.score = self._score_circle(fields, c.x, c.y, c.r)
            scored.append(c)

        best0 = max(scored, key=lambda c: c.score)

        # Raffinement très local uniquement.
        best = best0
        for dx in np.arange(-1.0, 1.01, 0.5):
            for dy in np.arange(-1.0, 1.01, 0.5):
                for dr in np.arange(-1.0, 1.01, 0.5):
                    x = best0.x + dx
                    y = best0.y + dy
                    r = best0.r + dr
                    score = self._score_circle(fields, x, y, r)
                    if score > best.score:
                        best = Circle(float(x), float(y), float(r), score)

        # Retour coordonnées image originale.
        result = Circle(
            best.x * w / small_w,
            best.y * h / small_h,
            best.r * 0.5 * (w / small_w + h / small_h),
            best.score,
        )

        return result, gray_small

    # ------------------------------------------------------------
    # Tracking local.
    # ------------------------------------------------------------
    def track(self, gray, previous: Circle, search_xy=25, search_r=15):
        h, w = gray.shape

        small_w = max(64, int(round(w / self.downsample)))
        small_h = max(64, int(round(h / self.downsample)))

        gray_small = cv2.resize(
            gray,
            (small_w, small_h),
            interpolation=cv2.INTER_AREA
        )

        sx = small_w / w
        sy = small_h / h

        px = previous.x * sx
        py = previous.y * sy
        pr = previous.r * 0.5 * (sx + sy)

        fields = self._prepare_scales(gray_small)

        # Recherche locale en coordonnées réduites.
        xy_span = search_xy * 0.5 * (sx + sy)
        r_span = search_r * 0.5 * (sx + sy)

        best = None

        # Pas volontairement assez large pour rester rapide.
        for x in np.arange(px - xy_span, px + xy_span + 0.01, 2.0):
            for y in np.arange(py - xy_span, py + xy_span + 0.01, 2.0):
                for r in np.arange(pr - r_span, pr + r_span + 0.01, 2.0):

                    if r <= 5:
                        continue

                    score = self._score_circle(fields, x, y, r)

                    if best is None or score > best.score:
                        best = Circle(float(x), float(y), float(r), score)

        if best is None:
            return None

        return Circle(
            best.x / sx,
            best.y / sy,
            best.r / (0.5 * (sx + sy)),
            best.score
        )

    # ------------------------------------------------------------
    # Masque final
    # ------------------------------------------------------------
    @staticmethod
    def make_mask(shape, circle, margin=0.99):
        h, w = shape[:2]
        yy, xx = np.ogrid[:h, :w]

        r = circle.r * margin

        mask = (
            (xx - circle.x) ** 2
            + (yy - circle.y) ** 2
            <= r ** 2
        )

        return mask.astype(np.uint8) * 255


def draw_result(gray, circle, mask=None):
    vis = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    if circle is not None:
        center = (int(round(circle.x)), int(round(circle.y)))
        radius = int(round(circle.r))

        cv2.circle(vis, center, radius, (0, 255, 0), 2)
        cv2.circle(vis, center, 3, (0, 0, 255), -1)

        text = (
            f"x={circle.x:.1f}  y={circle.y:.1f}  "
            f"R={circle.r:.1f}  score={circle.score:.3f}"
        )

        cv2.putText(
            vis,
            text,
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    if mask is not None:
        overlay = vis.copy()
        overlay[mask > 0] = (
            0.7 * overlay[mask > 0]
            + 0.3 * np.array([255, 255, 0])
        ).astype(np.uint8)

        vis = cv2.addWeighted(vis, 0.65, overlay, 0.35, 0)

    return vis


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--downsample", type=int, default=4)
    parser.add_argument("--margin", type=float, default=0.99)

    args = parser.parse_args()

    ## Open image
    gray = cv2.imread('interfero_pre.png', cv2.IMREAD_GRAYSCALE)

    plt.figure()
    plt.imshow(gray, cmap='gray')
    plt.show()

    if gray is None:
        raise FileNotFoundError(args.image)

    detector = MultiScaleCircleDetector(
        downsample=args.downsample,
        sigmas=(1.5, 3.0, 6.0),
        ntheta=360,
        hough_param2=24,
        max_candidates=12,
        mask_margin=args.margin,
    )

    circle, _ = detector.detect(gray)

    if circle is None:
        print("Aucun cercle détecté.")
        return 2

    print(f"Centre X : {circle.x:.2f} px")
    print(f"Centre Y : {circle.y:.2f} px")
    print(f"Rayon    : {circle.r:.2f} px")
    print(f"Score    : {circle.score:.4f}")

    h, w = gray.shape
    downsampling = 4
    small_w = max(64, int(round(w / downsampling)))
    small_h = max(64, int(round(h / downsampling)))
    mask = detector.make_mask(gray.shape, circle, args.margin)
    mask_small = cv2.resize(
        mask,
        (small_w, small_h),
        interpolation=cv2.INTER_AREA
    )
    gray_small = cv2.resize(
        gray,
        (small_w, small_h),
        interpolation=cv2.INTER_AREA
    )
    circle.x = circle.x / downsampling
    circle.y = circle.y / downsampling
    circle.r = circle.r / downsampling

    vis = draw_result(gray_small, circle, mask_small)

    print('SHOW')
    cv2.imshow("Zygo - detection circulaire", vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
