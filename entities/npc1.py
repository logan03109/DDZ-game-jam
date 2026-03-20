# entities/npc1.py
import random

class Boss:
    def __init__(self, config):
        self.hp      = config["hp"]
        self.max_hp  = config["hp"]
        self.name    = config["name"]

    def is_alive(self):
        return self.hp > 0