from hearthstone.deckstrings import Deck
from hearthstone import cardxml
from hearthstone.cardxml import CardXML
from hearthstone.enums import CardType, FormatType, GameTag, Race, Rarity


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


class DeckHandler():
	def __init__(self):
		self.db = db

	def handle(self, input):
		return self.format_deckstring(input)

	def format_deckstring(self, deckstring):
		
		deck = None
		try:
			deck = Deck.from_deckstring(deckstring)
		except Exception as e:
			return str(e)

		hero = ",".join([self.find_card_name(card_id) for card_id in deck.heroes])

		output = ""
		output += f"\n###"
		output += f"\n# Class: {hero}"
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
		output += f"\n# {deck.as_deckstring}"
		output += f"\n#"
		output += f"\n# To use this deck, copy it to your clipboard and create a new deck in Hearthstone"

		return output
	
	def find_card_name(self, card_id):
		if card_id in self.db:
			card = self.db[card_id]
			return card.name
		else:
			return "UNKNOWN"
