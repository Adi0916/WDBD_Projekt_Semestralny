extends Resource
class_name PlaneStateData

var flight_data: FlightData
var plane_data: PlaneData

func _init(fd: FlightData, pd: PlaneData) -> void:
	flight_data = fd
	plane_data = pd
