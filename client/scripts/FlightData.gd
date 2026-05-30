extends StaticBody3D
class_name FlightData

@export var flight_data: Data
func retrive_data() -> Data:
	print(flight_data.latitude, "|", flight_data.langnitude)
	return flight_data

func set_data(new_data: Data) -> void:
	flight_data = new_data
