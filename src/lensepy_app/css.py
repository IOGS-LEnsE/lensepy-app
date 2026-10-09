__all__ = [
    'LAMBDA', 'BLUE_IOGS', 'ORANGE_IOGS',
    'STYLE_H1', 'STYLE_H2', 'STYLE_H3', 'NO_STYLE',
    'INACTIVATED_BUTTON', 'ACTIVATED_BUTTON', 'DISABLED_BUTTON',
    'BUTTON_HEIGHT', 'OPTIONS_BUTTON_HEIGHT'
]

#### Style Sheet for LEnsE API

# Symbols
LAMBDA = '\u03BB'

# Colors
# ------
BLUE_IOGS = '#0A3250'
ORANGE_IOGS = '#FF960A'
GREEN_IOGS = (0, 180, 0)
RED_IOGS = '#EE0000'
WHITE = '#000000'
GRAY = '#727272'
BLACK = '#FFFFFF'

# Styles
# ------
STYLE_H1 = {
    'WHITE': {
        'CLASSIC': f"font-size:18px; padding:0px; color:{BLUE_IOGS};font-weight: bold;",
        'LITE': f"font-size:14px; padding:0px; color:{BLUE_IOGS};font-weight: bold;"
    },
    'BLACK':{
        'CLASSIC': f"font-size:18px; padding:0px; color:{ORANGE_IOGS};font-weight: bold;",
        'LITE': f"font-size:14px; padding:0px; color:{ORANGE_IOGS};font-weight: bold;"
    }
}
STYLE_H2 = {
    'WHITE': {
        'CLASSIC': f"font-size:16px; padding:0px; color:{BLUE_IOGS}; font-weight: bold;",
        'LITE': f"font-size:12px; padding:0px; color:{BLUE_IOGS};font-weight: bold;"
    },
    'BLACK': {
        'CLASSIC': f"font-size:16px; padding:0px; color:white; font-weight: bold;",
        'LITE': f"font-size:12px; padding:0px; color:white;font-weight: bold;"
    }
}
STYLE_H3 = {
    'WHITE': {
        'CLASSIC': f"font-size:14px; padding:0px; color:{BLUE_IOGS};",
        'LITE': f"font-size:10px; padding:0px; color:{BLUE_IOGS};"
    },
    'BLACK': {
        'CLASSIC': f"font-size:14px; padding:0px; color:white;",
        'LITE': f"font-size:10px; padding:0px; color:white;"
    }
}
NO_STYLE = {
    'CLASSIC': f"background-color:{GRAY}; color:{BLACK}; font-size:14px;",
    'LITE': f"background-color:{GRAY}; color:{BLACK}; font-size:12px;"
}
STYLE_L = {
    'CLASSIC': f"font-size:14px; padding:0px; color:{ORANGE_IOGS}; font-weight: bold;",
    'LITE': f"font-size:10px; padding:0px; color:{ORANGE_IOGS}; font-weight: bold;"
}
STYLE_T = {
    'CLASSIC': f"font-size:14px; padding:5px; font-weight: bold; background-color: white;",
    'LITE': f"font-size:10px; padding:2px; font-weight: bold; background-color: white;"
}


styleCheckbox = f"font-size: 14px; padding: 3px; color: {BLUE_IOGS}; font-weight: normal;"
styleL = f"font-size:14px; padding:0px; color:{ORANGE_IOGS}; font-weight: bold;"
styleT = f"font-size:14px; padding:5px; font-weight: bold; background-color: white;"
styleL_s = f"font-size:10px; padding:0px; color:{ORANGE_IOGS}; font-weight: bold;"
styleT_s = f"font-size:10px; padding:2px; font-weight: bold; background-color: white;"


