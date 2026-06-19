import sys
from PyQt6.QtWidgets import QApplication
from plot import create_health_window

app = QApplication(sys.argv)
win = create_health_window()
win.show()
sys.exit(app.exec())