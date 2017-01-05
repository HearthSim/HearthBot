import re
import asyncio
from .issue_handler import IssueHandler
from .card_handler import CardHandler
from .enum_handler import EnumHandler


CMD_CARD = "!card "
CMD_CARD_COLLECTIBLE = "!cardc "
CMD_CARD_NONCOLLECTIBLE = "!cardn "
CMD_TAG = "!tag "
CMD_ENUM = "!enum "


def log(message, response, edited):
	print("[%s]" % (message.channel), message.content.encode("utf-8"))
	print("Reponse:", response.encode("utf-8"), edited)


class MessageHandler():
	def __init__(self, config, client):
		self.client = client
		self.issue_handler = IssueHandler(config["repos"])
		self.card_handler = CardHandler()
		self.enum_handler = EnumHandler(config)
		self.max_cards_public = int(config["max_cards_public"])
		self.max_cards_private = int(config["max_cards_private"])


	async def handle(self, message):
		if message.author.id == self.client.user.id:
			return
		if await self.handle_cmd(message):
			return

		matches = re.findall(r"(?<!<)(\w+)?#(\d+)($|\s)", message.content)
		if len(matches):
			print("[%s]" % (message.channel), message.content)
		for match in matches:
			prefix = match[0]
			issue = match[1]
			response = self.issue_handler.handle(message.channel.name, prefix, issue)
			print("Reponse:", response.encode("utf-8") if response else "None")
			if response is not None:
				await self.client.send_message(message.channel, response)


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
		return False


	async def respond(self, message, response, my_message=None):
		log(message, response, my_message is not None)
		if my_message is None:
			my_message = await self.client.send_message(message.channel, response)
		else:
			await self.client.edit_message(my_message, response)
		await self.check_edit(message, my_message)


	async def handle_card(self, message, cmd, my_message, collectible=None):
		response = self.card_handler.handle(message.content[len(cmd):], self.max_response(message), collectible)
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
