extends Camera3D
class_name CameraControl

@export var rotator: Node3D
var camera_movement: bool = false
var planet_pos: Vector2 = Vector2.ZERO

func _input(event: InputEvent) -> void:
	if event is InputEventMouse:
		
		if event.is_action_pressed("Click"):
			camera_movement = true
		if event.is_action_released("Click"):
			camera_movement = false
			
		if event.is_action_pressed("Select"):
			var from: Vector3 = project_ray_origin(event.position)
			var to: Vector3 = from + project_ray_normal(event.position)*20
			var raycast := PhysicsRayQueryParameters3D.new()
			raycast.from = from
			raycast.to = to
			var ray_res := get_world_3d().direct_space_state.intersect_ray(raycast)
			if not ray_res.is_empty():
				if ray_res["collider"] is PlaneVis:
					var data: PlaneStateData = ray_res["collider"].return_data()
					planet_pos.x = data.flight_data.latitude - 13 # Poprawka przez perspektywe
					planet_pos.y = -data.flight_data.longnitude + 2.0 # Poprawka przez perspektywe

	if event is InputEventMouseMotion and camera_movement:
		var velocity: Vector2 = event.velocity
		planet_pos.x = rotator.rotation_degrees.x + deg_to_rad(velocity.y)
		planet_pos.y = rotator.rotation_degrees.y + deg_to_rad(velocity.x)

func _physics_process(delta: float) -> void:
		rotator.rotation_degrees.x = lerp(rotator.rotation_degrees.x, planet_pos.x, delta * 3)
		rotator.rotation_degrees.y = lerp(rotator.rotation_degrees.y, planet_pos.y, delta * 3)
