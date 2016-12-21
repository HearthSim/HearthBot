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
	if message.author.id == client.user.id:
		return
	if message.content.startswith("!card "):
		response = card_handler.handle(message.content[6:])
		print("[%s]" % (message.channel), message.content)
		print("Reponse:", response)
		await client.send_message(message.channel, response);
		return
	matches = re.findall("(\w+)?#(\d+)", message.content)
	if len(matches):
		print("[%s]" % (message.channel), message.content)		
	for match in matches:
		prefix = match[0]
		issue = match[1]
		response = issue_handler.handle(message.channel.name, prefix, issue)
		print("Reponse:", response)
		if response is not None:
			await client.send_message(message.channel, response)


client.run(config["token"])