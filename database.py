import _sqlite3
import os

DB_NAME = "opensky_data.db"

def connect_db():
    conn = _sqlite3.connect(DB_NAME)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def create_tables():

    with connect_db() as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS continent (
                           continent_id INTEGER PRIMARY KEY AUTOINCREMENT,
                           continent_name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS country (
                           country_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            country_name TEXT NOT NULL UNIQUE,
                            continent_id INTEGER REFERENCES continent(continent_id));

        CREATE TABLE IF NOT EXISTS airport (
                           icao_code text primary key,
                           airport_name text,
                           country_id integer references country(country_id),
                           latitude real,
                           longitude real,
                           type text);
        CREATE TABLE IF NOT EXISTS aircraft (
                           icao24 text primary key,
                           callsign text,
                           country_id integer references country(country_id),
                           last_updated text);

        CREATE TABLE IF NOT EXISTS flight_data (
                flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                aircraft_id TEXT REFERENCES aircraft(icao24),
                departure_airport_id TEXT REFERENCES airport(icao_code),
                arrival_airport_id TEXT REFERENCES airport(icao_code),
                departure_date_time TEXT,
                arrival_date_time TEXT);

        CREATE TABLE IF NOT EXISTS location (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                aircraft_id TEXT REFERENCES aircraft(icao24),
                flight_id INTEGER REFERENCES flight_data(flight_id),
                true_track REAL,
                longitude REAL,
                latitude REAL,
                baro_altitude REAL,
                geo_altitude REAL,
                velocity REAL,
                on_ground INTEGER,
                time_pos TEXT,
                UNIQUE(aircraft_id, time_pos)
            );

        CREATE TABLE IF NOT EXISTS import_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                imported_at TEXT,
                records_received INTEGER,
                records_saved INTEGER,
                status TEXT,
                error_message TEXT
            );
        create index IF NOT EXISTS idx_location_flight ON location(flight_id);
                           ''')
        conn.commit()

if __name__ == "__main__":
    if not os.path.exists(DB_NAME):
        create_tables()
        print(f"Database '{DB_NAME}' created and tables initialized.")
    else:
        print(f"Database '{DB_NAME}' already exists. No action taken.")