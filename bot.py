import json
import discord
from handlers.message_handler import MessageHandler


with open("config.json", "r") as f:
	config = json.load(f)
client = discord.Client()
message_handler = MessageHandler(config, client)


@client.event
async def on_ready():
	print("Logged in as", client.user.name)


@client.event
async def on_message(message):
	await message_handler.handle(message)


client.run(config["token"])
