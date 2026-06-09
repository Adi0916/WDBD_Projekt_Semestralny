extends Node
class_name EarthMap

const plane: PackedScene = preload("res://scenes/3D scenes/Plane.tscn")
const point: PackedScene = preload("res://scenes/3D scenes/PathPoint.tscn")
const airport: PackedScene = preload("res://scenes/3D scenes/Airport.tscn")

@export var plane_node: Node3D
@export var path_node: Node3D
@export var airport_node: Node3D
@export var data_loader: LoadData

func _ready() -> void:
	data_loader.airports_loaded.connect(airport_data_handler)
	data_loader.path_loaded.connect(route_data_handler)
	data_loader.plane_loaded.connect(plane_data_handler)
	data_loader.load_path()

func add_route(route_id: int, route: Array[FlightData]) -> void:
	var root: Node3D = Node3D.new()
	root.name = str(route_id)
	for route_point in route:
		var tmp: RoutePoint = point.instantiate()
		tmp.flight_data = route_point
		tmp.set_pos(route_point.longnitude, route_point.latitude)
		root.add_child(tmp)
	data_loader.load_plane(root.get_child(root.get_child_count()/2))
	path_node.add_child(root, true)

func clear_routes(node: Node3D) -> void:
	while node.get_child_count() > 0:
		var tmp := node.get_child(0)
		node.remove_child(tmp)
		tmp.free()

func remove_route(route_id: int) -> void:
	for i in path_node.get_children_count():
		var temp: Node3D = path_node.get_child(i)
		if temp.name == str(route_id):
			path_node.remove_child(temp)
			return

func remove_plane(route_id: int) -> void:
	for i in plane_node.get_children_count():
		var temp: Node3D = plane_node.get_child(i)
		if temp.name == str(route_id):
			plane_node.remove_child(temp)
			return

func add_airport(airport_icao: String, airport_data: AirportData):
	var tmp: Airport = airport.instantiate()
	tmp.set_pos(airport_data.longnitude, airport_data.latitude)
	tmp.airport_data = airport_data
	tmp.name = airport_icao
	airport_node.add_child(tmp, true)


# Request Handlers
func airport_data_handler(airports: Array[AirportData]) -> void:
	for port in airports:
		add_airport(airport.icao, port)

func route_data_handler(route_data: Dictionary[int, Array]) -> void:
	print(route_data.keys())
	for key in route_data.keys():
		add_route(key, route_data[key])

func plane_data_handler(plane_data: PlaneData, route_point: RoutePoint) -> void:
	var tmp: PlaneVis = plane.instantiate()
	tmp.flight_data = route_point.flight_data
	tmp.plane_data = plane_data
	tmp.rotation = route_point.rotation
	tmp.name = route_point.get_parent().name
	route_point.queue_free()
	plane_node.add_child(tmp, true)
