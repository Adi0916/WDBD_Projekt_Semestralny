import sys
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLineEdit, QPushButton, QLabel, QGridLayout, QScrollArea)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Import Twoich funkcji (zakładam, że są w pliku data_queries.py)
from queries import (get_live_radar_data, get_airport_traffic_stats,
                          get_aircraft_trajectory, get_continent_distribution_stats,
                          get_system_health_report)

class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class VisualizationWindow(QMainWindow):
    # Dodajemy argument 'defaults' (domyślnie pusty słownik)
    def __init__(self, title, update_func, filter_map, defaults=None):
        super().__init__()
        self.setWindowTitle(title)
        self.update_func = update_func
        self.filter_map = filter_map
        self.defaults = defaults or {}

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        self.inputs = {}
        grid = QGridLayout()
        for i, (label, param_key) in enumerate(filter_map.items()):
            grid.addWidget(QLabel(label), i // 2, (i % 2) * 2)
            input_box = QLineEdit()

            # --- TUTAJ USTWIAMY DOMYŚLNĄ WARTOŚĆ ---
            if param_key in self.defaults:
                input_box.setText(str(self.defaults[param_key]))

            grid.addWidget(input_box, i // 2, (i % 2) * 2 + 1)
            self.inputs[param_key] = input_box
        layout.addLayout(grid)

        # Reszta klasy pozostaje bez zmian...
        self.canvas = ChartCanvas()
        layout.addWidget(self.canvas)

        btn = QPushButton(f"Refresh {title}")
        btn.clicked.connect(self.run_update)
        layout.addWidget(btn)

    def run_update(self):
        vals = {k: self.inputs[k].text() if self.inputs[k].text() else None for k in self.inputs}
        self.update_func(self.canvas, vals)

# --- Logika dla każdego modułu ---

def update_radar(canvas, f):
    data = get_live_radar_data(f['country'], f['continent'], f['on_ground'], f['category'])
    canvas.axes.cla()
    if data:
        df = pd.DataFrame(data, columns=['icao', 'call', 'cntry', 'cont', 'cat', 'lat', 'lon', 'alt', 'vel', 'og', 'time'])
        canvas.axes.scatter(df['lon'], df['lat'], c='blue', alpha=0.5)
    canvas.draw()

def update_traffic(canvas, f):
    airport = f.get('airport') if f.get('airport') else None
    d_from = f.get('date_from') if f.get('date_from') else None
    d_to = f.get('date_to') if f.get('date_to') else None

    data = get_airport_traffic_stats(airport, d_from, d_to)
    canvas.axes.cla()

    if not data:
        canvas.axes.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=12)
        canvas.draw()
        return

    df = pd.DataFrame(data, columns=['id', 'wylot', 'przylot', 'ruch'])

    df_sorted = df.sort_values(by='ruch', ascending=False)
    df_top = df_sorted.head(20).sort_values(by='ruch', ascending=True)

    bars = canvas.axes.barh(df_top['id'], df_top['ruch'], color='#2ca02c', alpha=0.7)

    num_items = len(df_top)
    if num_items >= 20:
        canvas.axes.set_title("Top 20 Most Active Airports", fontsize=12, fontweight='bold')
    else:
        canvas.axes.set_title(f"Activity of all {num_items} Airports", fontsize=12, fontweight='bold')

    canvas.axes.set_xlabel("Number of Operations")
    canvas.axes.set_ylabel("Airport Code")
    canvas.axes.grid(axis='x', linestyle='--', alpha=0.5)

    for bar in bars:
        width = bar.get_width()
        canvas.axes.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                         f'{int(width)}', ha='left', va='center', fontsize=9)

    canvas.figure.tight_layout()
    canvas.draw()

def update_trajectory(canvas, f):
    data = get_aircraft_trajectory(f['icao24'], f['time_from'])
    canvas.axes.cla()
    if data:
        df = pd.DataFrame(data, columns=['lat', 'lon', 'alt', 'vel', 'time'])
        canvas.axes.plot(df['lon'], df['lat'])
    canvas.draw()

