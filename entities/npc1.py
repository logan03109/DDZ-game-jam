# entities/npc1.py
import random

class Boss:
    def __init__(self, config):
        self.hp      = config["hp"]
        self.max_hp  = config["hp"]
        self.name    = config["name"]
        self.bleed_stacks = 0
        self.damage_reduction = config.get("damage_reduction", 0)
        self.regen = config.get("regen", 0)

    def is_alive(self):
        return self.hp > 0