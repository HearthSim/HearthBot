from hearthstone import deckstrings
import binascii


class DeckHandler():
    def handle(self, input):
        if ' ' not in input:
            if self.isvalid(input):
                return self.geturl(input)
        for word in input.split():
            if self.isvalid(word):
                return self.geturl(word)
        return None


    @staticmethod
    def isvalid(text):
        try:
            deckstrings.parse_deckstring(text)
        except binascii.Error:
            return False
        except ValueError:
            return False
        return True

    @staticmethod
    def geturl(deckstring):
        return 'WIP'