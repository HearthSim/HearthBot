import inspect
import re

from hearthstone import enums


def pretty_list(items):
	if not items:
		return ""

	if len(items) == 1:
		return "`%s`" % items[0]

	return ", ".join("`%s`" % s for s in items[:-1]) + (" or `%s`" % items[-1])


class EnumHandler:
	def __init__(self, config):
		self.max_response = int(config["max_enum"])

	def handle(self, input):
		target_enum = None
		parts = input.split()
		target_name = parts[0].lower()

		if len(parts) < 2:
			return "Invalid number of arguments. Use '!enum [ENUM_NAME] [NAME|VALUE]'"

		enum_classes = inspect.getmembers(enums, inspect.isclass)
		for enum_class in enum_classes:
			if enum_class[0].lower() == target_name or enum_class[1].__doc__.lower() == target_name:
				target_enum = enum_class[1]
				break
		if target_enum is None:
			return self.find_enum(enum_classes, target_name)

		ret = []
		terms = parts[1:]
		match = re.match(r"^(\d*)-(\d*)$", terms[0])
		if len(terms) == 1 and match:
			lower = match.group(1) and int(match.group(1)) or 0
			upper = match.group(2) and int(match.group(2)) or lower + self.max_response
			terms = [str(x) for x in range(lower, upper + 1)]

		term_count = len(terms)
		num_values = [None] * term_count

		for i in range(term_count):
			try:
				num_values[i] = int(terms[i].strip())
			except Exception:
				pass

		for enum in target_enum:
			for i in range(0, term_count):
				term = terms[i].strip().lower()
				if not len(term):
					continue
				enum_name = enum.name.lower()
				if (
					term == ("\"%s\"" % enum_name) or term in enum_name or
					num_values[i] and enum.value == num_values[i]
				):
					pair = (enum.name, enum.value)
					if pair not in ret:
						ret.append(pair)

		if not ret:
			return "Tag not found"

		if len(ret) > self.max_response:
			return f"More than {self.max_response} matches, please be more specific"

		return ", ".join("`%s = %s`" % (name, value) for (name, value) in ret)

	def find_enum(self, enum_classes, target_name):
		suggestions = []
		for enum_class in enum_classes:
			class_name = enum_class[0].lower()
			if class_name in target_name or target_name in class_name:
				suggestions.append(enum_class[0])
		response = "Invalid enum name."
		if suggestions:
			response += " Try " + pretty_list(suggestions)

		return response
