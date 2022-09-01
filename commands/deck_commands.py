from enum import IntEnum

import discord
from discord import AllowedMentions, app_commands
from hearthstone import cardxml
from hearthstone.cardxml import CardXML
from hearthstone.deckstrings import Deck
from hearthstone.enums import FormatType, GameTag, Locale

ValidLocales = IntEnum("Locale", [(i.name, i.value) for i in Locale if i.value >= 0])

db, _ = cardxml.load_dbf()


def loc_name(self, locale):
	return self.strings[GameTag.CARDNAME][locale]


def loc_text(self, locale):
	return self.strings[GameTag.CARDTEXT_INHAND][locale]


def loc_flavor(self, locale):
	return self.strings[GameTag.FLAVORTEXT][locale]


CardXML.loc_name = loc_name
CardXML.loc_text = loc_text
CardXML.loc_flavor = loc_flavor


class DeckCommands:
	def __init__(self):
		self.db = db

	def install(self, client):
		@client.tree.command(
			name="deck",
			description="Decode a Hearthstone deck",
		)
		async def card_by_card_id(interaction: discord.Interaction, deckstring: str):
			deck = None
			try:
				deck = Deck.from_deckstring(deckstring)
			except Exception as e:
				await interaction.response.send_message(
					f"Sorry, that doesn't look like a valid deck! (Error was \"{str(e)}\")",
					ephemeral=True,
				)
				return

			hero = ",".join([self.find_card_name(card_id) for card_id in deck.heroes])

			output = "```"
			output += f"\n###"
			output += f"\n# Hero: {hero}"
			output += f"\n# Format: {list(FormatType)[(deck.format)].name}"
			output += f"\n#"
			for card in deck.cards:
				count = card[1]
				card_id = card[0]
				if card_id in self.db:
					card = self.db[card_id]
					output += f"\n# {count}x ({card.cost}) {card.name}"
				else:
					output += f"\n# {count}x UNKNONWN"
			output += f"\n#"
			output += f"\n{deck.as_deckstring}"
			output += f"\n#"
			output += f"\n# To use this deck, copy it to your clipboard and create a new deck in Hearthstone"
			output += "```"

			await interaction.response.send_message(
				output,
				allowed_mentions=AllowedMentions.none(),
			)

	def find_card_name(self, card_id):
		if card_id in self.db:
			card = self.db[card_id]
			return card.name
		else:
			return "UNKNOWN"
