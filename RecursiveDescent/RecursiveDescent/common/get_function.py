def getFunction(name, map):
	if name in map:
		return map[name]
	else:
		raise RuntimeError("Unexpected name of function")
