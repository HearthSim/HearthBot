import re
from hearthstone.enums import CardType, Race, Rarity
from hearthstone import cardxml

db, _ = cardxml.load()


class CardHandler():	
	def handle(self, input, max_response):
		print("input:", input)
		try:
			card = db[input];
			if card is not None:
				return self.stringify_card(card)
		except Exception as e:
			print(e)
			pass
		
		try:	
			index = -1
			match = re.match("^(.+?)(\d+)$", input)
			if match is not None:
				input = match.group(1).strip()
				index = int(match.group(2))
			
			cards = []
			for card in db.values():
				if input.lower() in card.name.lower():
					cards.append(card)
			num_cards = len(cards)

			if num_cards == 0:
				return "Card not found"
			if num_cards == 1:
				return self.stringify_card(cards[0], 0, 0)				
			if index >= 0:
				return self.stringify_card(cards[index-1], index, num_cards)
			
			return "\n".join(
				self.stringify_card(cards[i], i + 1, num_cards) 
				for i in range(0, min(max_response, num_cards))
			)
		except Exception as e:
			print(e)
			pass
		return "Card not found"

	def stringify_card(self, card, index = 0, total = 0):
		health = card.durability if card.type == CardType.WEAPON else card.health
		search_index = " (%s/%s)" % (index, total) if total > 0 else ""
		stats = " %s/%s" % (card.atk, health) if card.atk + health > 0 else ""
		race = " (%s)" % (card.race.name.title()) if card.race != Race.INVALID else ""
		rarity = " %s" % card.rarity.name.title() if card.rarity != Rarity.INVALID else ""
		descr = "\n[%s Mana,%s%s %s%s]" % (card.cost, stats, rarity, card.type.name.title(), race)
		text = "\n" + card.description if len(card.description) else ""
		flavor = "\n> " + card.flavortext if len(card.flavortext) else ""
		return "```Markdown\n[%s][%s]%s%s%s%s\n```" % (card.name, card.id, search_index, descr, text, flavor)