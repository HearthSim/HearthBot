from .card_commands import CardCommands
from .deck_commands import DeckCommands
from .enum_commands import EnumCommands


def install_commands(config, client):
	cards = CardCommands(
		max_responses_public=config["max_cards_public"],
		max_responses_private=config["max_cards_private"],
	)
	decks = DeckCommands()
	enums = EnumCommands(
		max_responses_public=config["max_enum"],
		max_responses_private=config["max_enum"],
	)

	for commands in [cards, decks, enums]:
		commands.install(client)
