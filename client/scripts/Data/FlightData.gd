extends Resource
class_name FlightData

@export var longnitude: float # deg
@export var latitude: float # deg
@export var amplitude: float # m
@export var velocity: float # m/s

func _init(long: float, lat: float, vel, amp) -> void:
	self.longnitude = long
	self.latitude = lat
	if amp is float:
		self.amplitude = amp
	else: 
		self.amplitude = 0
	if vel is float:
		self.velocity = vel
	else:
		self.velocity = 0
