import logging
from database import connect_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#1: Najnowsze pozycje samolotów

def get_live_radar_data(country_name=None, continent_name=None, on_ground=None, category=None):

    query = '''
        SELECT 
            a.icao24,
            a.callsign,
            c.country_name,
            ct.continent_name,
            a.aircraft_category,
            l.latitude,
            l.longitude,
            l.baro_altitude,
            l.velocity,
            l.on_ground,
            l.time_pos
        FROM aircraft a
        JOIN location l ON a.icao24 = l.aircraft_id
        LEFT JOIN country c ON a.country_id = c.country_id
        LEFT JOIN continent ct ON c.continent_id = ct.continent_id
        INNER JOIN (
            -- Podzapytanie wyciągające tylko najświeższy timestamp dla każdego samolotu
            SELECT aircraft_id, MAX(time_pos) as max_time
            FROM location
            GROUP BY aircraft_id
        ) latest ON l.aircraft_id = latest.aircraft_id AND l.time_pos = latest.max_time
        WHERE l.latitude IS NOT NULL AND l.longitude IS NOT NULL
    '''
    params = []

    if country_name:
        query += " AND c.country_name = ?"
        params.append(country_name)
    if continent_name:
        query += " AND ct.continent_name = ?"
        params.append(continent_name)
    if on_ground is not None:
        query += " AND l.on_ground = ?"
        params.append(1 if on_ground else 0)
    if category is not None:
        query += " AND a.aircraft_category = ?"
        params.append(category)

    with connect_db() as conn:
        cursor = conn.execute(query, params)
        return cursor.fetchall()


#2: Statystyki ruchu na lotniskach

def get_airport_traffic_stats(airport_code=None, date_from=None, date_to=None):

    query = '''
        SELECT 
            id_lotniska,
            COUNT(DISTINCT wylot_id) as liczba_wylotów,
            COUNT(DISTINCT przylot_id) as liczba_przylotów,
            (COUNT(DISTINCT wylot_id) + COUNT(DISTINCT przylot_id)) as całkowity_ruch
        FROM (
            SELECT departure_airport_id as id_lotniska, flight_id as wylot_id, NULL as przylot_id, departure_date_time as dt FROM flight_data
            UNION ALL
            SELECT arrival_airport_id as id_lotniska, NULL as wylot_id, flight_id as przylot_id, arrival_date_time as dt FROM flight_data
        )
        WHERE id_lotniska IS NOT NULL
    '''
    params = []

    if airport_code:
        query += " AND id_lotniska = ?"
        params.append(airport_code)
    if date_from:
        query += " AND dt >= ?"
        params.append(date_from)
    if date_to:
        query += " AND dt <= ?"
        params.append(date_to)

    query += " GROUP BY id_lotniska ORDER BY całkowity_ruch DESC"

    with connect_db() as conn:
        cursor = conn.execute(query, params)
        return cursor.fetchall()


#3: Historia trasy konkretnego samolotu

def get_aircraft_trajectory(icao24, time_from=None):

    query = '''
        SELECT latitude, longitude, baro_altitude, velocity, time_pos
        FROM location
        WHERE aircraft_id = ?
    '''
    params = [icao24]

    if time_from:
        query += " AND time_pos >= ?"
        params.append(time_from)

    query += " ORDER BY time_pos ASC"

    with connect_db() as conn:
        cursor = conn.execute(query, params)
        return cursor.fetchall()


#4: Udział procentowy kontynentów lub kategorii w globalnym ruchu

def get_continent_distribution_stats():
 
    query = '''
        SELECT 
            COALESCE(ct.continent_name, 'Unknown') as continent,
            COUNT(a.icao24) as aircraft_count
        FROM aircraft a
        LEFT JOIN country c ON a.country_id = c.country_id
        LEFT JOIN continent ct ON c.continent_id = ct.continent_id
        GROUP BY continent
        ORDER BY aircraft_count DESC
    '''
    with connect_db() as conn:
        cursor = conn.execute(query)
        return cursor.fetchall()



#5: Raport techniczny

def get_system_health_report(status_filter=None):

    query = '''
        SELECT log_id, imported_at, records_received, records_saved, status, error_message
        FROM import_log
        WHERE 1=1
    '''
    params = []

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY log_id DESC LIMIT 50"

    with connect_db() as conn:
        cursor = conn.execute(query, params)
        return cursor.fetchall()