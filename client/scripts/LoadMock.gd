extends Node
class_name LoadData
@export var mock_data: String
@export var data: Array[Data]

func load_data() -> void:
	data.clear()
	print(mock_data)
	var csv := FileAccess.open(mock_data, FileAccess.READ)
	var header: PackedStringArray = csv.get_csv_line()
	var amp := header.find("geoamplitude")
	var lat := header.find("lat")
	var lon := header.find("lon")
	var pname := header.find("callsign")
	var vel := header.find("velocity")
	while !csv.eof_reached():
		var x := csv.get_csv_line()
		if len(x) == 1: return
		var d := Data.new()
		d.amplitude = float(x[amp])
		d.latitude = float(x[lat])
		d.langnitude = float(x[lon])
		d.plane_name = x[pname]
		d.velocity = float(x[vel])
		data.append(d)
