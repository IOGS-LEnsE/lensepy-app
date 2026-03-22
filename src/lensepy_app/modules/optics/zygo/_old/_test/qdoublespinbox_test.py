import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QDoubleSpinBox, QLabel
)
from PyQt6.QtCore import Qt

class DoubleSpinBoxExample(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Exemple de QDoubleSpinBox")
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout()

        # Création du QDoubleSpinBox
        self.spin_box = QDoubleSpinBox()
        self.spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_box.setRange(0.0, 100.0)        # Valeur min/max
        self.spin_box.setSingleStep(0.5)          # Incrément à chaque clic
        self.spin_box.setDecimals(2)              # Nombre de décimales affichées
        self.spin_box.setSuffix(" kg")            # Suffixe (optionnel)

        # Création du QLabel pour afficher la valeur
        self.label = QLabel("Valeur : 0.00 kg")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Connexion du signal valueChanged à une méthode
        self.spin_box.valueChanged.connect(self.update_label)

        # Ajout des widgets au layout
        layout.addWidget(self.spin_box)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def update_label(self, value):
        self.label.setText(f"Valeur : {value:.2f} kg")

# Lancement de l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DoubleSpinBoxExample()
    window.show()
    sys.exit(app.exec())
