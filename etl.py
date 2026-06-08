import logging
from api_client import fetch_states, fetch_all_flights
from datetime import datetime, timezone
from database import connect_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BBOX_EUROPE = (35.0, 70.0, -10.0, 40.0)

def log_import_run(conn, received, saved, status, error_msg=None):
    conn.execute(
        '''INSERT INTO import_log (imported_at, records_received, records_saved, status, error_message)
           VALUES (?, ?, ?, ?, ?)''',
        (datetime.now(timezone.utc).isoformat(), received, saved, status, error_msg)
    )
    conn.commit()

def get_airport_info(icao):

    if not icao:
        return 'Unknown', 'Unknown'
    
    cities = {
        "EPWA": "Warsaw", "EPKK": "Krakow", "EPGD": "Gdansk", "EPMO": "Modlin",
        "EDDF": "Frankfurt", "EDDB": "Berlin", "EHAM": "Amsterdam", "EGLL": "London",
        "LFPG": "Paris", "LKPR": "Prague", "LOWW": "Vienna", "KJFK": "New York"
    }
    
    prefixes = {
        "EP": "Poland", "ED": "Germany", "ET": "Germany", "LK": "Czech Republic",
        "LZ": "Slovakia", "LH": "Hungary", "LO": "Austria", "LS": "Switzerland",
        "LF": "France", "EB": "Belgium", "EH": "Netherlands", "EG": "United Kingdom",
        "EI": "Ireland", "ES": "Sweden", "EN": "Norway", "EK": "Denmark",
        "EF": "Finland", "UM": "Lithuania", "UK": "Ukraine", "LI": "Italy",
        "LE": "Spain", "LP": "Portugal", "LG": "Greece", "K": "United States"
    }

    city = cities.get(icao, "Unknown")
    country = "Unknown"

    if icao[:2] in prefixes:
        country = prefixes[icao[:2]]
    elif icao[0] in prefixes:
        country = prefixes[icao[0]]
    
    return city, country


def run_radar_etl():
    logging.info("Starting RADAR ETL")

    with connect_db() as conn:
        try:
            data = fetch_states()
            states = data.get("states", [])
            if not states:
                logging.warning("No data received from API in given bounding box.")
                log_import_run(conn, 0, 0, "SUCCESS", "No Data")
                return
            
            recieved = len(states)
            saved = 0

            for state in states:
                try:
                    icao24 = state[0]
                    callsign = state[1].strip() if len(state) > 1 and state[1] else None
                    origin_country = state[2] if len(state) > 2 else "Unknown"
                    time_position = state[3] if len(state) > 3 else None
                    longitude = state[5] if len(state) > 5 else None
                    latitude = state[6] if len(state) > 6 else None
                    baro_altitude = state[7] if len(state) > 7 else None
                    on_ground = 1 if len(state) > 8 and state[8] else 0
                    velocity = state[9] if len(state) > 9 else None
                    true_track = state[10] if len(state) > 10 else None
                    geo_altitude = state[13] if len(state) > 13 else None
                    category = state[17] if len(state) > 17 else 0

                    
                    conn.execute('''
                        INSERT INTO country (country_name)
                        VALUES (?)
                        ON CONFLICT(country_name) DO NOTHING;
                    ''', (origin_country,))
                    c_res = conn.execute('SELECT country_id FROM country WHERE country_name = ?', (origin_country,))
                    country_id = c_res.fetchone()[0]
                    
                    conn.execute('''
                            INSERT INTO aircraft (icao24, callsign, country_id, aircraft_category, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(icao24) DO UPDATE SET
                        callsign = excluded.callsign,
                        country_id = excluded.country_id,
                        aircraft_category = excluded.aircraft_category,
                        last_updated = excluded.last_updated;
                    ''', (icao24, callsign, country_id, category, datetime.now(timezone.utc).isoformat()))
            
                    if time_position:
                        dt_pos = datetime.fromtimestamp(time_position, tz=timezone.utc).isoformat()
                        cur = conn.execute('''
                        INSERT INTO location (aircraft_id, true_track, longitude, latitude, baro_altitude, geo_altitude, velocity, on_ground, time_pos)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(aircraft_id, time_pos) DO NOTHING;
                    ''', (icao24, true_track, longitude, latitude, baro_altitude, geo_altitude, velocity, on_ground, dt_pos))
                    
                        if cur.rowcount > 0:
                            saved += 1
                except Exception as row_error:
                    logging.warning(f"Skipped {state[0] if len(state)>0 else 'UNKNOWN'}: {row_error}")
                    continue
            log_import_run(conn, recieved, saved, "SUCCESS")
            logging.info(f"ETL completed: {recieved} records received, {saved} records saved.")
        
        except Exception as e:
            logging.error(f"RADAR ETL failed: {e}")
            log_import_run(conn, 0, 0, "FAILED - R", str(e))

