import inspect
from hearthstone import enums


def pretty_list(items):
	if not len(items):
		return None
	if len(items) == 1:
		return "`%s`" % items[0]
	return ", ".join("`%s`" % s for s in items[:-1]) + (" or `%s`" % items[-1])


class EnumHandler():
	def handle(self, input):
		targetEnum = None
		parts = input.split(" ")
		target_name = parts[0].lower()

		if len(parts) < 2:
			return "Invalid number of arguments. Use '!enum [ENUM_NAME] [NAME|VALUE]'"

		enum_classes = inspect.getmembers(enums, inspect.isclass)
		for enum_class in enum_classes:
			if enum_class[0].lower() == target_name or enum_class[1].__doc__.lower() == target_name:
				targetEnum = enum_class[1]
				break
		if targetEnum is None:
			return self.find_enum(enum_classes, target_name)

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


	def find_enum(self, enum_classes, target_name):
		suggestions = []
		for enum_class in enum_classes:
			class_name = enum_class[0].lower()
			if class_name in target_name or target_name in class_name:
				suggestions.append(enum_class[0])
		response = "Invalid enum name."
		if len(suggestions):
			response = response + " Try " + pretty_list(suggestions) if len(suggestions) else ""
		return response
