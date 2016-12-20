import discord
import re
import asyncio
import json
from handlers.issue_handler import IssueHandler
from handlers.card_handler import CardHandler

with open('config.json', 'r') as f:
    config = json.load(f)

client = discord.Client()
issue_handler = IssueHandler(config["repos"])
card_handler = CardHandler()

@client.event
async def on_ready():
    print('Logged in as', client.user.name)

@client.event
async def on_message(message):
	if message.content.startswith("!card "):
		response = card_handler.handle(message.content[6:])
		await client.send_message(message.channel, response);
		return
	match = re.match("(\w+)?#(\d+)", message.content)
	if match is not None:
		prefix = match.group(1)
		issue = match.group(2)
		response = issue_handler.handle(message.channel.name, prefix, issue)
		if response is not None:
			await client.send_message(message.channel, response)


client.run(config["token"])