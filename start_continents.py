import sys
from PyQt6.QtWidgets import QApplication
from plot import create_continents_window

app = QApplication(sys.argv)
win = create_continents_window()
win.show()
sys.exit(app.exec())