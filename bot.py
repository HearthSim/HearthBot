#!/usr/bin/env python

import argparse
import json
import subprocess

import discord
from handlers.message_handler import MessageHandler


def main():
	p = argparse.ArgumentParser()
	p.add_argument("--config", required=True, help="Path to configuration file")
	p.add_argument("--sync-roles", action="store_true")
	args = p.parse_args()
	sync_roles = args.sync_roles

	with open(args.config, "r") as f:
		config = json.load(f)

	client = discord.Client()
	message_handler = MessageHandler(config, client)

	@client.event
	async def on_ready():
		print("Logged in as", client.user.name)

		if sync_roles:
			p = subprocess.Popen(
				config["sync_roles"]["command"],
				stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
			)
			output, stderr = p.communicate()
			if stderr and b"psycopg2-binary" not in stderr:
				# ignore psycopg2-binary warning (sigh)
				raise RuntimeError("Error while running command: %r" % (stderr))
			accounts = json.loads(output.decode("utf-8"))
			discord_ids = [account_data["discord_id"] for account_data in accounts]
			server_id = config["sync_roles"]["server_id"]

			server = client.get_guild(str(server_id))
			if server is None:
				raise RuntimeError("Could not find server %r" % (server_id))

			role_name = config["sync_roles"]["role"]
			role_to_sync = None
			for role in server.roles:
				if role.name == role_name:
					role_to_sync = role
					break
			else:
				raise ValueError("Role %r not found on server %r" % (role_name, server))

			for member in server.members:
				member_roles = list(member.roles)
				if member.id in discord_ids:
					if role_to_sync not in member_roles:
						print("Adding role to %r" % (member))
						await member.add_roles(role_to_sync)
				else:
					if role_to_sync in member_roles:
						print("Removing role from %r" % (member))
						await member.remove_roles(role_to_sync)

			print("Done")
			await client.logout()

	@client.event
	async def on_message(message):
		if not sync_roles:
			await message_handler.handle(message)

	client.run(config["token"])


if __name__ == "__main__":
	main()
