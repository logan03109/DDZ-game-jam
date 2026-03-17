#libraries
import random
from collections import Counter

#classes
suits = ["Hearts", "Spades", "Diamonds", "Clubs"]
values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
sets = ["single", "double", "triple", "triple+1", "triple+2", "bomb", "straightx5", "straightx6", "straightx7", "straightx8", "straightx9", "straightx10", "straightx11", "straightx12", "doublex3", "doublex4", "doublex5", "doublex6", "doublex7", "doublex8", "doublex9", "doublex10", "triplex2", "triplex3", "triplex4", "triplex5", "triplex6", "triple+1x2", "triple+1x3", "triple+1x4", "triple+1x5", "triple+2x2", "triple+2x3", "triple+2x4", "jokerbomb"]
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def show(self):
        return f"{self.value} {self.suit}"

class Deck:
    def __init__(self):
        self.deck = []
        self.pool = []

    def shuffle(self):
        random.shuffle(self.deck)

    def make_deck(self):
        for suit in suits:
            for value in values:
                self.deck.append(Card(suit, value))
                self.deck.append(Card(suit, value))
        self.deck.append(Card("Joker", "Small"))
        self.deck.append(Card("Joker", "Small"))
        self.deck.append(Card("Joker", "Big"))
        self.deck.append(Card("Joker", "Big"))
        self.shuffle()

    def redeck(self):
        self.deck = self.pool
        self.pool = []
        self.shuffle()

class Hand:
    def __init__(self):
        self.hand = []
        self.sets = []

    def draw_hand(self, deck):
        pass

    def order_hand(self):
        self.hand.sort(key=lambda card: card.value)

    def draw_turn(self, deck, cards_used):
        for n in range(cards_used):
            self.hand.append(deck.pop())

class PlayerHand(Hand):
    def __init__(self):
        super().__init__()

    def draw_hand(self, deck):
        for n in range(20):
            self.hand.append(deck.pop())

class BossHand(Hand):
    def __init__(self):
        super.__init__(self)

    def draw_hand(self, deck):
        for n in range(17):
            self.hand.append(deck.pop())

class Player:
    def __init__(self, deck):
        self.hp = 100
        self.hand = PlayerHand()
        self.hand.draw_hand(deck)

    def pick_cards(self):
        pass

    def find_all_sets(self):
        pass

    def validate_set(self, cards):
        ranks = []
        for card in cards:
            ranks.append(card.value)
        ranks.sort()
        count = Counter(ranks)
        valid = False
        set = None
        if len(cards) == 1:
            valid = True
            set = sets[0]
        elif len(cards) == 2:
            if len(cards) == 1:
                valid = True
                set = sets[1]
        elif len(cards) == 3:
            if len(cards) == 1:
                valid = True
                set = sets[2]
        elif len(cards) == 4:
            if len(cards) == 1:
                valid = True
                set = sets[5]
            else:
                pass
        print(ranks, count, set, valid)
        return valid

    def play_turn(self):
        pass

#main
def main():
    deck = Deck()
    deck.make_deck()
    player1 = Player(deck.deck)
    player1.validate_set([Card("Hearts", "3"), Card("Club", "3")])

if __name__ == '__main__':
    main()