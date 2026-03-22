from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout

def remove_widget_at(grid_layout, row, column):
    item = grid_layout.itemAtPosition(row, column)  # Récupérer l'élément
    if item is not None:
        widget = item.widget()
        if widget is not None:
            grid_layout.removeWidget(widget)  # Retirer du layout
            widget.deleteLater()  # Supprimer proprement
            widget.setParent(None)  # Détruire toute affiliation avec le layout

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout(self)

        # Ajout de widgets à différentes positions
        self.layout.addWidget(QPushButton("A"), 0, 0)
        self.layout.addWidget(QPushButton("B"), 0, 1)
        self.layout.addWidget(QPushButton("C"), 1, 0)

        # Bouton pour supprimer le widget à (0,1)
        self.remove_button = QPushButton("Supprimer (0,1)")
        self.remove_button.clicked.connect(lambda: remove_widget_at(self.layout, 0, 1))
        self.layout.addWidget(self.remove_button, 1, 1)

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
