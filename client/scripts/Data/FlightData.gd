extends Resource
class_name FlightData

@export var longnitude: float # deg
@export var latitude: float # deg
@export var amplitude: float # m
@export var velocity: float # m/s

func _init(long: float, lat: float, vel: float, amp: float) -> void:
	self.longnitude = long
	self.latitude = lat
	self.amplitude = amp
	self.velocity = vel