DISABLED_BUTTON = {
    'WHITE': {
        'CLASSIC': f"background-color:{GRAY}; color:{BLACK}; font-size:14px; border-radius: 10px;",
        'LITE': f"background-color:{GRAY}; color:{BLACK}; font-size:10px; border-radius: 10px;"
    },
    'BLACK': {
        'CLASSIC': f"background-color:{GRAY}; color:{WHITE}; font-size:14px; border-radius: 10px;",
        'LITE': f"background-color:{GRAY}; color:{WHITE}; font-size:10px; border-radius: 10px;"
    }
}
INACTIVATED_BUTTON = {
    'WHITE': {
        'CLASSIC': f"background-color:{BLUE_IOGS}; color:white; font-size:14px; font-weight:bold; border-radius: 10px;",
        'LITE': f"background-color:{BLUE_IOGS}; color:white; font-size:10px; border-radius: 10px;"
    },
    'BLACK': {
        'CLASSIC': f"background-color:{BLUE_IOGS}; color:white; font-size:14px; font-weight:bold; border-radius: 10px;",
        'LITE': f"background-color:{BLUE_IOGS}; color:white; font-size:10px; border-radius: 10px;"
    }
}
ACTIVATED_BUTTON = {
    'WHITE': {
        'CLASSIC': f"background-color:{ORANGE_IOGS}; color:white; font-size:14px; font-weight:bold; border-radius: 10px;",
        'LITE': f"background-color:{ORANGE_IOGS}; color:white; font-size:10px; font-weight:bold; border-radius: 10px;"
    },
    'BLACK': {
        'CLASSIC': f"background-color:{ORANGE_IOGS}; color:white; font-size:14px; font-weight:bold; border-radius: 10px;",
        'LITE': f"background-color:{ORANGE_IOGS}; color:white; font-size:10px; font-weight:bold; border-radius: 10px;"
    }
}

BUTTON_HEIGHT = {   #px
    'WHITE': {'CLASSIC': 37, 'LITE': 22},
    'BLACK': {'CLASSIC': 37, 'LITE': 22},
}
OPTIONS_BUTTON_HEIGHT = {   #px
    'WHITE': {'CLASSIC': 18, 'LITE': 14},
    'BLACK': {'CLASSIC': 18, 'LITE': 14},
}

StyleSheet = '''
#IOGSProgressBar {
    text-align: center;
    color: white;
    width: 10px; 
    min-height: 16px;
    max-height: 16px;
    border-radius: 6px;
}
#IOGSProgressBar::chunk {
    border-radius: 6px;
    background-color: #FF960A;
}
'''

def progress_bar_color(bg_color, fg_color):
    css_text = (f'QProgressBar {{ border: 2px solid #444;'
                f'border-radius: 5px; background-color: {bg_color};'
                f'color: white; }}'
                f' QProgressBar::chunk {{ background-color: {fg_color};'
                f'border-radius: 3px; }}')
    return css_text


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import (
        QApplication,
        QWidget, QLabel, QVBoxLayout, QPushButton,
)
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QPalette, QColor

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(10, 10, 10))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

    class MainWindow(QWidget):
        def __init__(self, theme='WHITE', size='CLASSIC'):
            super().__init__()
            if theme != 'WHITE':
                self.setPalette(palette)
            layout = QVBoxLayout()
            self.setLayout(layout)
            self.setWindowTitle('lensepy-app')
            self.label_H1 = QLabel('Test H1')
            self.label_H1.setStyleSheet(STYLE_H1[theme][size])
            layout.addWidget(self.label_H1)

            self.label_H2 = QLabel('Test H2')
            self.label_H2.setStyleSheet(STYLE_H2[theme][size])
            layout.addWidget(self.label_H2)

            self.label_H3 = QLabel('Test H3')
            self.label_H3.setStyleSheet(STYLE_H3[theme][size])
            layout.addWidget(self.label_H3)

            self.button_activ = QPushButton('Activated')
            self.button_activ.setStyleSheet(ACTIVATED_BUTTON[theme][size])
            self.button_activ.setFixedHeight(BUTTON_HEIGHT[theme][size])
            layout.addWidget(self.button_activ)

            self.button_activ = QPushButton('In Activated')
            self.button_activ.setStyleSheet(INACTIVATED_BUTTON[theme][size])
            self.button_activ.setFixedHeight(BUTTON_HEIGHT[theme][size])
            layout.addWidget(self.button_activ)

            self.button_activ = QPushButton('Disabled')
            self.button_activ.setStyleSheet(DISABLED_BUTTON[theme][size])
            self.button_activ.setFixedHeight(BUTTON_HEIGHT[theme][size])
            layout.addWidget(self.button_activ)


    app = QApplication(sys.argv)
    widget = MainWindow(theme='WHITE')
    widget.setMinimumWidth(300)
    widget2 = MainWindow(theme='BLACK')
    widget2.setMinimumWidth(300)
    widget.show()
    widget2.show()
    sys.exit(app.exec())