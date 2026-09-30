import pygame
import math
import random
from config import WEAPON_TEMPLATES

# ==================== ITEMS ====================
class Item:
    def __init__(self, item_id, item_type, name, x, y):
        self.item_id = item_id
        self.item_type = item_type
        self.name = name
        self.x = x; self.y = y
        self.is_picked_up = False
        self.bob_timer = random.uniform(0, math.pi*2)

class Weapon(Item):
    def __init__(self, item_id, name, x, y, bonus_attack, attack_range, cooldown, weapon_class, color, spread=0.0, skill_name=None):
        super().__init__(item_id, "WEAPON", name, x, y)
        self.bonus_attack = bonus_attack
        self.attack_range = attack_range
        self.cooldown = cooldown
        self.weapon_class = weapon_class
        self.color = color
        self.spread = spread
        self.skill_name = skill_name

class HealthPotion(Item):
    def __init__(self, item_id, x, y, heal_amount=50.0):
        super().__init__(item_id, "POTION", "Bình Máu", x, y)
        self.heal_amount = heal_amount

def generate_random_weapon(item_id, map_size):
    x = random.uniform(100, map_size-100)
    y = random.uniform(100, map_size-100)
    w = random.choice(WEAPON_TEMPLATES)
    return Weapon(item_id, w["name"], x, y, w["atk"], w["rng"], w["cd"], w["cls"], w["col"], w["spread"], w.get("skill"))
