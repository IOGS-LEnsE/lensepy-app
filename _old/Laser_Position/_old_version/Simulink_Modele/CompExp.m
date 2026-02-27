% puis exécuter le code ci-dessous
%% 1. LECTURE DES DONNEES
%le vecteur des fréquences de mesure
f=[10 24 40 80 100 120 200];
%le vecteur des amplitudes m
m=[21 20 17 10 6 4 1.1];
%le vecteur des phases mesurées
phi=[0 51 72 115 151 164 180];
%vecteur du module en dB
mod=20*log10(m/50e-3);
%% ==========================================================
%%% Les deux parties ci-dessous sont à réaliser séparément 
%%% pour superposer les courbes
%%%
%% 2. COURBE DE GAIN ========================================
% cliquer sur la partie haute de la fenêtre générée par l'analyse
hold on 
semilogx(f,mod,'o-r')
hold off
%% 3. COURBE DE PHASE =======================================
% cliquer sur la partie basse de la fenêtre générée par l'analyse
% puis exécuter le code ci-dessous
hold on 
semilogx(f,-phi,'o-r')
hold off