import sys, inspect
from hearthstone import enums

class EnumHandler():
	def handle(self, input):
		targetEnum = None
		parts = input.split(" ")

		if len(parts) != 2:
			return "Invalid search term. Use '!enum [ENUM_NAME] [NAME/VALUE]'"
		
		for enum_class in inspect.getmembers(enums, inspect.isclass):
			if enum_class[0] == parts[0]:
				targetEnum = enum_class[1]
				break
		if targetEnum is None:
			return "Invalid enum name"

		ret = []
		numValue = None
		try:
			numValue = int(parts[1])
		except Exception as e:
			pass
		for enum in targetEnum:
			if numValue and enum.value == numValue or parts[1].lower() in enum.name.lower():
				ret.append((enum.name, enum.value))
		if len(ret) == 0:
			return "Tag not found"
		if len(ret) > 25:
			return "More than 25 matches, please be more specific"
		return ", ".join("`%s = %s`" % (name, value) for (name, value) in ret)
		
