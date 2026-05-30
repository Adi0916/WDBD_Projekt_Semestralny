extends Node3D
@export var init_pos: Vector2
@export var anmiate: AnimationPlayer
@export var mock: LoadData
@export var flight_data: FlightData
@export var path_nodes: Array[Node3D]
@export var current_time_stamp: int
@export var route_points: Array[Data]
var path_point: PackedScene = preload("res://scenes/3D scenes/PathPoint.tscn")

func _ready() -> void:
	anmiate.play("Blinking")
	set_new_route()
	
func set_new_route(num: int = 0) -> void:
	for child in path_nodes:
		get_parent().remove_child(child)
		child.queue_free()
	mock.load_data() # Do zmiany
	route_points = mock.data
	flight_data.set_data(mock.data[num])
	set_plane_pos(mock.data[num].latitude, mock.data[num].langnitude)
	current_time_stamp = num
	for data in mock.data:
		var temp_path:Node3D = path_point.instantiate()
		temp_path.rotation_degrees.x = -data.latitude
		temp_path.rotation_degrees.y = data.langnitude
		get_parent().add_child.call_deferred(temp_path)
		path_nodes.append(temp_path)

func change_plane_pos(diff: int = 0) -> void:
	current_time_stamp = max(min(current_time_stamp + diff, len(route_points)-1), 0)
	var point := route_points[current_time_stamp]
	set_plane_pos(point.latitude, point.langnitude)

func set_plane_pos(latitude: float, longnitude:float) -> void:
	rotation_degrees.x = -latitude
	rotation_degrees.y = longnitude

func _process(delta: float) -> void:
	if Input.is_action_just_pressed("ScrollUp"):
		change_plane_pos(1)
	if Input.is_action_just_pressed("ScrollDown"):
		change_plane_pos(-1)
