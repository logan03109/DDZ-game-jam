#Player logic
from settings import *
import random
from collections import Counter
class Player:
    def __init__(self, deck, hand_size=20):  # includes all attributes for a player
        self.hp = 1000
        self.hand = PlayerHand()
        self.max_hp = 1000
        self.hand.draw_hand(deck, hand_size)
        self.damage_mult = 1
        self.active_gimmicks = []
        self.hand_size = hand_size
        self.bonus_shuffles = 0

    def pick_cards(
            self):  # i avoided doing this because this will certainly require pygame consideration, and is not useful for python console testing
        pass

    def find_all_sets(
            self):  # a method i considered, where instead of you choosing cards and it gets validated, all valid sets are already displayed - not implemented
        pass

    def display_set(self, valid, ddz_set):  # shows result of above method - used in conjunction with above
        if valid:
            return ddz_set
        else:
            return "INVALID SET"

    def play_turn(self, cards, deck):  # removes the cards you have played, and adds them to the pool
        for card in cards:
            self.hand.hand.remove(card)
            deck.pool.append(card)

    def take_damage(self, damage):  # takes away your health
        self.hp -= damage

    def status(self):  # checks if you are alive - returns True if yes, if dead then False
        if self.hp <= 0:
            return False
        else:
            return True

    def apply_gimmick(self, gimmick, deck=None):
        from settings import GIMMICK_VALUES
        if gimmick == "damage_multiplier":
            pass  # effect applied per play in damage_calc
        elif gimmick == "hand_size_up":
            self.hand_size += GIMMICK_VALUES["hand_size_up"]
            if deck:
                for _ in range(GIMMICK_VALUES["hand_size_up"]):
                    if deck.deck:
                        self.hand.hand.append(deck.deck.pop())
                self.hand.hand.sort(key=lambda card: card.numeric_rank())
        elif gimmick == "shuffle_count_up":
            self.bonus_shuffles += GIMMICK_VALUES["shuffle_count_up"]
        self.active_gimmicks.append(gimmick)  # this line must always run
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
    def __init__(self):
        super().__init__()

    def draw_hand(self, deck, size=20):
        for n in range(size):
            self.hand.append(deck.pop())


class Card:
    def __init__(self, suit, value):
        self.suit  = suit
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.value == other.value

    def __hash__(self):
        return hash((self.suit, self.value))

    def numeric_rank(self):
        mapping = {"J": 11, "Q": 12, "K": 13, "A": 14, "2": 15,
                   "Small": 16, "Big": 17}
        if self.value in mapping:
            return mapping[self.value]
        return int(self.value)

class GimmickCard(Card):
    def __init__(self, suit, value, gimmick):
        super().__init__(suit, value)
        self.gimmick = gimmick


class Deck:
    def __init__(self):  # deck is the cards in the deck, pool is the cards that have been placed down for the turn
        self.deck = []
        self.pool = []



    def shuffle(self):  # shuffles deck
        random.shuffle(self.deck)

    def make_deck(self):
        for suit in suits:
            for value in values:
                self.deck.append(Card(suit, value))  # only once, not twice
        self.deck.append(Card("Joker", "Small"))
        self.deck.append(Card("Joker", "Big"))
        self.shuffle()

    def redeck(
            self):  # this is when the cards played for the turn are added back to the deck (im thinking this happens after each turn)
        self.deck += self.pool
        self.pool = []
        self.shuffle()


