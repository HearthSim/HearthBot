import discord
import re
import asyncio
import json
from handlers.issue_handler import IssueHandler
from handlers.card_handler import CardHandler
from handlers.enum_handler import EnumHandler


CMD_CARD = "!card "
CMD_CARD_COLLECTIBLE = "!cardc "
CMD_CARD_NONCOLLECTIBLE = "!cardn "
CMD_TAG = "!tag "
CMD_ENUM = "!enum "


with open('config.json', 'r') as f:
    config = json.load(f)

client = discord.Client()
issue_handler = IssueHandler(config["repos"])
card_handler = CardHandler()
enum_handler = EnumHandler()

@client.event
async def on_ready():
    print('Logged in as', client.user.name)

@client.event
async def on_message(message):
	if message.author.id == client.user.id:
		return
	if message.content.startswith(CMD_CARD):
		await handle_card(message, CMD_CARD);
		return
	if message.content.startswith(CMD_CARD_COLLECTIBLE):
		await handle_card(message, CMD_CARD_COLLECTIBLE, True);
		return
	if message.content.startswith(CMD_CARD_NONCOLLECTIBLE):
		await handle_card(message, CMD_CARD_NONCOLLECTIBLE, False);
		return
	if message.content.startswith(CMD_TAG):
		response = enum_handler.handle("GameTag " + message.content[len(CMD_TAG):])
		log(message, response)
		await client.send_message(message.channel, response);
		return
	if message.content.startswith(CMD_ENUM):
		response = enum_handler.handle(message.content[len(CMD_ENUM):])
		log(message, response)
		await client.send_message(message.channel, response);
		return	
		
	matches = re.findall("(?<!<)(\w+)?#(\d+)", message.content)
	if len(matches):
		print("[%s]" % (message.channel), message.content)		
	for match in matches:
		prefix = match[0]
		issue = match[1]
		response = issue_handler.handle(message.channel.name, prefix, issue)
		print("Reponse:", response.encode("utf-8"))
		if response is not None:
			await client.send_message(message.channel, response)

async def handle_card(message, cmd, collectible = None):
		response = card_handler.handle(message.content[len(cmd):], max_response(message), collectible)
		log(message, response)
		await client.send_message(message.channel, response);	

def max_response(message):
	return 10 if message.channel.is_private else 2

def log(message, response):
	print("[%s]" % (message.channel), message.content)
	print("Reponse:", response.encode("utf-8"))

client.run(config["token"])