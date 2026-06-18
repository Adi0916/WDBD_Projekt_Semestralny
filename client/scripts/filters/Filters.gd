extends Control
class_name Filters
@export var min_max: Dictionary = {"min": 0, "max": 0}
@export var timestamp_start: int: 
	set(value): timestamp_start = clampi(value, min_max["min"], timestamp_end)
@export var timestamp_end: int: 
	set(value): timestamp_end = clampi(value, timestamp_start, min_max["max"])
@export var country: String
@export var airport_start: String
@export var airport_end: String
@export var aircraft: String
@export var limit: int = 100: 
	set(value): limit = clampi(value, 1, 200)

@export var fields: Array[LineEdit]

func _ready() -> void:
	var tmp :Dictionary = DataLoader.get_min_max_timestamp()
	print(tmp)
	min_max["min"] = Time.get_unix_time_from_datetime_string(tmp["min"])
	min_max["max"] = Time.get_unix_time_from_datetime_string(tmp["max"])
	print(min_max)
	timestamp_end = min_max["max"]
	timestamp_start = min_max["min"]
	
	set_last_check()

func filter(param: Variant.Type) -> void:
	timestamp_start = Time.get_unix_time_from_datetime_string(fields[0].text)
	timestamp_end = Time.get_unix_time_from_datetime_string(fields[1].text)
	airport_start = fields[2].text
	airport_end = fields[3].text
	aircraft = fields[4].text
	limit = int(fields[5].text)
	set_last_check()

func set_last_check() -> void:
	fields[0].text = Time.get_date_string_from_unix_time(timestamp_start)
	fields[1].text = Time.get_date_string_from_unix_time(timestamp_end)
	fields[5].text = str(limit)
