from PyQt6.QtWidgets import QApplication
import sys
from plot import create_airport_window

app = QApplication(sys.argv)
win = create_airport_window()
win.show()
sys.exit(app.exec())