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


def max_response(message):
	return 10 if message.channel.is_private else 2


def log(message, response):
	print("[%s]" % (message.channel), message.content)
	print("Reponse:", response.encode("utf-8"))


class MessageHandler():
	def __init__(self, config, client):
		self.client = client;
		self.issue_handler = IssueHandler(config["repos"])
		self.card_handler = CardHandler()
		self.enum_handler = EnumHandler()


	async def handle(self, message):
		if message.author.id == self.client.user.id:
			return
		if await self.handle_cmd(message):
			return

		matches = re.findall("(?<!<)(\w+)?#(\d+)", message.content)
		if len(matches):
			print("[%s]" % (message.channel), message.content)
		for match in matches:
			prefix = match[0]
			issue = match[1]
			response = self.issue_handler.handle(message.channel.name, prefix, issue)
			print("Reponse:", response.encode("utf-8") if response else "None")
			if response is not None:
				await self.client.send_message(message.channel, response)


	async def handle_cmd(self, message):
		if message.content.startswith(CMD_CARD):
			await self.handle_card(message, CMD_CARD);
			return True
		if message.content.startswith(CMD_CARD_COLLECTIBLE):
			await self.handle_card(message, CMD_CARD_COLLECTIBLE, True);
			return True
		if message.content.startswith(CMD_CARD_NONCOLLECTIBLE):
			await self.handle_card(message, CMD_CARD_NONCOLLECTIBLE, False);
			return True
		if message.content.startswith(CMD_TAG):
			response = self.enum_handler.handle("GameTag " + message.content[len(CMD_TAG):])
			log(message, response)
			await self.client.send_message(message.channel, response);
			return True
		if message.content.startswith(CMD_ENUM):
			response = self.enum_handler.handle(message.content[len(CMD_ENUM):])
			log(message, response)
			await self.client.send_message(message.channel, response);
			return True
		return False


	async def handle_card(self, message, cmd, collectible = None):
		response = self.card_handler.handle(message.content[len(cmd):], max_response(message), collectible)
		log(message, response)
		await self.client.send_message(message.channel, response);
