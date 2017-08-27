import asyncio
import re
import sys
from datetime import datetime
from .card_handler import CardHandler
from .enum_handler import EnumHandler
from .issue_handler import IssueHandler
from .deck_handler import DeckHandler


__version__ = "1.0.1"

CMD_CARD = "!card "
CMD_CARD_COLLECTIBLE = "!cardc "
CMD_CARD_NONCOLLECTIBLE = "!cardn "
CMD_HELP = "!help"
CMD_TAG = "!tag "
CMD_ENUM = "!enum "
CMD_INVITE = "!invite"
CMD_PLUGINS = "!plugins"

USAGE = """
HearthBot v%s
Type `!card <search>` in public channels or PM to search for a Hearthstone card.

Example queries:
  * `!card Charge` -> Search for all cards with Charge in the name.
  * `!card "Charge"` -> Search for all cards with the exact name `Charge`.
  * `!card CS2_103` -> Search for a card by ID (exact match - CS2_103 is Charge).
  * `!card 344` -> Search for a card by ID (exact match - 344 is Charge).

Extra arguments (advanced):
  * `!card "Charge" --lang=frFR` -> Output the results in French.
  * `!card "Charge" --reqs` -> List the Play Requirements for the card.
  * `!card "Charge" --tags` -> List the GameTags for the card.

Made with love by HearthSim.
  * Support and discussion: https://discord.gg/hearthsim
  * Source code: https://github.com/HearthSim/HearthBot
  * Invite me to your server! PM me `!invite` for an invitation URL.

Pro tip: Typo'd your search? Edit it and I will edit my response. :)
""".strip() % (__version__)

PLUGINS_URL = "https://github.com/HearthSim/Hearthstone-Deck-Tracker/wiki/Available-Plugins"


def log_message(message):
	timestamp = datetime.now().isoformat()
	sys.stdout.write("[%s] [%s] [%s] [%s] %s\n" % (
		timestamp, message.server, message.channel, message.author, message.content)
	)
	sys.stdout.flush()


class MessageHandler():
	def __init__(self, config, client):
		self.client = client
		self.issue_handler = IssueHandler(config["repos"])
		self.card_handler = CardHandler()
		self.enum_handler = EnumHandler(config)
		self.deck_handler = DeckHandler(config["deck_response"])
		self.max_cards_public = int(config["max_cards_public"])
		self.max_cards_private = int(config["max_cards_private"])
		self.invite_url = config.get("invite_url", "")

	async def handle(self, message):
		if message.author.id == self.client.user.id:
			return
		if await self.handle_cmd(message):
			return

		matches = re.findall(r"(?<!<)(\w+)?#(\d+)($|\s|[^\w])", message.content)
		for match in matches:
			prefix = match[0]
			issue = match[1]
			response = self.issue_handler.handle(message.channel.name, prefix, issue)
			if response is not None:
				await self.client.send_message(message.channel, response)

		deckresponse = self.deck_handler.handle(message.content)
		if deckresponse is not None:
			await self.client.send_message(message.channel, deckresponse)

	async def handle_cmd(self, message, my_message=None):
		if message.content.startswith(CMD_CARD):
			await self.handle_card(message, CMD_CARD, my_message)
			return True

		if message.content.startswith(CMD_CARD_COLLECTIBLE):
			await self.handle_card(message, CMD_CARD_COLLECTIBLE, my_message, True)
			return True

		if message.content.startswith(CMD_CARD_NONCOLLECTIBLE):
			await self.handle_card(message, CMD_CARD_NONCOLLECTIBLE, my_message, False)
			return True

		if message.content.startswith(CMD_TAG):
			response = self.enum_handler.handle("GameTag " + message.content[len(CMD_TAG):])
			await self.respond(message, response, my_message)
			return True

		if message.content.startswith(CMD_ENUM):
			response = self.enum_handler.handle(message.content[len(CMD_ENUM):])
			await self.respond(message, response, my_message)
			return True

		if message.content.startswith(CMD_PLUGINS):
			await self.respond(message, PLUGINS_URL, my_message)
			return True

		if message.content.startswith(CMD_HELP):
			if message.channel.is_private:
				await self.respond(message, USAGE)
			else:
				await self.respond(message, "PM me !help for available commands. <3")
			return True

		if message.channel.is_private:
			if message.content.startswith(CMD_INVITE):
				if self.invite_url:
					await self.respond(message, self.invite_url)
				else:
					await self.respond(message, "No `invite_url` key found in the configuration.")
				return True
			else:
				log_message(message)

		return False

	async def respond(self, message, response, my_message=None):
		log_message(message)
		if my_message is None:
			my_message = await self.client.send_message(message.channel, response)
		else:
			await self.client.edit_message(my_message, response)
		await self.check_edit(message, my_message)

	async def handle_card(self, message, cmd, my_message, collectible=None):
		response = self.card_handler.handle(
			message.content[len(cmd):], self.max_response(message), collectible
		)
		await self.respond(message, response, my_message)

	async def check_edit(self, message, sent):
		original_content = message.content
		for _ in range(0, 30):
			if message.content != original_content:
				await self.handle_cmd(message, sent)
				return
			await asyncio.sleep(1)

	def max_response(self, message):
		return self.max_cards_private if message.channel.is_private else self.max_cards_public
