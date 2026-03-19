# libraries
import random
from collections import Counter

# data
suits = ["Hearts", "Spades", "Diamonds", "Clubs"]  # suits
values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]  # values, excluding jokers
sets = ["single", "double", "triple", "triple+1", "triple+2", "bomb", "single_straight", "double_straight",
        "triple_straight", "triple+1_straight", "triple+2_straight", "jokerbomb"]  # every type of set
gimmicks = ["bleed", "regen", "damage_reduction", "damage_multiplier"]  # gimmicks
base_damage_constant = {"single": 1,
                        "double": 2,
                        "triple": 3,
                        "triple+1": 3.25,
                        "triple+2": 3.5,
                        "bomb": 20,
                        "single_straight": 5,
                        "double_straight": 8,
                        "triple_straight": 15,
                        "triple+1_straight": 15.25,
                        "triple+2_straight": 15.5,
                        "jokerbomb": 25}  # damage multipler for each set - TEMPORARY


# classes
class Card:
    def __init__(self, suit, value):  # basic cards have just a suit and value
        self.suit = suit
        self.value = value

    def show(self):  # method really only used for python console testing - will need to be implemented with pygame
        return f"{self.value} {self.suit}"


class GimmickCard(Card):
    def __init__(self, suit, value, gimmick):  # inherits from card - has a gimmick attribute applying to a gimmic above
        super().__init__(suit, value)
        self.gimmick = gimmick


class Deck:
    def __init__(self):  # deck is the cards in the deck, pool is the cards that have been placed down for the turn
        self.deck = []
        self.pool = []

    def shuffle(self):  # shuffles deck
        random.shuffle(self.deck)

    def make_deck(self):  # makes two decks
        for suit in suits:
            for value in values:
                self.deck.append(Card(suit, value))
                self.deck.append(Card(suit, value))
        self.deck.append(Card("Joker", "Small"))
        self.deck.append(Card("Joker", "Small"))
        self.deck.append(Card("Joker", "Big"))
        self.deck.append(Card("Joker", "Big"))
        self.shuffle()

    def redeck(
            self):  # this is when the cards played for the turn are added back to the deck (im thinking this happens after each turn)
        self.deck += self.pool
        self.pool = []
        self.shuffle()


class Hand:
    def __init__(self):  # parent hand class - hand is cards in hand, sets is explained later
        self.hand = []
        self.sets = []

    def draw_hand(self, deck):  # abstract method
        pass

    def order_hand(self):  # orders hand by value, with no suit consideration
        self.hand.sort(key=lambda card: card.value)

    def draw_turn(self, deck,
                  cards_used):  # royce and i said that after each turn (i.e. set placed), you draw the same number of cards played
        for n in range(cards_used):
            self.hand.append(deck.pop())


class PlayerHand(Hand):
    def __init__(self):  # inherits from hand, PLAYER
        super().__init__()

    def draw_hand(self, deck):  # draws 20 at start
        for n in range(20):
            self.hand.append(deck.pop())


class BossHand(Hand):
    def __init__(self):  # inherits from hand, NPC
        super().__init__()

    def draw_hand(self, deck):  # draws 17 at start
        for n in range(17):
            self.hand.append(deck.pop())


