import json
import os
from enum import Enum

# ==================== CONSTANTS ====================
MAP_SIZE   = 8000
POP_SIZE   = 300
MAX_FRAMES = 6000
SCREEN_W   = 1100
SCREEN_H   = 800
UI_WIDTH   = 310
FPS        = 60
MAX_PARTICLES = 1200

class HeroClass(Enum):
    WARRIOR  = "Warrior"
    RANGER   = "Ranger"
    MAGE     = "Mage"
    ASSASSIN = "Assassin"
    TANK     = "Tank"

# Global data holders
HERO_CLASS_CONFIG = {}
WEAPON_TEMPLATES = []
NAMES_DATA = {"first_names": [], "last_names": []}

def load_data():
    global HERO_CLASS_CONFIG, WEAPON_TEMPLATES, NAMES_DATA
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    
    # Load Hero Config
    try:
        with open(os.path.join(data_dir, "hero_config.json"), "r", encoding="utf-8") as f:
            raw_cfg = json.load(f)
            # Reconstruct dict with HeroClass Enum as keys
            for hc in HeroClass:
                if hc.value in raw_cfg:
                    cfg = raw_cfg[hc.value]
                    # Convert color lists back to tuples
                    cfg["color"] = tuple(cfg["color"])
                    cfg["glow"] = tuple(cfg["glow"])
                    HERO_CLASS_CONFIG[hc] = cfg
    except Exception as e:
        print("Error loading hero_config.json:", e)

    # Load Weapons
    try:
        with open(os.path.join(data_dir, "weapons.json"), "r", encoding="utf-8") as f:
            WEAPON_TEMPLATES = json.load(f)
            for w in WEAPON_TEMPLATES:
                if "col" in w:
                    w["col"] = tuple(w["col"])
    except Exception as e:
        print("Error loading weapons.json:", e)

    # Load Names
    try:
        with open(os.path.join(data_dir, "names.json"), "r", encoding="utf-8") as f:
            NAMES_DATA = json.load(f)
    except Exception as e:
        print("Error loading names.json:", e)

# Load data immediately on import
load_data()
