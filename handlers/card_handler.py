import re

from hearthstone import cardxml
from hearthstone.cardxml import CardXML
from hearthstone.enums import CardType, GameTag, Race, Rarity


ERR_LANG_NOT_FOUND = "Language not found. Supported language keys are e.g. `enUS` or `deDE`"


db, _ = cardxml.load()


def loc_name(self, locale):
	return self.strings[GameTag.CARDNAME][locale]


def loc_text(self, locale):
	return self.strings[GameTag.CARDTEXT_INHAND][locale]


def loc_flavor(self, locale):
	return self.strings[GameTag.FLAVORTEXT][locale]


CardXML.loc_name = loc_name
CardXML.loc_text = loc_text
CardXML.loc_flavor = loc_flavor


class CardHandler():
	def __init__(self):
		self.db = {}
		for key in db.keys():
			self.db[key.lower()] = db[key]

	def handle(self, input, max_response, collectible=None):
		term, params = self.parse_input(input)

		if term in self.db:
			card = self.db[term]
			if card is not None:
				return self.stringify_card(card, include_url=True, params=params)

		try:
			page = 1
			match = re.match(r"^(.+?)\s+(\d+)$", term)
			if match is not None:
				term = match.group(1).strip()
				page = max(1, int(match.group(2)))

			term_num = None
			try:
				term_num = int(term)
			except Exception:
				pass
			cards = []
			for card in db.values():
				if collectible is None or collectible == card.collectible:
					card_name = card.name.lower()
					if (
						term_num is None and (term == ("\"%s\"" % card_name) or term in card_name) or
						term_num is not None and term_num == card.dbf_id
					):
						cards.append(card)
			num_cards = len(cards)
			if num_cards == 0:
				return "Card not found"
			if num_cards == 1:
				return self.stringify_card(cards[0], 0, 0, True, params)

			page_size = min(max_response, num_cards)
			page_count = int(num_cards / page_size)
			page_index_hint = (
				" - What are you trying to do here?! It clearly says %d!" % (page_count)
			) if page > page_count else ""
			page = min(page, page_count)
			offset = max(0, (page - 1) * page_size)
			next_page_hint = " - append '2' to see the second page." if not offset else ""
			hint = (
				"```Page %d/%d%s```" % (page, page_count, next_page_hint or page_index_hint)
			) if page_count > 1 else ""
			return hint + "".join(
				self.stringify_card(cards[i], i + 1, num_cards, params)
				for i in range(offset, min(offset + page_size, num_cards))
			)
		except Exception as e:
			print(e)
		return "Card not found"

	def parse_input(self, input):
		parts = input.split(" --")
		term = parts[0].strip().lower()
		params = {}
		for part in parts[1:]:
			p = part.split("=")
			value = p[1] if len(p) > 1 else True
			params[p[0].lower()] = value
		return term, params

	def stringify_card(self, card, index=0, total=0, include_url=False, params=None):
		locale = card.locale
		tags = ""
		reqs = ""
		ents = ""
		if params:
			if params.get("tags", False):
				tags = "\n%s" % self.get_tags(card)
			if params.get("reqs", False):
				reqs = "\n%s" % self.get_reqs(card)
			if params.get("ents", False) or params.get("entourage", False):
				ents = "\n%s" % self.get_ents(card)
			lang = params.get("lang", None)
			if lang:
				if len(lang) != 4:
					return ERR_LANG_NOT_FOUND
				locale = lang[0:2].lower() + lang[2:4].upper()
				try:
					card.loc_name(locale)
				except Exception:
					return ERR_LANG_NOT_FOUND
		health = card.durability if card.type == CardType.WEAPON else card.health
		stats = " %s/%s" % (card.atk, health) if card.atk + health > 0 else ""
		race = " (%s)" % (card.race.name.title()) if card.race != Race.INVALID else ""
		rarity = " %s" % card.rarity.name.title() if card.rarity != Rarity.INVALID else ""
		if card.tags.get(GameTag.IS_BACON_POOL_MINION, False) and card.tags.get(GameTag.TECH_LEVEL, 0):
			descr = "\n[Tier %s,%s%s %s%s]" % (card.tags.get(GameTag.TECH_LEVEL), stats, rarity, card.type.name.title(), race)
		else:
			descr = "\n[%s Mana,%s%s %s%s]" % (card.cost, stats, rarity, card.type.name.title(), race)
		text = "\n" + card.loc_text(locale) if len(card.description) else ""
		flavor = "\n> " + card.loc_flavor(locale) if len(card.flavortext) else ""
		if include_url and self.has_link(card):
			url = "https://hsreplay.net/cards/%s\n" % (card.dbf_id)
		else:
			url = ""

		return (
			"```Markdown\n[%s][%s][%s]%s%s%s%s%s%s```%s"
			% (card.loc_name(locale), card.id, card.dbf_id, descr, text, flavor, tags, reqs, ents, url)
		)

	def has_link(self, card):
		return card.collectible and card.type.name in ["MINION", "SPELL", "WEAPON"]

	def get_tags(self, card):
		tags = ", ".join("%s=%s" % (
			getattr(key, "name", int(key)), card.tags[key]
		) for key in card.tags.keys())
		return (
			"# Tags: [%s]"
			% (tags)
		)

	def get_reqs(self, card):
		reqs_list = []
		for key in card.requirements.keys():
			val = "=%s" % card.requirements[key] if card.requirements[key] else ""
			reqs_list.append("%s%s" % (key.name, val))
		reqs = ", ".join(reqs_list)
		return (
			"# Requirements: [%s]"
			% (reqs)
		)

	def get_ents(self, card):
		ents = ", ".join([ent for ent in card.entourage])
		return (
			"# Entourage: [%s]" 
			% (ents)
		)
