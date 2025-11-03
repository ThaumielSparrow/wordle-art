import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

import gui

if __name__ == "__main__":
    app = QApplication(sys.argv)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = gui.WordleGUI()

    window.show()
    sys.exit(app.exec())