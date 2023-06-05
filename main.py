
import sys

from PyQt5.QtWidgets import QApplication
from ui.gui.windows import MainWindow
from ui.resources import resources


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
