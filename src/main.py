from plot import create_airport_window, create_health_window, create_continents_window
import sys
from PyQt6.QtWidgets import QApplication  # lub PyQt5

def main():
    # 1. Musisz utworzyć instancję QApplication jako pierwszą
    app = QApplication(sys.argv)

    # 2. Teraz możesz bezpiecznie tworzyć okna
    airport_win = create_airport_window()
    continents_win = create_continents_window()
    health_win = create_health_window()

    # Opcjonalnie: wyświetl okna (jeśli nie robią tego funkcje create_...)
    airport_win.show()
    continents_win.show()
    health_win.show()

    # 3. Uruchom pętlę zdarzeń
    sys.exit(app.exec())

if __name__ == "__main__":
    main()