def update_distribution(canvas, f):
    data = get_continent_distribution_stats()
    canvas.axes.cla()

    if data:
        df = pd.DataFrame(data, columns=['cont', 'count'])

        wedges, texts, autotexts = canvas.axes.pie(
            df['count'],
            labels=None,
            autopct='%1.1f%%',
            pctdistance=0.8,
            startangle=140,
            textprops={'fontsize': 10, 'weight': 'bold'}
        )

        canvas.axes.legend(
            wedges, df['cont'],
            title="Continents",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=9
        )

        #canvas.axes.set_title("Distribution by Continent", fontsize=14, fontweight='bold')

        canvas.figure.subplots_adjust(left=0.05, right=0.7, top=0.9, bottom=0.1)
        canvas.figure.tight_layout()
    else:
        canvas.axes.text(0.5, 0.5, 'No data available', ha='center', va='center')

    canvas.draw()

def update_health(canvas, f):
    data = get_system_health_report(f.get('status'))
    canvas.axes.cla()

    if not data:
        canvas.axes.text(0.5, 0.5, 'No health data available', ha='center', va='center')
        canvas.draw()
        return

    df = pd.DataFrame(data, columns=['id', 'date', 'recv', 'saved', 'status', 'err'])
    df = df.sort_values(by='id', ascending=True).tail(15)

    time_labels = [str(d).split('T')[1][:8] for d in df['date']]

    # Maksymalna wartość dla skalowania osi
    max_recv = df['recv'].max() if df['recv'].max() > 0 else 100

    # Rysowanie słupków
    bars = canvas.axes.barh(range(len(df)), df['recv'], color='#4a90e2', alpha=0.7)

    # Zmniejszenie marginesów, aby wykres był jak najszerszy
    canvas.figure.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)

    canvas.axes.set_yticks(range(len(df)))
    canvas.axes.set_yticklabels(time_labels, fontsize=8)

    # Ustalenie limitu osi X - dopasowane do najdłuższego słupka
    canvas.axes.set_xlim(0, max_recv * 1.05)

    for i, bar in enumerate(bars):
        status = df.iloc[i]['status']
        # Tekst wewnątrz słupka, zaczynający się od 2% jego szerokości
        canvas.axes.text(max_recv * 0.02, i, status,
                         va='center', fontsize=7, fontweight='bold', color='black')

    canvas.axes.set_title("Recent Activity", fontsize=12, fontweight='bold')
    canvas.axes.set_xlabel("Records Received")

    canvas.draw()

class WindowManager:
    def __init__(self):
        self.windows = {}

    def add_window(self, key, window_instance):
        self.windows[key] = window_instance

    def show(self, key):
        if key in self.windows:
            self.windows[key].show()
        else:
            print(f"Windows '{key}' does not exist.")

    def show_all(self):
        for win in self.windows.values():
            win.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    manager = WindowManager()

    # Uzupełnione definicje okien w menadżerze
    manager.add_window("radar", VisualizationWindow(
        "Live radar data",
        update_radar,
        {"Country": "country", "Continent": "continent", "Ground": "on_ground", "Category": "category"},
        defaults={"country": "None", "continent": "None", "on_ground": "None", "category": "None"}
    ))

    manager.add_window("airport", VisualizationWindow(
        "Airport traffic",
        update_traffic,
        {"Airport": "airport", "From": "date_from", "To": "date_to"},
        defaults={"airport": "", "date_from": "2026-01-01", "date_to": "2026-20-09"}
    ))

    manager.add_window("trajectory", VisualizationWindow(
        "Aircraft trajectory",
        update_trajectory,
        {"ICAO24": "icao24", "Time From": "time_from"},
        defaults={"icao24": "None", "time_from": "None"}
    ))

    manager.add_window("continents", VisualizationWindow(
        "Continent distribution",
        update_distribution,
        {}
    ))

    manager.add_window("health", VisualizationWindow(
        "System health report",
        update_health,
        {"Status": "status"},
        defaults={"status": ""}
    ))

    #radar nie działa bo queries źle działa
    #manager.show("radar")

    #działa super
    #manager.show("airport")

    #napraw
    #manager.show("trajectory")

    #działa super
    #manager.show("continents")

    #działa super
    #manager.show("health")

    sys.exit(app.exec())