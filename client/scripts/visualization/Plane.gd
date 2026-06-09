extends Visualization3D
class_name PlaneVis

@export var anmiate: AnimationPlayer
var plane_data: PlaneData
var flight_data: FlightData

func _ready() -> void:
	anmiate.play("Blinking")

func return_data() -> PlaneStateData:
	return PlaneStateData.new(flight_data, plane_data)
