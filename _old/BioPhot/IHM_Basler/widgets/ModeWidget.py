# Libraries to import
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QApplication, QLabel

#-------------------------------------------------------------------------------------------------------

class Mode_Widget(QWidget):
    """
    Widget used to set our utilization mode.

    Args:
        QWidget (class): QWidget can be put in another widget and / or window.
    """
    def __init__(self, mode="Manual"):
        """
        Initialisation of our widget.
        """
        super().__init__()
        # Adding all to the mainLayout
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(labelAutomatic)
        # mainLayout.addWidget(self.toggle)
        mainLayout.addWidget(labelManual)
        self.setLayout(mainLayout)

#-------------------------------------------------------------------------------------------------------

# Launching as main for tests
if __name__ == "__main__":
    app = QApplication([])
    w = Mode_Widget()
    w.show()
    app.exec()