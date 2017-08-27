from hearthstone import deckstrings
import binascii
import requests
import json
import threading

TASK_DELAY = 60 * 60 * 1

class DeckHandler():

    def __init__(self, deck_response):
        self.deck_response = deck_response
        self.decks = []
        self.update_decks()


    def handle(self, input):
        result = ''
        for word in input.split():
            deck = self.get_deck(word)
            if deck != None:
                result += self.get_url(deck)
        if result != '':
            return self.deck_response + result
        return None


    @staticmethod
    def get_deck(potentialstring):
        try:
            return deckstrings.Deck.from_deckstring(potentialstring)
        except binascii.Error:
            return None
        except ValueError:
            return None

    def get_url(self, deck):
        cards = []
        for cardid, count in deck.get_dbf_id_list():
            for i in range(0, count):
                cards.append(cardid)
        request = requests.post("https://hsreplay.net/api/v1/decks/", data={"format": int(deck.format), "cards": cards})
        # handles status code 201, when it creates a new deck. No reason to link to a new deck with no stats!
        if request.status_code != 200:
            print("Got status code " + str(request.status_code) + " from HSReplay API.")
            return ''

        shortid = request.json()["shortid"]

        if shortid not in self.decks:
            return ''

        return "https://hsreplay.net/decks/" + shortid + '/\n'

    def update_decks(self):
        # Start a timer to update decks
        threading.Timer(TASK_DELAY, self.update_decks).start()
        request = requests.get("https://hsreplay.net/api/v1/analytics/query/list_deck_inventory/")
        if request.status_code != 200:
            print("Error " + request.status_code + " when updating HSReplay decks: " + request.text)
            return
        olddecks = self.decks
        self.decks = []
        try:
            for key in json.loads(request.text)["series"]:
                self.decks.append(key)
        except:
            print('Error when updating decks from HSReplay. Reverting update')
            self.decks = olddecks
            raise




