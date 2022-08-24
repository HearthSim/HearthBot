import inspect
import re
from typing import List, Optional

import discord
from discord import app_commands
from hearthstone import enums


class CommandError(Exception):
	pass


def pretty_list(items):
	if not items:
		return ""

	if len(items) == 1:
		return "`%s`" % items[0]

	return ", ".join("`%s`" % s for s in items[:-1]) + (" or `%s`" % items[-1])


class EnumCommands:
	def __init__(self, max_responses_public: int, max_responses_private: int):
		self.max_responses_public = max_responses_public
		self.max_responses_private = max_responses_private

	def install(self, client):
		@client.tree.command(
			name="enum",
			description="Show details about a Hearthstone enum",
		)
		@app_commands.describe(
			enum="The enum to retrieve",
			member="The member of the enum to retrieve (name or number)"
		)
		async def enum(
			interaction: discord.Interaction,
			enum: str,
			member: Optional[str] = None
		):
			max_responses = (
				self.max_responses_private if interaction.guild_id is None
				else self.max_responses_public
			)

			try:
				response = self.handle_enum(enum, member, max_responses)
				await interaction.response.send_message(response)
			except CommandError as err:
				await interaction.response.send_message(
					str(err),
					ephemeral=True,
				)
			except Exception as err:
				await interaction.response.send_message(
					"Sorry, something went wrong!",
					ephemeral=True,
				)

		@enum.autocomplete("enum")
		async def autocomplete_enum_name(
			interaction: discord.Interaction,
			enum: str
		) -> List[app_commands.Choice[str]]:
			enum_classes = inspect.getmembers(enums, inspect.isclass)
			enum_names = [enum_class[0] for enum_class in enum_classes]
			if enum:
				return [
					app_commands.Choice(name=enum_name, value=enum_name)
					for enum_name in self.get_suggestions(enum, enum_names)
				]
			else:
				return [
					app_commands.Choice(name=enum_name, value=enum_name)
					for enum_name in enum_names
				][:25]

		@enum.autocomplete("member")
		async def autocomplete_enum_member(
			interaction: discord.Interaction,
			member: str,
		) -> List[app_commands.Choice[str]]:
			if "enum" not in interaction.namespace:
				return []
			enum_name = interaction.namespace["enum"]
			return self.get_enum_member_autocompletions(enum_name, member)

		@client.tree.command(
			name="tag",
			description="Retrieve information about a specific Hearthstone GameTag",
		)
		@app_commands.describe(
			game_tag="The GameTag to retrieve (name or number)"
		)
		async def tag(
			interaction: discord.Interaction,
			game_tag: str,
		):
			max_responses = (
				self.max_responses_private if interaction.guild_id is None
				else self.max_responses_public
			)

			try:
				response = self.handle_enum("GameTag", game_tag, max_responses)
				await interaction.response.send_message(response)
			except CommandError as err:
				await interaction.response.send_message(
					str(err),
					ephemeral=True,
				)
			except Exception as err:
				await interaction.response.send_message(
					"Sorry, something went wrong!",
					ephemeral=True,
				)

		@tag.autocomplete("game_tag")
		async def autocomplete_game_tag(
			interaction: discord.Interaction,
			game_tag: str,
		) -> List[app_commands.Choice[str]]:
			return self.get_enum_member_autocompletions("GameTag", game_tag)

	def handle_enum(self, enum: str, members: Optional[str], max_responses: int):
		target_name = enum.lower()

		target_enum = None
		enum_classes = inspect.getmembers(enums, inspect.isclass)
		for enum_class in enum_classes:
			if enum_class[0].lower() == target_name or enum_class[
				1].__doc__.lower() == target_name:
				target_enum = enum_class[1]
				break
		if target_enum is None:
			return self.find_enum(enum_classes, target_name)

		terms = members.split(",") if members else []
		if terms:
			match = re.match(r"^(\d*)-(\d*)$", terms[0])
			if len(terms) == 1 and match:
				lower = match.group(1) and int(match.group(1)) or 0
				upper = match.group(2) and int(
					match.group(2)) or lower + max_responses
				terms = [str(x) for x in range(lower, upper + 1)]
		else:
			terms = [str(x) for x in range(0, max_responses + 1)]

		term_count = len(terms)
		num_values = [None] * term_count

		for i in range(term_count):
			try:
				num_values[i] = int(terms[i].strip())
			except Exception:
				pass

		ret = []
		exact_ret = []
		for enum in target_enum:
			for i in range(0, term_count):
				term = terms[i].strip().lower()
				if not len(term):
					continue
				target_name = enum.name.lower()
				if term.lower() == target_name.lower():
					pair = (enum.name, enum.value)
					if pair not in exact_ret:
						exact_ret.append(pair)
				if (
					term == ("\"%s\"" % target_name) or term in target_name or
					num_values[i] and enum.value == num_values[i]
				):
					pair = (enum.name, enum.value)
					if pair not in ret:
						ret.append(pair)

		if exact_ret:
			ret = exact_ret

		if not ret:
			raise CommandError("Tag not found")

		if len(ret) > max_responses:
			raise CommandError(f"More than {max_responses} matches, please be more specific")

		if len(ret) < 10:
			header = "```python"
			the_class = f"class {target_enum.__name__}(IntEnum):"
			members = "\n".join([f"\t{name} = {value}" for name, value in ret])
			if len(ret) < len(target_enum):
				members += "\n\t# ..."
			footer = "```"
			return "\n".join([header, the_class, members, footer])

		return ", ".join("`%s = %s`" % (name, value) for (name, value) in ret)

	def find_enum(self, enum_classes, target_name):
		suggestions = []
		for enum_class in enum_classes:
			class_name = enum_class[0].lower()
			if class_name in target_name or target_name in class_name:
				suggestions.append(enum_class[0])
		response = "Unknown enum."
		if suggestions:
			response += " Try " + pretty_list(suggestions)

		return response

	def get_enum_member_autocompletions(self, enum_name: str, member: str):
		target_enum = None
		enum_classes = inspect.getmembers(enums, inspect.isclass)
		for enum_class in enum_classes:
			if enum_class[0].lower() == enum_name.lower():
				target_enum = enum_class[1]

		if not target_enum:
			return []

		member_names = [member.name for member in target_enum]
		return [
			app_commands.Choice(name=name, value=name)
			for name in self.get_suggestions(member, member_names)
		]

	def get_suggestions(
		self,
		typeahead: str,
		options: List[str],
	):
		if not typeahead:
			return options[:25]

		by_exact = [
			member_name for member_name in options
			if member_name.lower() == typeahead.lower()
		]
		by_startswith = sorted(
			[
				member_name for member_name in options
				if member_name.lower().startswith(typeahead.lower())
				and member_name not in by_exact
			],
			key=lambda x: len(x)
		)
		by_substr = [
			member_name for member_name in options
			if typeahead.lower() in member_name.lower()
			and member_name not in by_exact
			and member_name not in by_startswith
		]

		return (by_exact + by_startswith + by_substr)[:25]
