extends Control
class_name PlaneDataInfo
@export_category("AIRPORT")
@export var airport_name: LineEdit
@export var arrivals: LineEdit
@export var departures: LineEdit
@export var type: LineEdit
@export var country: LineEdit
var current_airport_data: AirportData

@export_category("AIRCRAFT")
@export var icao: LineEdit
@export var call_sign: LineEdit
@export var plane_country: LineEdit
@export var flight_start: LineEdit
@export var flight_end: LineEdit
var current_aircraft_data: PlaneData
@export_category("ROUTE POINT")

@export var longitude: LineEdit
@export var latitude: LineEdit
@export var amplitude: LineEdit
@export var velocity: LineEdit
var current_flight_data: FlightData

@export var filters: Filters


func read_airport_data(airport_data: AirportData) -> void:
	var data := DataLoader.get_airport_data(airport_data.icao)
	current_airport_data = airport_data
	airport_name.text = data["airport_name"]
	arrivals.text = "Ilość przylotów: " + str(data["arrival"])
	departures.text = "Ilość wylotów: " + str(data["depart"])
	type.text = data["type"]
	country.text = str(data["country"])

func read_aircraft_data(aircraft_data: PlaneStateData) -> void:
	current_aircraft_data = aircraft_data.plane_data
	var data := DataLoader.get_aircraft_time_data(aircraft_data.plane_data.icao24)
	icao.text = aircraft_data.plane_data.icao24
	plane_country.text = aircraft_data.plane_data.country
	call_sign.text = aircraft_data.plane_data.plane_name
	read_route_data(aircraft_data.flight_data)


func read_route_data(flight_data: FlightData) -> void:
	current_flight_data = flight_data
	longitude.text = "Longitude: "+str(flight_data.longnitude)
	latitude.text = "Latitude: "+str(flight_data.latitude)
	amplitude.text = "Amplitude: "+str(flight_data.amplitude)
	velocity.text = "Velocity: "+str(flight_data.velocity)

	pass
	
func set_airport_start() -> void:
	if not current_airport_data: return
	filters.airport_start = airport_name.text
	filters.fields[2].text = airport_name.text

func set_airport_end() -> void:
	if not current_airport_data: return
	filters.airport_end = airport_name.text
	filters.fields[3].text = airport_name.text


func set_aircraft() -> void:
	if not current_aircraft_data: return
	filters.aircraft = int(current_aircraft_data.plane_name)