def run_flight_etl():
    logging.info("Starting FLIGHT ETL")
    with connect_db() as conn:
        try:
            end_ts = int(datetime.now(timezone.utc).timestamp()) - (24*3600)
            begin_ts = end_ts - 24 * 3600
            flights = fetch_all_flights(begin_ts, end_ts)
            if not flights:
                logging.warning("No flight found in given time range.")
                log_import_run(conn, 0, 0, "SUCCESS", "No Data")
                return
            
            received = len(flights)
            saved = 0

            for flight in flights:
                icao24 = flight.get("icao24")
                departure_airport_id = flight.get("estDepartureAirport")
                arrival_airport_id = flight.get("estArrivalAirport")
                departure_date_time = datetime.fromtimestamp(flight.get("firstSeen"), tz=timezone.utc).isoformat() if flight.get("firstSeen") else None
                arrival_date_time = datetime.fromtimestamp(flight.get("lastSeen"), tz=timezone.utc).isoformat() if flight.get("lastSeen") else None

                conn.execute(''' insert into aircraft (icao24) values (?) on conflict(icao24) do nothing''', (icao24,))
                
                for airport_id in [departure_airport_id, arrival_airport_id]:
                    if airport_id:
                        city, country = get_airport_info(airport_id)

                        conn.execute(''' insert into country (country_name) values (?) on conflict(country_name) do nothing''', (country,))
                        c_res = conn.execute('SELECT country_id FROM country WHERE country_name = ?', (country,))
                        row = c_res.fetchone()
                        a_country_id = row[0] if row else None

                        conn.execute(''' insert into airport (icao_code, city, country_id)
                        values (?, ?, ?)
                                     on conflict (icao_code) do update 
                                     set city = case when city = 'Unknown' then excluded.city else city end,
                                      country_id = excluded.country_id
                        ''', (airport_id, city, a_country_id))
               
                cur = conn.execute('''
                                    select 1 from flight_data 
                                    where aircraft_id = ? and departure_date_time = ?''', (icao24, departure_date_time))
                
                if not cur.fetchone():
                    conn.execute('''
                        insert into flight_data (aircraft_id, departure_airport_id, arrival_airport_id, departure_date_time, arrival_date_time)
                        values (?, ?, ?, ?, ?)''', 
                        (icao24, departure_airport_id, arrival_airport_id, departure_date_time, arrival_date_time))
                    
                    saved += 1
            log_import_run(conn, received, saved, "SUCCESS - FLIGHT")
            logging.info(f"FLIGHT ETL completed: {received} records received, {saved} records saved.")

        except Exception as e:
            logging.error(f"FLIGHT ETL failed: {e}")
            log_import_run(conn, 0, 0, "FAILED - F", str(e))

def run_etl():
    run_radar_etl()
    run_flight_etl()

if __name__ == "__main__":

    from database import create_tables
    create_tables()
    run_etl()