class Player:
    def __init__(self, deck):  # includes all attributes for a player
        self.hp = 1000
        self.hand = PlayerHand()
        self.hand.draw_hand(deck)
        self.regen = 1
        self.damage_mult = 1
        self.gimmick_chance = {gimmicks[0]: [[suits[0], 0], [suits[1], 0], [suits[2], 0], [suits[3], 0]],
                               gimmicks[1]: [[suits[0], 0], [suits[1], 0], [suits[2], 0], [suits[3], 0]],
                               gimmicks[2]: [[suits[0], 0], [suits[1], 0], [suits[2], 0], [suits[3], 0]],
                               gimmicks[3]: [[suits[0], 0], [suits[1], 0], [suits[2], 0], [suits[3],
                                                                                           0]]}  # dictionary for every gimmick - each suit has a chance of turning into that gimmick, displayed in the 2d array

    def pick_cards(
            self):  # i avoided doing this because this will certainly require pygame consideration, and is not useful for python console testing
        pass

    def find_all_sets(
            self):  # a method i considered, where instead of you choosing cards and it gets validated, all valid sets are already displayed - not implemented
        pass

    def validate_set(self,
                     cards):  # you pick cards, and it finds if it is valid/what kind of set it is - outputs valid, the kind of set, the cards of the set
        ranks = []
        suits = []
        for card in cards:
            if card.value == "J":
                ranks.append("11")
            elif card.value == "Q":
                ranks.append("12")
            elif card.value == "K":
                ranks.append("13")
            elif card.value == "A":
                ranks.append("14")
            elif card.value == "2":
                ranks.append("15")
            else:
                ranks.append(card.value)
            suits.append(card.suit)
        ranks.sort()
        count = Counter(ranks)
        valid = False
        ddz_set = None
        if set(suits) == {"Joker"}:
            valid = True
            ddz_set = sets[11]
        elif "Joker" in suits:
            pass
        elif len(cards) >= 4 and len(list(count.values())) == 1:
            valid = True
            ddz_set = sets[5]
        elif len(cards) == 1:
            valid = True
            ddz_set = sets[0]
        elif len(cards) == 2 and list(count.values()) == [2]:
            valid = True
            ddz_set = sets[1]
        elif len(cards) == 3 and list(count.values()) == [3]:
            valid = True
            ddz_set = sets[2]
        elif len(cards) == 4 and (list(count.values()) == [1, 3] or list(count.values()) == [3, 1]):
            valid = True
            ddz_set = sets[3]
        elif len(cards) == 5 and (list(count.values()) == [2, 3] or list(count.values()) == [3, 2]):
            valid = True
            ddz_set = sets[4]
        elif len(cards) >= 5 and len(set(ranks)) == len(cards) and "15" not in ranks:
            consecutive = True
            for idx in range(0, len(ranks) - 1):
                if int(ranks[idx]) != int(ranks[idx + 1]) - 1:
                    consecutive = False
                    break
            if consecutive:
                valid = True
                ddz_set = sets[6]
        elif len(cards) >= 6 and len(set(ranks)) == len(cards) // 2 and all(x == 2 for x in list(count.values())):
            consecutive = True
            set_list = sorted(list(set(ranks)))
            for idx in range(0, len(set_list) - 1):
                if int(set_list[idx]) != int(set_list[idx + 1]) - 1:
                    consecutive = False
                    break
            if consecutive:
                valid = True
                ddz_set = sets[7]
        elif len(cards) >= 6:
            if len(set(ranks)) == len(cards) // 3:
                consecutive = True
                set_list = sorted(list(set(ranks)))
                for idx in range(0, len(set_list) - 1):
                    if int(set_list[idx]) != int(set_list[idx + 1]) - 1:
                        consecutive = False
                        break
                if consecutive:
                    valid = True
                    ddz_set = sets[8]
            else:
                if len(cards) >= 8 and list(count.values()).count(3) == list(count.values()).count(1) and list(
                        count.values()).count(3) + list(count.values()).count(1) == len(count):
                    consecutive = True
                    triples = [value for value, num in count.items() if num == 3]
                    set_list = sorted(list(set(ranks)))
                    for idx in range(0, len(triples) - 1):
                        if int(triples[idx]) != int(triples[idx + 1]) - 1:
                            consecutive = False
                            break
                    if consecutive:
                        valid = True
                        ddz_set = sets[9]
                elif len(cards) >= 10 and list(count.values()).count(3) == list(count.values()).count(2) and list(
                        count.values()).count(3) + list(count.values()).count(2) == len(count):
                    consecutive = True
                    triples = [value for value, num in count.items() if num == 3]
                    set_list = sorted(list(set(ranks)))
                    for idx in range(0, len(triples) - 1):
                        if int(triples[idx]) != int(triples[idx + 1]) - 1:
                            consecutive = False
                            break
                    if consecutive:
                        valid = True
                        ddz_set = sets[10]
        return valid, ddz_set, cards

    def display_set(self, valid, ddz_set):  # shows result of above method - used in conjunction with above
        if valid:
            return ddz_set
        else:
            return "INVALID SET"

    def play_turn(self, cards, deck):  # removes the cards you have played, and adds them to the pool
        for card in cards:
            self.hand.hand.remove(card)
            deck.pool.append(card)

    def damage_calc(self, cards, ddz_set,
                    boss):  # damage calculation - needs balancing, TEMPORARY, returns damage dealt - has boss parameter since you need to direct attack at a boss
        card_values = []
        for card in cards:
            if card.value == "J":
                card_values.append(11)
            elif card.value == "Q":
                card_values.append(12)
            elif card.value == "K":
                card_values.append(13)
            elif card.value == "A":
                card_values.append(14)
            elif card.value == "2":
                card_values.append(15)
            elif card == Card("Joker", "Small"):
                card_values.append(16)
            elif card == Card("Joker", "Big"):
                card_values.append(17)
            else:
                card_values.append(int(card.value))
        # temp code for damage
        damage = max(card_values) * base_damage_constant[ddz_set] * self.damage_mult
        return damage

    def take_damage(self, damage):  # takes away your health
        self.hp -= damage

    def status(self):  # checks if you are alive - returns True if yes, if dead then False
        if self.hp <= 0:
            return False
        else:
            return True


# main
def main():
    deck = Deck()
    deck.make_deck()
    player1 = Player(deck.deck)
    valid, ddz_set, cards = player1.validate_set(
        [Card("Heart", "A"), Card("Heart", "A"), Card("Heart", "A"), Card("Heart", "K"), Card("Heart", "K"),
         Card("Heart", "K"), Card("Heart", "3"), Card("Heart", "3"), Card("Heart", "2"), Card("Heart", "2")])
    print(player1.damage_calc(cards, ddz_set, 0))


if __name__ == '__main__':
    main()