from hearthstone import deckstrings
import binascii
import requests
import json

class DeckHandler():

    def __init__(self, deck_response):
        self.deck_response = deck_response
        self.decks = self.get_decks()

    def handle(self, input):
        # Handling the message being just the deck string
        if ' ' not in input:
            if self.is_valid(input):
                url = self.get_url(input)
                if url != '':
                    return self.deck_response + url
        # Handling multiple words and multiple deck strings in the message.
        result = ''
        for word in input.split():
            if self.is_valid(word):
                result += self.get_url(word)
        if result != '':
            return self.deck_response + result
        return None


    @staticmethod
    def is_valid(potentialstring):
        try:
            deckstrings.parse_deckstring(potentialstring)
        except binascii.Error:
            return False
        except ValueError:
            return False
        return True

    def get_url(self, deckstring):
        deck = deckstrings.Deck().from_deckstring(deckstring)
        cards = []
        for cardid, count in deck.get_dbf_id_list():
            for i in range(0, count):
                cards.append(cardid)
        request = requests.post("https://hsreplay.net/api/v1/decks/", data={"format": 1, "cards": cards})
        # handles status code 201, when it creates a new deck. No reason to link to a new deck with no stats!
        if request.status_code != 200:
            print("Got status code " + str(request.status_code) + " from HSReplay API.")
            return ''

        shortid = request.json()["shortid"]

        if shortid not in self.decks:
            return ''

        return "https://hsreplay.net/decks/" + shortid + '/\n'

    @staticmethod
    def get_decks():
        request = requests.get("https://hsreplay.net/api/v1/analytics/query/list_deck_inventory/")
        if request.status_code != 200:
            print("Error " + request.status_code + " when preloading HSReplay decks: " + request.text)
            return []
        decks = []
        try:
            for key in json.loads(request.text)["series"]:
                decks.append(key)
        except:
            print('Error when preloading decks from HSReplay.')
            raise
        print('Successfully preloaded HSReplay decks.')
        return decks


