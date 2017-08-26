from hearthstone import deckstrings
import binascii
import requests


class DeckHandler():

    def __init__(self, deck_response):
        self.deck_response = deck_response

    def handle(self, input):
        # Handling the message being just the deck string
        if ' ' not in input:
            if self.isvalid(input):
                url = self.geturl(input)
                if url != '':
                    return self.deck_response + url
        # Handling multiple words and multiple deck strings in the message.
        result = ''
        for word in input.split():
            if self.isvalid(word):
                result += self.geturl(word)
        if result != '':
            return self.deck_response + result
        return None


    @staticmethod
    def isvalid(potentialstring):
        try:
            deckstrings.parse_deckstring(potentialstring)
        except binascii.Error:
            return False
        except ValueError:
            return False
        return True

    @staticmethod
    def geturl(deckstring):
        deck = deckstrings.Deck().from_deckstring(deckstring)
        cards = []
        for cardid, count in deck.get_dbf_id_list():
            for i in range(0, count):
                cards.append(cardid)
        request = requests.post("https://hsreplay.net/api/v1/decks/", data={"format": 1, "cards": cards})
        # handles status code 201, when it creates a new deck. No reason to link to a new deck with no stats!
        if request.status_code != 200:
            print('Got status code ' + str(request.status_code) + " from HSReplay API.")
            return ''
        return "https://hsreplay.net/decks/" + request.json()["shortid"] + '\n'