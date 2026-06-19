import logging
from api_client import fetch_states, fetch_all_flights
from datetime import datetime, timezone
from database import connect_db
from airports import airport_data
import pycountry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BBOX_EUROPE = (35.0, 70.0, -10.0, 40.0)

def log_import_run(conn, received, saved, status, error_msg=None):
    conn.execute(
        '''INSERT INTO import_log (imported_at, records_received, records_saved, status, error_message)
           VALUES (?, ?, ?, ?, ?)''',
        (datetime.now(timezone.utc).isoformat(), received, saved, status, error_msg)
    )
    conn.commit()

def get_full_continent_name(continent_code):

    code_map = {
        "AF": "Africa",
        "AN": "Antarctica",
        "AS": "Asia",
        "EU": "Europe",
        "NA": "North America",
        "OC": "Oceania",
        "SA": "South America"
    }
    return code_map.get(continent_code, continent_code)


def get_airport_info(conn, icao_code):

    if not icao_code or icao_code.strip() == "":
        return

    continent_code = "Unknown"
    country_code = "Unknown"
    airport_name = "Unknown"
    lat = None
    lon = None
    apt_type = "Unknown"

    try:
        apt_list = airport_data.get_airport_by_icao(icao_code)

        if apt_list:
            apt_info = apt_list[0]
            continent_code = apt_info.get("continent", "Unknown")
            country_code = apt_info.get("country_code", "Unknown")
            airport_name = apt_info.get("airport", "Unknown")
            lat = apt_info.get("latitude", None)
            lon = apt_info.get("longitude", None)
            apt_type = apt_info.get("type", "Unknown")

    except Exception as e:
        logging.warning(f"Failed to get airport info for {icao_code}: {e}")

    country_name = "Unknown"
    if country_code and country_code != "Unknown":
        country_obj = pycountry.countries.get(alpha_2=country_code)
        if country_obj:
            country_name = country_obj.name

    continent_name = get_full_continent_name(continent_code)

    conn.execute(''' insert into continent (continent_name) values (?)
                    on conflict(continent_name) do nothing''', (continent_name,))

    res = conn.execute('SELECT continent_id FROM continent WHERE continent_name = ?', (continent_name,))
    continent_id = res.fetchone()[0]

    conn.execute (''' insert into country (country_name, continent_id) values (?, ?)
                    on conflict(country_name) do update set
                    continent_id = excluded.continent_id where continent_id is NULL''', (country_name, continent_id))
    res = conn.execute('SELECT country_id FROM country WHERE country_name = ?', (country_name,))
    country_id = res.fetchone()[0]

    conn.execute(''' insert into airport (icao_code, airport_name, country_id, latitude, longitude, type)
                    values (?, ?, ?, ?, ?, ?)
                    on conflict(icao_code) do update set
                    airport_name = CASE WHEN airport_name = 'Unknown' THEN excluded.airport_name ELSE airport_name END,
                    country_id = excluded.country_id,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    type = excluded.type
                    ''', (icao_code, airport_name, country_id, lat, lon, apt_type))

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


                    conn.execute('''
                        INSERT INTO country (country_name)
                        VALUES (?)
                        ON CONFLICT(country_name) DO NOTHING;
                    ''', (origin_country,))
                    c_res = conn.execute('SELECT country_id FROM country WHERE country_name = ?', (origin_country,))
                    country_id = c_res.fetchone()[0]

                    conn.execute('''
                            INSERT INTO aircraft (icao24, callsign, country_id, last_updated)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(icao24) DO UPDATE SET
                        callsign = excluded.callsign,
                        country_id = excluded.country_id,
                        last_updated = excluded.last_updated;
                    ''', (icao24, callsign, country_id, datetime.now(timezone.utc).isoformat()))

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
            log_import_run(conn, recieved, saved, "SUCCESS - RADAR")
            logging.info(f"ETL completed: {recieved} records received, {saved} records saved.")

        except Exception as e:
            logging.error(f"RADAR ETL failed: {e}")
            log_import_run(conn, 0, 0, "FAILED - R", str(e))

def run_flight_etl():
    logging.info("Starting FLIGHT ETL")
    with connect_db() as conn:
        try:
            end_ts = int(datetime.now(timezone.utc).timestamp()) - (2*3600)
            begin_ts = end_ts - (4 * 3600)
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

                if not departure_airport_id or departure_airport_id.strip() == "":
                    departure_airport_id = None
                if not arrival_airport_id or arrival_airport_id.strip() == "":
                    arrival_airport_id = None

                conn.execute(''' insert into aircraft (icao24) values (?) on conflict(icao24) do nothing''', (icao24,))

                if departure_airport_id:
                    get_airport_info(conn, departure_airport_id)
                if arrival_airport_id:
                    get_airport_info(conn, arrival_airport_id)

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

def link_location_to_flight():

    logging.info("Linking locations to flights...")
    with connect_db() as conn:
        try:

            cur = conn.execute('''
                UPDATE location
                SET flight_id = (
                    SELECT flight_id
                    FROM flight_data f
                    WHERE f.aircraft_id = location.aircraft_id
                      AND location.time_pos >= f.departure_date_time
                      AND location.time_pos <= f.arrival_date_time
                    LIMIT 1
                )
                WHERE flight_id IS NULL AND time_pos IS NOT NULL
            ''')
            conn.commit()
            logging.info(f"Updated {cur.rowcount} locations with specific flight_ids.")
        except Exception as e:
            logging.error(f"Error linking locations to flights: {e}")

def run_etl():
    run_radar_etl()
    run_flight_etl()

if __name__ == "__main__":

    from database import create_tables
    create_tables()
    run_etl()
    link_location_to_flight()