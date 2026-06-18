extends Node
class_name LoadData

# Visualization Data Loaded
signal path_loaded(data: Dictionary[int, Array])
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

func load_flights() -> void:
	print("Loading path...")
	var data: Array[FlightData]
	var query:= """
	SELECT longitude lon, latitude lat, amplitude amp
	"""
	path_loaded.emit({1:data} as Dictionary[int, Array])
	print("Path loading Successful!")

func load_plane_by_icao(icao: String, node: Node3D) -> void:
	print("Loading plane...")
	var query:= """
	SELECT icao24, call_sign, c.country 
	FROM aircraft a
	INNER JOIN country c ON a.country_id = c.country_id
	WHERE icao24 = ?;
	"""
	var err := database.query_with_bindings(query, [icao])
	if err: return
	var first_plane :Dictionary= database.query_result[0]
	var pd: PlaneData = PlaneData.new()
	pd.icao24 = first_plane["icao24"]
	pd.plane_name = first_plane["call_sign"]
	pd.country = first_plane["country"]
	plane_loaded.emit(pd, node)
	print("Plane loading Successful!")

func load_plane_by_path(path_id: int, node: Node3D) -> void:
	print("Loading plane...")
	var query:= """
	SELECT icao24, call_sign, c.country 
	FROM aircraft a
	INNER JOIN country c ON a.country_id = c.country_id
	WHERE icao24 = ?;
	"""
	var err := database.query_with_bindings(query, [path_id])
	var pd: PlaneData = PlaneData.new()
	# Kod
	plane_loaded.emit(pd, node)
	print("Plane loading Successful!")

func load_airports() -> void:
	print("Load airports")
	var data: Array[AirportData] = []
	var err := database.query("SELECT DISTINCT latitude, longitude, airport_name, icao_code FROM airport WHERE airport_name != 'Unknown'")
	if !err: 
		print("Load unsuccessful")
		return
	for airport in database.query_result:
		var temp: AirportData = AirportData.new()
		temp.icao = airport["icao_code"]
		temp.latitude = airport["latitude"]
		temp.longnitude = airport["longitude"]
		data.append(temp)
	print("Load successful")
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