def validate_set(cards):  # you pick cards, and it finds if it is valid/what kind of set it is - outputs valid, the kind of set, the cards of the set
    ranks = []
    suits_list = []
    for card in cards:
        if card.suit == "Joker":  # ADD THIS CHECK FIRST
            suits_list.append(card.suit)
            continue
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
        suits_list.append(card.suit)
    ranks.sort(key=lambda x: int(x))
    count = Counter(ranks)
    valid = False
    ddz_set = None
    if set(suits_list) == {"Joker"} and len(cards) == 2:
        joker_values = sorted([card.value for card in cards])
        if joker_values == ["Big", "Small"]:
            valid = True
            ddz_set = sets_list[11]
    elif "Joker" in suits_list and len(cards) == 1:
        valid = True
        ddz_set = sets_list[0]  # single
    elif "Joker" in suits_list and len(cards) == 2:
        valid = True
        ddz_set = sets_list[1]  # double (two of same joker)
    elif "Joker" in suits_list:
        pass
    elif len(cards) >= 4 and len(list(count.values())) == 1:
        valid = True
        ddz_set = sets_list[5]
    elif len(cards) == 1:
        valid = True
        ddz_set = sets_list[0]
    elif len(cards) == 2 and list(count.values()) == [2]:
        valid = True
        ddz_set = sets_list[1]
    elif len(cards) == 3 and list(count.values()) == [3]:
        valid = True
        ddz_set = sets_list[2]
    elif len(cards) == 4 and (list(count.values()) == [1, 3] or list(count.values()) == [3, 1]):
        valid = True
        ddz_set = sets_list[3]
    elif len(cards) == 5 and (list(count.values()) == [2, 3] or list(count.values()) == [3, 2]):
        valid = True
        ddz_set = sets_list[4]
    elif 5 <= len(cards) == len(set(ranks)) and "15" not in ranks:
        consecutive = True
        for idx in range(0, len(ranks) - 1):
            if int(ranks[idx]) != int(ranks[idx + 1]) - 1:
                consecutive = False
                break
        if consecutive:
            valid = True
            ddz_set = sets_list[6]
    elif len(cards) >= 6 and len(set(ranks)) == len(cards) // 2 and all(x == 2 for x in list(count.values())):
        consecutive = True
        unique_ranks = sorted(list(set(ranks)), key=lambda x: int(x))
        for idx in range(0, len(unique_ranks) - 1):
            if int(unique_ranks[idx]) + 1 != int(unique_ranks[idx + 1]):
                consecutive = False
                break
        if consecutive:
            valid = True
            ddz_set = sets_list[7]
    elif len(cards) >= 6:
        if len(set(ranks)) == len(cards) // 3:
            consecutive = True
            set_list = sorted(list(set(ranks)), key=lambda x: int(x))
            for idx in range(0, len(set_list) - 1):
                if int(set_list[idx]) != int(set_list[idx + 1]) - 1:
                    consecutive = False
                    break
            if consecutive:
                valid = True
                ddz_set = sets_list[8]
    else:
        if len(cards) >= 8 and list(count.values()).count(3) == list(count.values()).count(1) and list(
                count.values()).count(3) + list(count.values()).count(1) == len(count):
            consecutive = True
            triples = [value for value, num in count.items() if num == 3]
            set_list = sorted(list(set(ranks)), key=lambda x: int(x))
            for idx in range(0, len(triples) - 1):
                if int(triples[idx]) != int(triples[idx + 1]) - 1:
                    consecutive = False
                    break
            if consecutive:
                valid = True
                ddz_set = sets_list[9]
        elif len(cards) >= 10 and list(count.values()).count(3) == list(count.values()).count(2) and list(
                count.values()).count(3) + list(count.values()).count(2) == len(count):
            consecutive = True
            triples = [value for value, num in count.items() if num == 3]
            set_list = sorted(list(set(ranks)), key=lambda x: int(x))
            for idx in range(0, len(triples) - 1):
                if int(triples[idx]) != int(triples[idx + 1]) - 1:
                    consecutive = False
                    break
            if consecutive:
                valid = True
                ddz_set = sets_list[10]
    return valid, ddz_set, cards

def damage_calc(cards, ddz_set, damage_mult=1, has_gambling=False):
    card_values = [card.numeric_rank() for card in cards]
    damage = max(card_values) * base_damage_constant[ddz_set] * damage_mult

    roll = None
    if has_gambling:
        roll = random.randint(7, 15) / 10
        damage *= roll

    if ddz_set == "single_straight":
        extra_cards = len(cards) - 5
        if extra_cards > 0:
            damage *= 1 + (extra_cards * 0.10)
    elif ddz_set == "double_straight":
        extra_pairs = (len(cards) // 2) - 3
        if extra_pairs > 0:
            damage *= 1 + (extra_pairs * 0.15)

    return damage, roll