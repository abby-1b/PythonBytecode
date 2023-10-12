
# Map names to shorter versions! (unoptimized)
def reset_name_mappings():
	global name_mappings
	global name_map_id

NAME_MAP_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
name_map_id = [
	0, # variables
	0 # labels
]
name_mappings: dict[str, str] = {}

# Shorten variable/label names. Passing n=None generates a new name regardless,
# without tying it to a name, which is useful for generating label names. If an
# already shortened name is passed, it's original name mapping is returned.
def new_name(n: str | None = None, map_idx: int = 0):
	global name_mappings
	global name_map_id

	if n in name_mappings: return name_mappings[n]

	new_name = ""
	temp_name_map_id = name_map_id[map_idx]
	while True:
		new_name += NAME_MAP_CHARACTERS[temp_name_map_id % len(NAME_MAP_CHARACTERS)]
		temp_name_map_id //= len(NAME_MAP_CHARACTERS)
		if temp_name_map_id == 0: break
	name_map_id[map_idx] += 1
	if n != None: name_mappings[n] = new_name
	return new_name
