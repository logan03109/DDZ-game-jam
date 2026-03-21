import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
# data
suits = ["Hearts", "Spades", "Diamonds", "Clubs"]  # suits
values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]  # values, excluding jokers
sets_list = ["single", "double", "triple", "triple+1", "triple+2", "bomb", "single_straight", "double_straight",
        "triple_straight", "triple+1_straight", "triple+2_straight", "jokerbomb"]  # every type of set
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
FPS  = 60
BG_COLOUR   = (15, 20, 40)
CARD_WHITE  = (240, 235, 220)

BOSS_CONFIGS = [
    {
        "name": "Shadow Landlord",
        "hp": 100,
        "hand_size": 10,
        "max_plays": 5,
        "max_shuffles": 3,
        "allowed_sets": [
            "single",
            "double"
        ]
    },
    {
        "name": "Shadow Landlord II",
        "hp": 250,
        "hand_size": 15,
        "max_plays": 5,
        "max_shuffles": 3,
        "allowed_sets": [
            "single",
            "double",
            "triple",
            "triple+1",
            "triple+2",
            "single_straight",
            "double_straight",
        ]
    },
    {
        "name": "Shadow Landlord III",
        "hp": 500,
        "hand_size": 20,
        "max_plays": 5,
        "max_shuffles": 3,
        "allowed_sets": [
            "single",
            "double",
            "triple",
            "triple+1",
            "triple+2",
            "bomb",
            "single_straight",
            "double_straight",
            "triple_straight",
            "triple+1_straight",
            "triple+2_straight",
            "jokerbomb"
        ]
    },
]


gimmicks = ["damage_multiplier", "hand_size_up", "shuffle_count_up"]

GIMMICK_DESCRIPTIONS = {
    "damage_multiplier": "Gamble! Multiply damage by 0.7x to 1.5x",
    "hand_size_up":      "Increase hand size by 3 cards",
    "shuffle_count_up":  "Gain 2 extra shuffles",
}
GIMMICK_VALUES = {
    "hand_size_up":      3,
    "shuffle_count_up":  2,
}

GIMMICK_CARD_CONFIGS = {
    "3": {"effect": "bleed",        "description": "Playing a 3 applies bleed (-10 bonus dmg)"},
    "4": {"effect": "dmg_boost",    "description": "Playing a 4 multiplies damage by 1.5x"},
    "5": {"effect": "plays_up",     "description": "Playing a 5 has 50% chance of +1 play"},
    "6": {"effect": "shuffles_up",  "description": "Playing a 6 has 50% chance of +1 shuffle"},
}

# Font sizes — increase these to scale all text up
FONT_SIZE_SMALL  = 22
FONT_SIZE_NORMAL = 24
FONT_SIZE_UI     = 27
FONT_SIZE_MSG    = 36
FONT_SIZE_TITLE  = 60