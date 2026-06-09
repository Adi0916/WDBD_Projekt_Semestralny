extends StaticBody3D
class_name Visualization3D

func set_pos(longnitude: float, latitude: float):
	rotation_degrees.x = -latitude
	rotation_degrees.y = longnitude
