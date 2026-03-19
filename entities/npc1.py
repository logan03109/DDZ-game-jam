# entities/npc1.py
import random

class Boss:
    def __init__(self):
        self.hp      = 500
        self.max_hp  = 500
        self.name    = "Shadow Landlord"

    def is_alive(self):
        return self.hp > 0