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



func load_path() -> void:
	print("Loading path...")
	var data: Array[FlightData]
	var csv := FileAccess.open(mock_data, FileAccess.READ)
	var header: PackedStringArray = csv.get_csv_line()
	var amp := header.find("geoamplitude")
	var lat := header.find("lat")
	var lon := header.find("lon")
	var vel := header.find("velocity")
	while !csv.eof_reached():
		var x := csv.get_csv_line()
		if len(x) == 1: break
		var d := FlightData.new(float(x[lon]), float(x[lat]), float(x[vel]),  float(x[amp]))
		data.append(d)
	path_loaded.emit({1:data} as Dictionary[int, Array])
	print("Path loading Successful!")

func load_plane(node: Node3D) -> void:
	print("Loading plane...")
	plane_loaded.emit(plane_data, node)
	print("Plane loading Successful!")

func load_airports() -> void:
	pass
