import re
from enum import Enum, IntEnum
from typing import Any, Optional

import discord
from discord import ActionRow, ButtonStyle, app_commands
from hearthstone import cardxml
from hearthstone.cardxml import CardXML
from hearthstone.enums import CardType, GameTag, Locale, Race, Rarity


class LanguageNotFound(Exception):
	pass


class CardNotFound(Exception):
	pass


ValidLocales = IntEnum("Locale", [(i.name, i.value) for i in Locale if i.value >= 0])

class CollectibleFilter(Enum):
	ALL = 1
	UNCOLLECTIBLE_ONLY = 2
	COLLECTIBLE_ONLY = 3

	@property
	def collectible(self):
		if self == CollectibleFilter.COLLECTIBLE_ONLY:
			return True
		elif self == CollectibleFilter.UNCOLLECTIBLE_ONLY:
			return False
		else:
			return None


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


class PaginationUI(discord.ui.View):
	def __init__(self, get_prev_page: Optional[Any], get_next_page: Optional[Any]):
		self.get_prev_page = get_prev_page
		self.get_next_page = get_next_page
		super().__init__()
		self.init_page_buttons()

	def init_page_buttons(self):
		prev_page = discord.ui.Button(
			label="Previous Page",
			style=discord.ButtonStyle.grey,
			disabled=self.get_prev_page is None,
		)
		prev_page.callback = self.prev_page

		next_page = discord.ui.Button(
			label="Next Page",
			style=discord.ButtonStyle.grey,
			disabled=self.get_next_page is None,
		)
		next_page.callback = self.next_page

		self.add_item(prev_page)
		self.add_item(next_page)

	async def prev_page(self, interaction: discord.Interaction):
		if self.get_prev_page is None:
			return
		content, view = self.get_prev_page()
		await interaction.response.edit_message(
			content=content,
			view=view,
		)
		self.stop()

	async def next_page(self, interaction: discord.Interaction):
		if self.get_next_page is None:
			return
		content, view = self.get_next_page()
		await interaction.response.edit_message(
			content=content,
			view=view,
		)
		self.stop()


class CardCommands:
	def __init__(self, max_responses_public: int, max_responses_private: int):
		self.max_responses_public = max_responses_public
		self.max_responses_private = max_responses_private
		self.db = {}
		for key in db.keys():
			self.db[key.lower()] = db[key]

	def install(self, client):
		@client.tree.command(name="card", description="Retrieve details about a Hearthstone card")
		@app_commands.describe(
			tags="Include tags data in the response",
			requirements="Include requirements data in the response",
			entourage="Include entourage data in the response",
			collectible="Filter to only collectible/only uncollectible cards",
		)
		async def card(
			interaction: discord.Interaction,
			search_text: str,
			locale: ValidLocales = ValidLocales.enUS,
			tags: bool = False,
			requirements: bool = False,
			entourage: bool = False,
			collectible: CollectibleFilter = None,
		):
			if collectible is None:
				# Default to all collectibles if clearly a dbf id or a card id
				collectible = (
					CollectibleFilter.ALL if re.match(r"^\d+$", search_text) or "_" in search_text
					else CollectibleFilter.COLLECTIBLE_ONLY
				)

			try:
				response, view = self.do_card_search(
					search_text,
					self.max_responses_public,
					locale=Locale(locale.value),
					tags=tags,
					requirements=requirements,
					entourage=entourage,
					collectible=collectible.collectible,
				)
				await interaction.response.send_message(
					content=response,
					view=view
				)
			except CardNotFound:
				await interaction.response.send_message(
					"Card Not Found",
					ephemeral=True,
				)
			except LanguageNotFound:
				await interaction.response.send_message(
					"Language not found. Supported language keys are e.g. `enUS` or `deDE`",
					ephemeral=True,
				)

	def do_card_search(
		self,
		term: str,
		max_response: int,
		locale: Locale,
		tags: bool,
		requirements: bool,
		entourage: bool,
		collectible: Optional[bool],
		page: Optional[int] = 1,
	):
		lterm = term.lower()
		params = {
			"tags": tags,
			"requirements": requirements,
			"entourage": entourage,
			"lang": str(locale.name),
		}

		if lterm in self.db:
			card = self.db[lterm]
			if card is not None:
				return self.stringify_card(card, include_url=True, params=params), None

		try:
			term_num = None
			try:
				term_num = int(lterm)
			except Exception:
				pass
			cards = []
			for card in db.values():
				if collectible is None or collectible == card.collectible:
					card_name = card.name.lower()
					if (
						term_num is None and (lterm == ("\"%s\"" % card_name) or lterm in card_name) or
						term_num is not None and term_num == card.dbf_id
					):
						cards.append(card)
			num_cards = len(cards)
			if num_cards == 0:
				raise CardNotFound
			if num_cards == 1:
				return self.stringify_card(cards[0], True, params), None

			page_size = min(max_response, num_cards)
			page_count = int(num_cards / page_size)
			page = max(min(page, page_count), 1)
			offset = max(0, (page - 1) * page_size)
			hint = f"```Page {page}/{page_count}```" if page_count > 1 else ""

			has_next_page = page < page_count
			def get_next_page():
				return self.do_card_search(
					term=term,
					max_response=max_response,
					locale=locale,
					tags=tags,
					requirements=requirements,
					entourage=entourage,
					collectible=collectible,
					page=page + 1,
				)

			has_prev_page = page > 1
			def get_prev_page():
				return self.do_card_search(
					term=term,
					max_response=max_response,
					locale=locale,
					tags=tags,
					requirements=requirements,
					entourage=entourage,
					collectible=collectible,
					page=page - 1,
				)

			return "".join(
				self.stringify_card(cards[i], False, params)
				for i in range(offset, min(offset + page_size, num_cards))
			) + hint, PaginationUI(
				get_next_page=get_next_page if has_next_page else None,
				get_prev_page=get_prev_page if has_prev_page else None,
			) if has_next_page or has_prev_page else None
		except Exception as e:
			print(e)
		raise CardNotFound

	def stringify_card(
		self,
		card,
		include_url,
		params,
	):
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
					raise LanguageNotFound
				locale = lang[0:2].lower() + lang[2:4].upper()
				try:
					card.loc_name(locale)
				except Exception:
					raise LanguageNotFound
		health = card.durability if card.type == CardType.WEAPON else card.health
		stats = " %s/%s" % (card.atk, health) if card.atk + health > 0 else ""
		race = " (%s)" % (card.race.name.title()) if card.race != Race.INVALID else ""
		rarity = " %s" % card.rarity.name.title() if card.rarity != Rarity.INVALID else ""
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
