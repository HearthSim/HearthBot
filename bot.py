#!/usr/bin/env python

import argparse
import json

import discord
from discord import app_commands

from commands import install_commands
from handlers.message_handler import MessageHandler


class HearthBotClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		await self.tree.sync()


def main():
	p = argparse.ArgumentParser()
	p.add_argument("--config", required=True, help="Path to configuration file")
	args = p.parse_args()

	with open(args.config, "r") as f:
		config = json.load(f)

	intents = discord.Intents.default()
	activity = discord.CustomActivity("DM me !help or !invite")
	client = HearthBotClient(intents=intents, activity=activity)
	install_commands(config, client)

	@client.event
	async def on_ready():
		print("Logged in as", client.user.name)

	# Legacy commands
	message_handler = MessageHandler(config, client)

	@client.event
	async def on_message(message):
		await message_handler.handle(message)


	client.run(config["token"])


if __name__ == "__main__":
	main()
