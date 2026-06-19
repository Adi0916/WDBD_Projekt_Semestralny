extends Visualization3D
class_name PlaneVis

@export var anmiate: AnimationPlayer
var plane_data: PlaneData
var flight_data: FlightData

func _ready() -> void:
	pass
func return_data() -> PlaneStateData:
	return PlaneStateData.new(flight_data, plane_data)

func update_pos(new_data: FlightData, destroy: bool) -> void:
	if destroy: self.queue_free()
	flight_data = new_data
	set_pos(new_data.longnitude, new_data.latitude)
	
