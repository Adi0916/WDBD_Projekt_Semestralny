extends Node
class_name LoadData

# Visualization Data Loaded
signal path_loaded(data: Dictionary[String, Array])
signal plane_loaded(data: PlaneData, node: RoutePoint)
signal airports_loaded(data: Array[AirportData])

@export var mock_data: String
var plane_data: PlaneData = PlaneData.new()

var database: SQLite
func _ready() -> void:
	database = SQLite.new()
	database.path = "res://opensky_data.db"
	database.open_db()

func _exit_tree() -> void:
	database.close_db()

func load_flights(filters: Filters) -> void:
	var data: Dictionary[String, Array]
	var query:= """
	SELECT longitude lon, latitude lat, geo_altitude amp, velocity vel, l.aircraft_id id
	FROM location l
	WHERE l.aircraft_id IN
		(SELECT DISTINCT l.aircraft_id
		FROM location l
		WHERE time_pos BETWEEN ? AND ?
		ORDER BY l.aircraft_id, l.time_pos
		LIMIT ?)
	"""
	var params: Array = filters.get_filter_params()
	params.append(filters.limit)
	database.query_with_bindings(query, params)
	for row in database.query_result:
		if row["id"] not in data.keys():
			data[row["id"]] = []
		data[row["id"]].append(FlightData.new(row["lon"], row["lat"],row["vel"], row["amp"]))
	path_loaded.emit(data)

func load_plane_by_icao(icao: String, node: Node3D) -> void:
	var query:= """
	SELECT icao24, callsign, c.country_name country
	FROM aircraft a
	INNER JOIN country c ON a.country_id = c.country_id
	WHERE icao24 = ?;
	"""
	var err := database.query_with_bindings(query, [icao])
	if not err: return
	var first_plane:Dictionary= database.query_result[0]
	var pd: PlaneData = PlaneData.new()
	pd.icao24 = first_plane["icao24"]
	pd.plane_name = first_plane["callsign"]
	pd.country = first_plane["country"]
	plane_loaded.emit(pd, node)

func load_airports() -> void:
	var data: Array[AirportData] = []
	var err := database.query("SELECT DISTINCT latitude, longitude, airport_name, icao_code FROM airport WHERE airport_name != 'Unknown'")
	if !err: 
		return
	for airport in database.query_result:
		var temp: AirportData = AirportData.new()
		temp.icao = airport["icao_code"]
		temp.latitude = airport["latitude"]
		temp.longnitude = airport["longitude"]
		data.append(temp)
	airports_loaded.emit(data)

func get_airport_data(icao: String) -> Dictionary:
	var query := """
	SELECT 
		airport_name, 
		COUNT(DISTINCT f1.flight_id) depart, 
		COUNT(DISTINCT f2.flight_id) arrival,
		c.country_name country,
		type
		FROM airport a
		LEFT JOIN flight_data f1 ON f1.departure_airport_id = a.icao_code
		LEFT JOIN flight_data f2 ON f2.arrival_airport_id = a.icao_code
		INNER JOIN country c ON c.country_id = a.country_id
		WHERE icao_code = ?
	"""
	database.query_with_bindings(query, [icao])
	return database.query_result[0]

func get_aircraft_time_data(icao: String) -> Dictionary:
	return {}

func get_min_max_timestamp() -> Dictionary:
	var query := """
	SELECT MIN(time_pos) as min, MAX(time_pos) as max FROM location
	"""
	database.query(query)
	return database.query_result[0]
