import inspect
from hearthstone import enums


def pretty_list(items):
	if not len(items):
		return None
	if len(items) == 1:
		return "`%s`" % items[0]
	return ", ".join("`%s`" % s for s in items[:-1]) + (" or `%s`" % items[-1])


class EnumHandler():
	def __init__(self, config):
		self.max_response = int(config["max_enum"])


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
		term_count = len(parts) - 1
		numValues = [None] * term_count
		for i in range(0, term_count):
			try:
				numValues[i] = int(parts[i + 1].strip())
			except Exception:
				pass
		for enum in targetEnum:
			for i in range(0, term_count):
				term = parts[i + 1].strip().lower()
				if not len(term):
					continue
				enum_name = enum.name.lower()
				if (
					term == ("\"%s\"" % enum_name) or term in enum_name
				 	or numValues[i] and enum.value == numValues[i]
				):
					pair = (enum.name, enum.value)
					if pair not in ret:
						ret.append(pair)
		if len(ret) == 0:
			return "Tag not found"
		if len(ret) > self.max_response:
			return "More than %s matches, please be more specific" % self.max_response
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
