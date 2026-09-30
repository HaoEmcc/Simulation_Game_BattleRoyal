import pygame
import math
import random
import sys
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

# ==================== HERO CLASSES ====================
class HeroClass(Enum):
    WARRIOR  = "Warrior"
    RANGER   = "Ranger"
    MAGE     = "Mage"
    ASSASSIN = "Assassin"
    TANK     = "Tank"

HERO_CLASS_CONFIG = {
    HeroClass.WARRIOR:  {"color": (220, 75,  40),  "glow": (255,120, 60), "hp_mult": 1.4, "spd_mult": 1.1, "sides": 5, "skill": "Whirlwind",    "skill_cd": 300, "size": 12},
    HeroClass.RANGER:   {"color": ( 50,195,  80),  "glow": ( 90,255,120), "hp_mult": 0.9, "spd_mult": 1.4, "sides": 4, "skill": "Eagle Eye",     "skill_cd": 250, "size": 10},
    HeroClass.MAGE:     {"color": (155, 55, 220),  "glow": (200, 90,255), "hp_mult": 0.7, "spd_mult": 1.0, "sides": 8, "skill": "Arcane Nova",   "skill_cd": 350, "size": 11},
    HeroClass.ASSASSIN: {"color": ( 55, 55,  80),  "glow": (140,140,200), "hp_mult": 0.8, "spd_mult": 1.8, "sides": 3, "skill": "Shadow Dash",   "skill_cd": 200, "size":  9},
    HeroClass.TANK:     {"color": (195,165,  25),  "glow": (255,220, 60), "hp_mult": 1.8, "spd_mult": 0.65,"sides": 6, "skill": "Iron Skin",     "skill_cd": 400, "size": 14},
}

# ==================== WEAPONS ====================
WEAPON_TEMPLATES = [
    # MELEE (9)
    {"name": "Dao Găm",        "atk":10,  "rng": 22,   "cd": 8,  "cls":"MELEE",  "col":(180,180,210), "spread":0.0,  "skill":"Quick Strike"},
    {"name": "Kiếm Thép",      "atk":22,  "rng": 33,   "cd":15,  "cls":"MELEE",  "col":(200,215,235), "spread":0.0,  "skill":"Cleave"},
    {"name": "Rìu Chiến",      "atk":52,  "rng": 27,   "cd":40,  "cls":"MELEE",  "col":(155,100, 50), "spread":0.0,  "skill":"Shockwave"},
    {"name": "Giáo Dài",       "atk":28,  "rng": 56,   "cd":24,  "cls":"MELEE",  "col":(215,185,145), "spread":0.0,  "skill":"Lunge"},
    {"name": "Dual Blades",    "atk":16,  "rng": 20,   "cd": 7,  "cls":"MELEE",  "col":( 90,215,215), "spread":0.0,  "skill":"Double Strike"},
    {"name": "War Hammer",     "atk":78,  "rng": 30,   "cd":52,  "cls":"MELEE",  "col":(120,120,130), "spread":0.0,  "skill":"Quake"},
    {"name": "Flail",          "atk":38,  "rng": 46,   "cd":28,  "cls":"MELEE",  "col":(185,145, 60), "spread":0.0,  "skill":"Whirlwind"},
    {"name": "Katana",         "atk":26,  "rng": 28,   "cd": 6,  "cls":"MELEE",  "col":(255,255,255), "spread":0.0,  "skill":"Blink Strike"},
    {"name": "Scythe",         "atk":42,  "rng": 38,   "cd":35,  "cls":"MELEE",  "col":(120, 40, 40), "spread":0.0,  "skill":"Lifesteal Strike"},
    {"name": "Energy Sword",   "atk":55,  "rng": 26,   "cd":22,  "cls":"MELEE",  "col":(50, 255, 100),"spread":0.0,  "skill":"Laser Beam"},
    {"name": "Power Gauntlets","atk":60,  "rng": 18,   "cd":45,  "cls":"MELEE",  "col":(200, 100, 20),"spread":0.0,  "skill":"Quake"},

    # RANGED (11)
    {"name": "Cung Ngắn",      "atk":18,  "rng":185,   "cd":20,  "cls":"RANGED", "col":(140, 70, 20), "spread":0.12, "skill":"Volley"},
    {"name": "Nỏ Thần",        "atk":36,  "rng":245,   "cd":44,  "cls":"RANGED", "col":(105, 52, 22), "spread":0.06, "skill":"Piercing Shot"},
    {"name": "Súng Tỉa",       "atk":92,  "rng":390,   "cd":88,  "cls":"RANGED", "col":( 50, 52, 62), "spread":0.01, "skill":"Sniper Mark"},
    {"name": "Shotgun",        "atk":46,  "rng":115,   "cd":50,  "cls":"RANGED", "col":(170,170,175), "spread":0.40, "skill":"Explosive Shot"},
    {"name": "Pistol",         "atk":24,  "rng":158,   "cd":18,  "cls":"RANGED", "col":(135,135,155), "spread":0.08, "skill":"Rapid Fire"},
    {"name": "Grenade Launcher","atk":68, "rng":225,   "cd":72,  "cls":"RANGED", "col":( 85,125, 62), "spread":0.05, "skill":"Grenade"},
    {"name": "Minigun",        "atk":12,  "rng":175,   "cd": 4,  "cls":"RANGED", "col":(100,100,100), "spread":0.25, "skill":"Rapid Fire"},
    {"name": "Laser Rifle",    "atk":30,  "rng":350,   "cd":25,  "cls":"RANGED", "col":(255, 50, 50), "spread":0.0,  "skill":"Laser Beam"},
    {"name": "Poison Dart",    "atk":15,  "rng":160,   "cd":16,  "cls":"RANGED", "col":( 50,200, 50), "spread":0.04, "skill":"Poison Cloud"},
    {"name": "Boomerang",      "atk":28,  "rng":220,   "cd":30,  "cls":"RANGED", "col":(180,120, 50), "spread":0.08, "skill":"Tornado"},
    
    # MAGIC (8)
    {"name": "Trượng Phép",    "atk":28,  "rng":162,   "cd":32,  "cls":"MAGIC",  "col":(150,  0,215), "spread":0.08, "skill":"Arcane Bolt"},
    {"name": "Magic Staff",    "atk":44,  "rng":215,   "cd":46,  "cls":"MAGIC",  "col":( 82, 62,205), "spread":0.04, "skill":"Chain Bolt"},
    {"name": "Fire Wand",      "atk":24,  "rng":135,   "cd":26,  "cls":"MAGIC",  "col":(255, 82, 32), "spread":0.10, "skill":"Fireball"},
    {"name": "Thunder Spear",  "atk":52,  "rng":285,   "cd":62,  "cls":"MAGIC",  "col":(105,205,255), "spread":0.03, "skill":"Chain Lightning"},
    {"name": "Ice Wand",       "atk":22,  "rng":145,   "cd":28,  "cls":"MAGIC",  "col":(100,255,255), "spread":0.05, "skill":"Frost Nova"},
    {"name": "Venom Staff",    "atk":35,  "rng":195,   "cd":40,  "cls":"MAGIC",  "col":( 80,255, 80), "spread":0.15, "skill":"Poison Cloud"},
    {"name": "Meteor Staff",   "atk":40,  "rng":320,   "cd":75,  "cls":"MAGIC",  "col":(255,100,  0), "spread":0.0,  "skill":"Meteor Strike"},
    {"name": "Necro Tome",     "atk":15,  "rng":250,   "cd":20,  "cls":"MAGIC",  "col":(100, 30,100), "spread":0.05, "skill":"Lifesteal Strike"},

    # SPECIAL (3)
    {"name": "Plasma Cannon",  "atk":120, "rng":400,   "cd":110, "cls":"RANGED", "col":( 50, 50,255), "spread":0.0,  "skill":"Meteor Strike"},
    {"name": "Mjolnir",        "atk":85,  "rng": 40,   "cd":55,  "cls":"MELEE",  "col":(150,200,255), "spread":0.0,  "skill":"Chain Lightning"},
    {"name": "Kiến Hào",       "atk":150, "rng":15000, "cd":120, "cls":"RANGED", "col":(255,255,248), "spread":0.0,  "skill":"Sniper Mark"},
]

# ==================== UTILITY ====================
def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (int(c1[0]+(c2[0]-c1[0])*t), int(c1[1]+(c2[1]-c1[1])*t), int(c1[2]+(c2[2]-c1[2])*t))

def poly_points(cx, cy, radius, sides, angle_off=0.0):
    pts = []
    for i in range(sides):
        a = 2*math.pi*i/sides + angle_off
        pts.append((cx + radius*math.cos(a), cy + radius*math.sin(a)))
    return pts

def draw_poly(surface, color, cx, cy, radius, sides, angle_off=0.0, width=0):
    pts = poly_points(cx, cy, radius, sides, angle_off)
    if len(pts) >= 3:
        pygame.draw.polygon(surface, color, pts, width)

def draw_star(surface, color, cx, cy, r_out, r_in, points=6, angle_off=0.0, width=0):
    pts = []
    for i in range(points*2):
        a = math.pi*i/points + angle_off
        r = r_out if i%2==0 else r_in
        pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    if len(pts) >= 3:
        pygame.draw.polygon(surface, color, pts, width)

def draw_glow(surface, color, cx, cy, radius, intensity=100):
    if radius <= 0:
        return
    sz = radius*2 + 6
    gs = pygame.Surface((sz, sz), pygame.SRCALPHA)
    steps = max(4, radius // 5)
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(intensity * (1 - i/steps)**0.6 * 0.55)
        a = max(0, min(255, a))
        if r > 0:
            pygame.draw.circle(gs, (*color[:3], a), (sz//2, sz//2), r)
    surface.blit(gs, (cx - sz//2, cy - sz//2), special_flags=pygame.BLEND_ADD)

def generate_random_name():
    F = ["Shadow","Blaze","Viper","Phantom","Hunter","Storm","Titan","Raptor",
         "Slayer","Ghost","Phoenix","Frost","Reaper","Dragon","Falcon","Iron",
         "Silver","Thunder","Nexus","Zenith","Apex","Vortex","Saber","Razor",
         "Spectre","Rogue","Omega","Alpha","Havoc","Echo","Nova","Crimson",
         "Dark","Steel","Void","Ember","Ash","Jade","Fury","Neon","Blitz","Arc"]
    L = ["Knight","Blade","Striker","Wolf","Hawk","Fang","Fury","Claw",
         "Soul","Heart","Walker","Chaser","Breaker","Master","Legend",
         "Born","Bane","Lord","King","Mark","Edge","Rise","Fall","Forge"]
    return f"{random.choice(F)} {random.choice(L)}"

# ==================== PARTICLES ====================
class BloodParticle:
    __slots__ = ['x','y','vx','vy','life','max_life','size']
    def __init__(self, x, y):
        self.x, self.y = x, y
        a = random.uniform(0, math.pi*2)
        s = random.uniform(1.5, 5.5)
        self.vx, self.vy = math.cos(a)*s, math.sin(a)*s
        self.life = self.max_life = random.randint(14, 28)
        self.size = random.uniform(2.0, 5.0)
    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += 0.18; self.vx *= 0.94
        self.life -= 1
    def draw(self, surface, cam):
        if not cam.is_visible(self.x, self.y): return
        sx, sy = cam.world_to_screen(self.x, self.y)
        r_ratio = self.life / self.max_life
        col = (int(180*r_ratio), 0, 0)
        sz = max(1, int(self.size * r_ratio))
        pygame.draw.circle(surface, col, (sx, sy), sz)

class SparkParticle:
    __slots__ = ['x','y','vx','vy','life','max_life','color','length']
    def __init__(self, x, y, color=(255,220,50)):
        self.x, self.y = x, y
        a = random.uniform(0, math.pi*2)
        s = random.uniform(3.0, 9.0)
        self.vx, self.vy = math.cos(a)*s, math.sin(a)*s
        self.life = self.max_life = random.randint(8, 20)
        self.color = color
        self.length = random.uniform(3.0, 9.0)
    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vx *= 0.87; self.vy *= 0.87
        self.life -= 1
    def draw(self, surface, cam):
        if not cam.is_visible(self.x, self.y): return
        sx, sy = cam.world_to_screen(self.x, self.y)
        ratio = self.life / self.max_life
        ex = int(sx - self.vx * self.length)
        ey = int(sy - self.vy * self.length)
        c = lerp_color(self.color, (255,255,255), ratio)
        w = max(1, int(2*ratio))
        pygame.draw.line(surface, c, (sx,sy), (ex,ey), w)

class SmokeParticle:
    __slots__ = ['x','y','vx','vy','life','max_life','size','color']
    def __init__(self, x, y, color=(80,80,100)):
        self.x, self.y = x, y
        self.vx = random.uniform(-0.6, 0.6)
        self.vy = random.uniform(-1.6, -0.3)
        self.life = self.max_life = random.randint(30, 65)
        self.size = random.uniform(8.0, 22.0)
        self.color = color
    def update(self):
        self.x += self.vx; self.y += self.vy
        self.size += 0.35
        self.life -= 1
    def draw(self, surface, cam):
        if not cam.is_visible(self.x, self.y, self.size): return
        sx, sy = cam.world_to_screen(self.x, self.y)
        a = int(120 * (self.life/self.max_life))
        sz = int(self.size)
        gs = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*self.color, a), (sz+1,sz+1), sz)
        surface.blit(gs, (sx-sz, sy-sz))

class ExplosionParticle:
    __slots__ = ['x','y','vx','vy','life','max_life','color','size']
    def __init__(self, x, y, color=(255,140,20)):
        self.x, self.y = x, y
        a = random.uniform(0, math.pi*2)
        s = random.uniform(2.0, 10.0)
        self.vx, self.vy = math.cos(a)*s, math.sin(a)*s
        self.life = self.max_life = random.randint(18, 38)
        self.color = color
        self.size = random.uniform(3.0, 9.0)
    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vx *= 0.91; self.vy *= 0.91; self.vy += 0.12
        self.size *= 0.97
        self.life -= 1
    def draw(self, surface, cam):
        if not cam.is_visible(self.x, self.y): return
        sx, sy = cam.world_to_screen(self.x, self.y)
        ratio = self.life / self.max_life
        c = lerp_color((30,30,30), self.color, ratio)
        sz = max(1, int(self.size))
        pygame.draw.circle(surface, c, (sx, sy), sz)

class GlowTrail:
    __slots__ = ['x','y','life','max_life','color','size']
    def __init__(self, x, y, color, size=8):
        self.x, self.y = x, y
        self.life = self.max_life = random.randint(10, 22)
        self.color = color
        self.size = size
    def update(self):
        self.life -= 2
    def draw(self, surface, cam):
        if not cam.is_visible(self.x, self.y): return
        sx, sy = cam.world_to_screen(self.x, self.y)
        ratio = self.life / self.max_life
        sz = max(1, int(self.size * ratio))
        a = int(180 * ratio)
        gs = pygame.Surface((sz*2+2,sz*2+2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*self.color, a), (sz+1,sz+1), sz)
        surface.blit(gs, (sx-sz, sy-sz), special_flags=pygame.BLEND_ADD)

class HealBurst:
    __slots__ = ['x','y','radius','life','max_life','rays']
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 5
        self.life = self.max_life = 45
        self.rays = [(random.uniform(0,math.pi*2), random.uniform(22,55)) for _ in range(10)]
    def update(self):
        self.radius += 3.5
        self.life -= 1
    def draw(self, surface, cam):
        if not cam.is_visible(self.x, self.y, self.radius+10): return
        sx, sy = cam.world_to_screen(self.x, self.y)
        ratio = self.life / self.max_life
        a = int(220 * ratio)
        r = int(self.radius)
        if r > 0:
            rsurf = pygame.Surface((r*2+4,r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(rsurf, (50,255,100,a), (r+2,r+2), r, 2)
            surface.blit(rsurf, (sx-r-2, sy-r-2), special_flags=pygame.BLEND_ADD)
        for angle, length in self.rays:
            ex = int(sx + math.cos(angle)*length*(1-ratio)*1.5)
            ey = int(sy + math.sin(angle)*length*(1-ratio)*1.5)
            pygame.draw.line(surface, (80,255,130,a//2 if False else 80), (sx,sy), (ex,ey), 1)

class LightningParticle:
    __slots__ = ['points','color','life','max_life']
    def __init__(self, x1, y1, x2, y2, color=(100,200,255)):
        self.color = color
        self.life = self.max_life = 16
        segs = 8
        pts = [(x1,y1)]
        for i in range(1, segs):
            t = i/segs
            mx = x1+(x2-x1)*t + random.uniform(-22,22)
            my = y1+(y2-y1)*t + random.uniform(-22,22)
            pts.append((mx,my))
        pts.append((x2,y2))
        self.points = pts
    def update(self):
        self.life -= 1
    def draw(self, surface, cam):
        ratio = self.life/self.max_life
        w = max(1, int(3*ratio))
        for i in range(len(self.points)-1):
            p1,p2 = self.points[i], self.points[i+1]
            if cam.is_visible(p1[0],p1[1],30) or cam.is_visible(p2[0],p2[1],30):
                s1 = cam.world_to_screen(*p1)
                s2 = cam.world_to_screen(*p2)
                pygame.draw.line(surface, self.color, s1, s2, w)
                pygame.draw.line(surface, (255,255,255), s1, s2, 1)

class MeteorWarning:
    __slots__ = ['x','y','radius','life','max_life']
    def __init__(self, x, y, radius, delay):
        self.x, self.y = x, y
        self.radius = radius
        self.max_life = self.life = delay
    def update(self):
        self.life -= 1
    def draw(self, surface, cam):
        if not cam.is_visible(self.x, self.y, self.radius): return
        sx, sy = cam.world_to_screen(self.x, self.y)
        ratio = 1.0 - (self.life / max(1,self.max_life))
        a = 150
        surf = pygame.Surface((int(self.radius*2+4), int(self.radius*2+4)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255,50,50,50), (int(self.radius+2), int(self.radius+2)), int(self.radius))
        pygame.draw.circle(surf, (255,0,0,200), (int(self.radius+2), int(self.radius+2)), int(self.radius), 2)
        pygame.draw.circle(surf, (255,200,0,150), (int(self.radius+2), int(self.radius+2)), int(self.radius * ratio), 2)
        surface.blit(surf, (sx-self.radius-2, sy-self.radius-2))

class WhirlwindParticle:
    __slots__ = ['cx','cy','angle','radius','angular_speed','life','max_life','color','size']
    def __init__(self, cx, cy, color=(200,100,50)):
        self.cx, self.cy = cx, cy
        self.angle = random.uniform(0, math.pi*2)
        self.radius = random.uniform(20, 85)
        self.angular_speed = random.uniform(0.15,0.38)*(1 if random.random()<0.5 else -1)
        self.life = self.max_life = random.randint(22, 45)
        self.color = color
        self.size = random.uniform(3.0, 8.0)
    def update(self):
        self.angle += self.angular_speed
        self.radius *= 0.97
        self.life -= 1
    def draw(self, surface, cam):
        px = self.cx + math.cos(self.angle)*self.radius
        py = self.cy + math.sin(self.angle)*self.radius
        if not cam.is_visible(px, py): return
        sx, sy = cam.world_to_screen(px, py)
        ratio = self.life/self.max_life
        c = lerp_color((50,50,50), self.color, ratio)
        sz = max(1, int(self.size*ratio))
        pygame.draw.circle(surface, c, (sx,sy), sz)

class ShieldParticle:
    __slots__ = ['cx','cy','angle','life','max_life','color','radius']
    def __init__(self, cx, cy, color=(255,220,50)):
        self.cx, self.cy = cx, cy
        self.angle = random.uniform(0, math.pi*2)
        self.life = self.max_life = random.randint(18, 35)
        self.color = color
        self.radius = random.uniform(14, 28)
    def update(self):
        self.angle += 0.12
        self.life -= 1
    def draw(self, surface, cam):
        px = self.cx + math.cos(self.angle)*self.radius
        py = self.cy + math.sin(self.angle)*self.radius
        if not cam.is_visible(px, py): return
        sx, sy = cam.world_to_screen(px, py)
        ratio = self.life/self.max_life
        sz = max(1, int(5*ratio))
        pygame.draw.circle(surface, self.color, (sx,sy), sz)

class DamageText:
    __slots__ = ['x','y','text','color','life','max_life']
    def __init__(self, x, y, text, color=(255,60,60)):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.life = self.max_life = 70
    def update(self):
        self.y -= 0.7
        self.life -= 1
    def draw(self, surface, cam, font):
        if not cam.is_visible(self.x, self.y, 60): return
        sx, sy = cam.world_to_screen(self.x, self.y)
        ratio = self.life/self.max_life
        surf = font.render(self.text, True, self.color)
        surf.set_alpha(int(255*ratio))
        surface.blit(surf, (sx - surf.get_width()//2, sy))

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

# ==================== OBSTACLES ====================
class Obstacle:
    def __init__(self, x, y, w, h, obs_type="ROCK"):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.obs_type = obs_type
        self._gen_visual()

    def _gen_visual(self):
        if self.obs_type == "ROCK":
            b = random.randint(0,30)
            self.color = (70+b, 70+b, 82+random.randint(0,20))
            cx, cy = self.w/2, self.h/2
            r = min(self.w,self.h)/2
            sides = random.randint(5,9)
            self.poly_pts = []
            for i in range(sides):
                a = 2*math.pi*i/sides + random.uniform(-0.3,0.3)
                d = r*random.uniform(0.6,1.0)
                self.poly_pts.append((cx+math.cos(a)*d, cy+math.sin(a)*d))
        elif self.obs_type == "TREE":
            g = random.randint(0,30)
            self.color = (20+random.randint(0,15), 90+g, 20+random.randint(0,12))
            self.trunk_color = (82, 52, 22)
            n = 3
            self.leaf_radii   = [random.randint(int(self.w*0.38), int(self.w*0.62)) for _ in range(n)]
            self.leaf_offsets = [(random.uniform(-7,7), random.uniform(-8,2)) for _ in range(n)]
            self.poly_pts = None
        else:  # WALL
            b = random.randint(0,18)
            self.color = (92+b, 82+b, 72+b)
            self.poly_pts = None

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def collides_point(self, px, py, radius=10):
        cx = max(self.x, min(px, self.x+self.w))
        cy = max(self.y, min(py, self.y+self.h))
        return math.hypot(px-cx, py-cy) < radius

    def blocks_line(self, x1, y1, x2, y2):
        rect = self.get_rect()
        for t in (0.2,0.4,0.5,0.6,0.8):
            if rect.collidepoint(x1+(x2-x1)*t, y1+(y2-y1)*t):
                return True
        return False

    def draw(self, surface, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        if self.obs_type == "TREE":
            tw = max(4, self.w//5)
            tx = sx + self.w//2 - tw//2
            pygame.draw.rect(surface, (10,12,16), (tx+2, sy+self.h//2+2, tw, self.h//2))
            pygame.draw.rect(surface, self.trunk_color, (tx, sy+self.h//2, tw, self.h//2))
            lcx, lcy = sx+self.w//2, sy+self.h//3
            for i,(r,(ox,oy)) in enumerate(zip(self.leaf_radii, self.leaf_offsets)):
                shade = i*8
                lc = (min(255,self.color[0]+shade), min(255,self.color[1]+shade), min(255,self.color[2]+shade))
                pygame.draw.circle(surface, (8,10,14), (lcx+int(ox)+3, lcy+int(oy)+3), r)
                pygame.draw.circle(surface, lc, (lcx+int(ox), lcy+int(oy)), r)
                pygame.draw.circle(surface, (min(255,lc[0]+55),min(255,lc[1]+65),min(255,lc[2]+55)),
                                   (lcx+int(ox)-r//3, lcy+int(oy)-r//3), max(2,r//4))
        elif self.obs_type == "ROCK" and self.poly_pts:
            shadow = [(sx+p[0]+5, sy+p[1]+5) for p in self.poly_pts]
            if len(shadow)>=3: pygame.draw.polygon(surface, (8,10,14), shadow)
            pts = [(sx+p[0], sy+p[1]) for p in self.poly_pts]
            if len(pts)>=3:
                pygame.draw.polygon(surface, self.color, pts)
                hl = (min(255,self.color[0]+55), min(255,self.color[1]+55), min(255,self.color[2]+65))
                pygame.draw.polygon(surface, hl, pts, 1)
                inner = [(sx+p[0]*0.65+self.w*0.18, sy+p[1]*0.65+self.h*0.18) for p in self.poly_pts[:3]]
                if len(inner)>=3: pygame.draw.polygon(surface, hl, inner, 1)
        else:  # WALL
            pygame.draw.rect(surface, (8,10,14), (sx+5, sy+5, self.w, self.h))
            pygame.draw.rect(surface, self.color, (sx, sy, self.w, self.h))
            bh = 10
            for row in range(self.h//bh+1):
                by = sy+row*bh
                off = (row%2)*14
                for bx_off in range(-off, self.w+28, 22):
                    bx = sx+bx_off
                    dc = (max(0,self.color[0]-28),max(0,self.color[1]-28),max(0,self.color[2]-28))
                    pygame.draw.line(surface, dc, (bx,by),(bx+20,by),1)
                pygame.draw.line(surface,(max(0,self.color[0]-18),max(0,self.color[1]-18),max(0,self.color[2]-18)),(sx,by),(sx+self.w,by),1)
            hl = (min(255,self.color[0]+55),min(255,self.color[1]+55),min(255,self.color[2]+60))
            pygame.draw.rect(surface, hl, (sx,sy,self.w,3))
            pygame.draw.rect(surface,(min(255,self.color[0]+30),min(255,self.color[1]+30),min(255,self.color[2]+30)),(sx,sy,self.w,self.h),1)

def generate_obstacles(map_size, count=120):
    obstacles = []
    attempts = 0
    while len(obstacles) < count and attempts < count*5:
        attempts += 1
        ot = random.choice(["ROCK","ROCK","TREE","TREE","WALL"])
        if ot=="WALL":
            w = random.randint(80,200); h = random.randint(15,25)
            if random.random()<0.5: w,h=h,w
        elif ot=="TREE":
            s = random.randint(28,52); w,h=s,s
        else:
            w=random.randint(35,82); h=random.randint(35,82)
        x=random.uniform(120,map_size-120-w)
        y=random.uniform(120,map_size-120-h)
        cx,cy=map_size/2,map_size/2
        if math.hypot(x+w/2-cx,y+h/2-cy)<220: continue
        overlap=False
        for obs in obstacles:
            if abs(obs.x-x)<max(obs.w,w)+25 and abs(obs.y-y)<max(obs.h,h)+25:
                overlap=True; break
        if not overlap:
            obstacles.append(Obstacle(x,y,w,h,ot))
    return obstacles

# ==================== PROJECTILE ====================
class Projectile:
    def __init__(self, x, y, tx, ty, damage, shooter, color, speed=9.5, proj_type="NORMAL"):
        self.x, self.y = x, y
        self.damage = damage
        self.shooter = shooter
        self.color = color
        self.hitbox_radius = 5
        self.proj_type = proj_type
        self.trail = []
        self.max_trail = 7
        self.pulse = 0.0
        dx, dy = tx-x, ty-y
        dist = math.hypot(dx,dy)
        if dist>0:
            self.vx, self.vy = (dx/dist)*speed, (dy/dist)*speed
        else:
            self.vx, self.vy = speed, 0
        self.life = 110

    def step(self):
        self.trail.append((self.x,self.y))
        if len(self.trail)>self.max_trail: self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.pulse += 0.32

    def draw(self, surface, cam):
        if self.proj_type == "LASER":
            if not self.trail: return
            tx0, ty0 = self.trail[0]
            if cam.is_visible(self.x, self.y) or cam.is_visible(tx0, ty0):
                sx, sy = cam.world_to_screen(self.x, self.y)
                sx0, sy0 = cam.world_to_screen(tx0, ty0)
                pygame.draw.line(surface, self.color, (sx0,sy0), (sx,sy), 4)
                pygame.draw.line(surface, (255,255,255), (sx0,sy0), (sx,sy), 2)
                draw_glow(surface, self.color, sx, sy, 15, 100)
            return

        for i,(tx,ty) in enumerate(self.trail):
            if cam.is_visible(tx,ty):
                sx,sy = cam.world_to_screen(tx,ty)
                ratio = i/max(1,len(self.trail))
                sz = max(1,int(self.hitbox_radius*ratio*0.65))
                c = lerp_color((15,15,18), self.color, ratio*0.5)
                pygame.draw.circle(surface, c, (sx,sy), sz)
        if not cam.is_visible(self.x,self.y): return
        sx,sy = cam.world_to_screen(self.x,self.y)
        
        if self.proj_type=="MAGIC":
            pr = self.hitbox_radius + int(2.5*math.sin(self.pulse))
            draw_glow(surface, self.color, sx, sy, pr+10, 90)
            pygame.draw.circle(surface, self.color, (sx,sy), pr)
            pygame.draw.circle(surface, (255,255,255), (sx,sy), max(1,pr//2))
        elif self.proj_type=="EXPLOSIVE":
            pygame.draw.circle(surface,(255,100,20),(sx,sy),self.hitbox_radius+3)
            pygame.draw.circle(surface,(255,200,50),(sx,sy),self.hitbox_radius)
            draw_glow(surface,(255,140,20),sx,sy,self.hitbox_radius+6,70)
        elif self.proj_type=="SNIPER":
            if self.trail:
                tx0,ty0=self.trail[0]
                if cam.is_visible(tx0,ty0):
                    sx0,sy0=cam.world_to_screen(tx0,ty0)
                    pygame.draw.line(surface,self.color,(sx0,sy0),(sx,sy),3)
                    pygame.draw.line(surface,(255,255,255),(sx0,sy0),(sx,sy),1)
            pygame.draw.circle(surface,(255,255,200),(sx,sy),4)
            draw_glow(surface,(255,255,180),sx,sy,8,80)
        else:
            if self.trail:
                tx0,ty0=self.trail[0]
                if cam.is_visible(tx0,ty0):
                    sx0,sy0=cam.world_to_screen(tx0,ty0)
                    pygame.draw.line(surface,lerp_color((0,0,0),self.color,0.5),(sx0,sy0),(sx,sy),2)
            pygame.draw.circle(surface,self.color,(sx,sy),self.hitbox_radius)
            pygame.draw.circle(surface,(255,255,255),(sx,sy),2)

# ==================== CAMERA ====================
class Camera:
    def __init__(self, screen_w, screen_h, map_size):
        self.x=0.0; self.y=0.0
        self.screen_w=screen_w; self.screen_h=screen_h
        self.map_size=map_size
        self.speed=18.0
        self.following=None
    def center_on(self, tx, ty, smooth=False):
        ttx=tx-self.screen_w/2; tty=ty-self.screen_h/2
        if smooth:
            self.x+=(ttx-self.x)*0.1; self.y+=(tty-self.y)*0.1
        else:
            self.x=ttx; self.y=tty
        self._clamp()
    def move(self,dx,dy):
        self.x+=dx*self.speed; self.y+=dy*self.speed
        self.following=None; self._clamp()
    def _clamp(self):
        self.x=max(0,min(self.x,self.map_size-self.screen_w))
        self.y=max(0,min(self.y,self.map_size-self.screen_h))
    def world_to_screen(self,wx,wy):
        return int(wx-self.x), int(wy-self.y)
    def is_visible(self,wx,wy,margin=65):
        return (-margin<wx-self.x<self.screen_w+margin and
                -margin<wy-self.y<self.screen_h+margin)
    def is_rect_visible(self,rx,ry,rw,rh,margin=65):
        return not (rx+rw<self.x-margin or rx>self.x+self.screen_w+margin or
                    ry+rh<self.y-margin or ry>self.y+self.screen_h+margin)

# ==================== HERO ====================
class Hero:
    def __init__(self, hero_id):
        self.hero_id = hero_id
        self.name = generate_random_name()
        self.hero_class = random.choice(list(HeroClass))
        cfg = HERO_CLASS_CONFIG[self.hero_class]

        base_hp = random.randint(100,145)
        self.max_hp = int(base_hp * cfg["hp_mult"])
        self.hp = float(self.max_hp)
        self.max_stamina = 500
        self.stamina = float(self.max_stamina)

        self.base_attack = random.randint(5,15)
        self.defense = random.randint(1,5)
        self.base_speed = random.uniform(1.2,2.0)*cfg["spd_mult"]
        self.speed = self.base_speed

        self.base_attack_range = 22.0
        self.base_cooldown = 20

        self.x = 0.0; self.y = 0.0
        self.vx = 0.0; self.vy = 0.0
        self.wander_target = None
        self.facing_angle = 0.0
        self.rotation = random.uniform(0, math.pi*2)
        self.rotation_speed = random.uniform(-0.04, 0.04)

        self.equipped_weapon = None
        self.potions_count = 0
        self.kills = 0
        self.damage_dealt = 0
        self.is_alive = True

        self.hit_timer = 0
        self.attack_cooldown = 0
        self.dash_timer = 0
        self.rest_timer = 0
        self.locked_enemy = None

        self.skill_name = cfg["skill"]
        self.skill_cd_max = cfg["skill_cd"]
        self.skill_cd = 0
        self.skill_active = False
        self.skill_timer = 0
        self.shield_active = False
        
        # Debuffs
        self.poison_timer = 0
        self.frost_timer = 0

        self.state_label = "IDLE"
        self.committed_state = "PATROL"
        self.state_commit_timer = 0

        self.color = cfg["color"]
        self.glow_color = cfg["glow"]
        self.shape_sides = cfg["sides"]
        self.hero_size = cfg["size"]

        self.avoid_side = 1 if random.random()<0.5 else -1
        self.personality = {
            "RUN ZONE": random.randint(40,100),
            "HEALING":  random.randint(85,95),
            "FLEEING":  random.randint(30,90),
            "LOOTING":  random.randint(60,85),
            "COMBAT":   random.randint(60,100),
            "RESTING":  random.randint(40,50),
            "PATROL":   random.randint(20,30),
        }
        self.flee_threshold  = random.uniform(0.5,1.1)
        self.heal_threshold  = random.uniform(0.4,0.7)
        self.loot_greed_dist = random.randint(80,180)

    def reset(self, map_size):
        self.name = generate_random_name()
        self.hp = float(self.max_hp)
        self.stamina = float(self.max_stamina)
        self.x = random.uniform(160, map_size-160)
        self.y = random.uniform(160, map_size-160)
        self.vx = 0; self.vy = 0
        self.equipped_weapon = None
        self.potions_count = 0
        self.kills = 0; self.damage_dealt = 0
        self.is_alive = True
        self.hit_timer = 0; self.attack_cooldown = 0
        self.dash_timer = 0; self.wander_target = None
        self.state_label = "IDLE"; self.committed_state = "PATROL"
        self.state_commit_timer = 0
        self.skill_cd = 0; self.skill_active = False
        self.skill_timer = 0; self.shield_active = False
        self.poison_timer = 0; self.frost_timer = 0
        self.locked_enemy = None
        self.rotation = random.uniform(0, math.pi*2)

    def get_total_attack(self):
        return self.base_attack + (self.equipped_weapon.bonus_attack if self.equipped_weapon else 0)

    def get_attack_range(self):
        r = self.equipped_weapon.attack_range if self.equipped_weapon else self.base_attack_range
        if self.skill_active and self.skill_name=="Eagle Eye":
            r *= 2.0
        return r

    def get_cooldown(self):
        cd = self.equipped_weapon.cooldown if self.equipped_weapon else self.base_cooldown
        if self.hero_class == HeroClass.ASSASSIN: cd = max(1, int(cd * 0.8))
        return cd

    def evaluate_threat(self, enemy):
        my_power = self.hp * self.get_total_attack()
        ep = max(1, enemy.hp * enemy.get_total_attack())
        score = my_power / ep
        if enemy.get_attack_range() > self.get_attack_range()*2:
            score *= 0.7
        return score

    def move_towards(self, tx, ty, obstacles=None):
        dx, dy = tx-self.x, ty-self.y
        dist = math.hypot(dx,dy)
        if dist > 0:
            self.facing_angle = math.atan2(dy,dx)
            ba = self.facing_angle
            offs = [0, 0.4*self.avoid_side, -0.4*self.avoid_side,
                    0.8*self.avoid_side, -0.8*self.avoid_side,
                    1.3*self.avoid_side, -1.3*self.avoid_side]
            for off in offs:
                a = ba+off
                nx = self.x + math.cos(a)*self.speed
                ny = self.y + math.sin(a)*self.speed
                if not obstacles or not self._check_col(nx,ny,obstacles):
                    self.vx = nx - self.x; self.vy = ny - self.y
                    self.x, self.y = nx, ny; return
            self.avoid_side *= -1
            self.vx, self.vy = 0, 0

    def move_away(self, tx, ty, obstacles=None):
        dx, dy = self.x-tx, self.y-ty
        dist = math.hypot(dx,dy)
        if dist > 0:
            ba = math.atan2(dy,dx)
            self.facing_angle = ba
            offs = [0, 0.4*self.avoid_side, -0.4*self.avoid_side,
                    0.8*self.avoid_side, -0.8*self.avoid_side,
                    1.3*self.avoid_side, -1.3*self.avoid_side]
            for off in offs:
                a = ba+off
                nx = self.x + math.cos(a)*self.speed
                ny = self.y + math.sin(a)*self.speed
                if not obstacles or not self._check_col(nx,ny,obstacles):
                    self.vx = nx - self.x; self.vy = ny - self.y
                    self.x, self.y = nx, ny; return
            self.avoid_side *= -1
            self.vx, self.vy = 0, 0

    def _check_col(self, px, py, obstacles):
        for obs in obstacles:
            if obs.collides_point(px, py, 11): return True
        return False

    def dash(self):
        if self.stamina>=50 and self.dash_timer<=0:
            self.dash_timer=12; self.stamina-=50; return True
        return False

    def _can_see(self, tx, ty, obstacles):
        for obs in obstacles:
            if obs.blocks_line(self.x,self.y,tx,ty): return False
        return True

    def _find_cover(self, ex, ey, obstacles):
        best, bd = None, 9999
        for obs in obstacles:
            cx,cy = obs.x+obs.w/2, obs.y+obs.h/2
            d = math.hypot(cx-self.x, cy-self.y)
            if d<220 and d<bd: bd=d; best=obs
        return best

    def _nearby_obs(self, obstacles):
        return [o for o in obstacles if abs(o.x-self.x)<260 and abs(o.y-self.y)<260]

    # ---------- SKILL ----------
    def _use_skill(self, app, heroes, nearby_obs):
        if self.skill_cd>0: return
        sk = self.skill_name
        if not sk: return
        self.skill_cd = self.skill_cd_max

        # Existing Skills
        if sk=="Whirlwind":
            for h in heroes:
                if h!=self and h.is_alive:
                    d=math.hypot(self.x-h.x, self.y-h.y)
                    if d<85:
                        dmg=max(1,int(self.get_total_attack()*0.55)-h.defense)
                        h.hp-=dmg; h.hit_timer=8; self.damage_dealt+=dmg
                        app.dmg_texts.append(DamageText(h.x,h.y-20,str(dmg),(255,180,50)))
                        if h.hp<=0:
                            h.is_alive=False; self.kills+=1
                            app.add_kill(self.name,h.name,"Whirlwind ⚔️")
            for _ in range(24): app.particles.append(WhirlwindParticle(self.x,self.y,self.color))

        elif sk=="Eagle Eye":
            if not self.skill_active:
                self.skill_active=True; self.skill_timer=120
                for _ in range(10): app.particles.append(SparkParticle(self.x,self.y,self.glow_color))

        elif sk in ("Arcane Nova","Chain Bolt"):
            for h in heroes:
                if h!=self and h.is_alive:
                    d=math.hypot(self.x-h.x,self.y-h.y)
                    if d<155:
                        dmg=max(1,self.get_total_attack()-h.defense)
                        h.hp-=dmg; h.hit_timer=10; self.damage_dealt+=dmg
                        app.particles.append(LightningParticle(self.x,self.y,h.x,h.y,(180,80,255)))
                        app.dmg_texts.append(DamageText(h.x,h.y-20,str(dmg),(180,80,255)))
                        if h.hp<=0:
                            h.is_alive=False; self.kills+=1
                            app.add_kill(self.name,h.name,f"{sk} 💫")
            for _ in range(18): app.particles.append(ExplosionParticle(self.x,self.y,(160,80,225)))

        elif sk=="Shadow Dash":
            if self.locked_enemy:
                old_x,old_y=self.x,self.y
                a=math.atan2(self.locked_enemy.y-self.y,self.locked_enemy.x-self.x)
                self.x=self.locked_enemy.x-math.cos(a)*22
                self.y=self.locked_enemy.y-math.sin(a)*22
                for _ in range(10):
                    app.particles.append(SmokeParticle(old_x,old_y,(60,60,82)))
                    app.particles.append(GlowTrail(self.x,self.y,self.glow_color,14))

        elif sk=="Iron Skin":
            if not self.skill_active:
                self.shield_active=True; self.skill_active=True; self.skill_timer=185
                for _ in range(20): app.particles.append(ShieldParticle(self.x,self.y,self.glow_color))

        elif sk=="Volley":
            if self.locked_enemy:
                ba=math.atan2(self.locked_enemy.y-self.y,self.locked_enemy.x-self.x)
                dmg=max(1,self.get_total_attack()//2)
                wc=self.equipped_weapon.color if self.equipped_weapon else (140,70,20)
                for i in range(-2,3):
                    a=ba+i*0.16
                    app.projectiles.append(Projectile(self.x,self.y,
                        self.x+math.cos(a)*320,self.y+math.sin(a)*320, dmg,self,wc,10.5,"NORMAL"))

        elif sk=="Fireball":
            if self.locked_enemy:
                app.projectiles.append(Projectile(self.x,self.y,
                    self.locked_enemy.x,self.locked_enemy.y, self.get_total_attack()*2,self,(255,100,20),7.0,"EXPLOSIVE"))

        elif sk=="Chain Lightning":
            if self.locked_enemy:
                targets=[self.locked_enemy]; cur=self.locked_enemy
                for _ in range(3):
                    nb=None; nd=210
                    for h in heroes:
                        if h not in targets and h!=self and h.is_alive:
                            d=math.hypot(cur.x-h.x,cur.y-h.y)
                            if d<nd: nd=d; nb=h
                    if nb: targets.append(nb); cur=nb
                    else: break
                prev=self
                for t in targets:
                    app.particles.append(LightningParticle(prev.x,prev.y,t.x,t.y,(105,205,255)))
                    dmg=max(1,self.get_total_attack()-t.defense)
                    t.hp-=dmg; t.hit_timer=10; self.damage_dealt+=dmg
                    app.dmg_texts.append(DamageText(t.x,t.y-20,str(dmg),(105,205,255)))
                    if t.hp<=0:
                        t.is_alive=False; self.kills+=1
                        app.add_kill(self.name,t.name,"Chain Lightning ⚡")
                    prev=t

        elif sk=="Quake" or sk=="Shockwave":
            r = 108 if sk=="Quake" else 70
            for h in heroes:
                if h!=self and h.is_alive:
                    d=math.hypot(self.x-h.x,self.y-h.y)
                    if d<r:
                        dmg=max(1,int(self.get_total_attack()*0.72)-h.defense)
                        h.hp-=dmg; h.hit_timer=16; self.damage_dealt+=dmg
                        app.dmg_texts.append(DamageText(h.x,h.y-20,str(dmg),(205,155,52)))
                        if h.hp<=0:
                            h.is_alive=False; self.kills+=1
                            app.add_kill(self.name,h.name,sk+" 💥")
            for _ in range(r//4):
                ang=random.uniform(0,math.pi*2)
                if sk=="Quake": app.particles.append(ExplosionParticle(self.x+math.cos(ang)*r*0.5,self.y+math.sin(ang)*r*0.5,(205,155,52)))
                else: app.particles.append(SparkParticle(self.x+math.cos(ang)*50,self.y+math.sin(ang)*50,(220,170,52)))

        elif sk=="Rapid Fire":
            if self.locked_enemy:
                wc=self.equipped_weapon.color if self.equipped_weapon else (135,135,158)
                dmg=max(1,self.get_total_attack()//2)
                for _ in range(3):
                    tx=self.locked_enemy.x+random.uniform(-22,22)
                    ty=self.locked_enemy.y+random.uniform(-22,22)
                    app.projectiles.append(Projectile(self.x,self.y,tx,ty,dmg,self,wc,14.0,"NORMAL"))

        elif sk=="Double Strike":
            if self.locked_enemy:
                d=math.hypot(self.x-self.locked_enemy.x,self.y-self.locked_enemy.y)
                if d<=self.get_attack_range()+12:
                    dmg=max(1,self.get_total_attack()-self.locked_enemy.defense)
                    self.locked_enemy.hp-=dmg*2; self.locked_enemy.hit_timer=12; self.damage_dealt+=dmg*2
                    app.dmg_texts.append(DamageText(self.locked_enemy.x,self.locked_enemy.y-20, f"2×{dmg}!",(255,200,52)))
                    for _ in range(12): app.particles.append(SparkParticle(self.locked_enemy.x,self.locked_enemy.y,(255,200,52)))
                    if self.locked_enemy.hp<=0:
                        self.locked_enemy.is_alive=False; self.kills+=1
                        app.add_kill(self.name,self.locked_enemy.name,"Double Strike ⚔️⚔️")

        elif sk=="Grenade":
            if self.locked_enemy:
                app.projectiles.append(Projectile(self.x,self.y, self.locked_enemy.x,self.locked_enemy.y, self.get_total_attack(),self,(85,125,62),7.5,"EXPLOSIVE"))

        elif sk=="Sniper Mark":
            if self.locked_enemy:
                wc=self.equipped_weapon.color if self.equipped_weapon else (52,52,62)
                # Predict aim for Sniper
                dist = math.hypot(self.locked_enemy.x-self.x, self.locked_enemy.y-self.y)
                t = dist / 20.0
                tx = self.locked_enemy.x + self.locked_enemy.vx * t
                ty = self.locked_enemy.y + self.locked_enemy.vy * t
                app.projectiles.append(Projectile(self.x,self.y, tx,ty, self.get_total_attack()*2,self,wc,20.0,"SNIPER"))

        # --- New Skills ---
        elif sk=="Blink Strike":
            if self.locked_enemy:
                old_x, old_y = self.x, self.y
                a = math.atan2(self.locked_enemy.y-self.y, self.locked_enemy.x-self.x)
                self.x = self.locked_enemy.x + math.cos(a)*20
                self.y = self.locked_enemy.y + math.sin(a)*20
                dmg = max(1, self.get_total_attack()*2 - self.locked_enemy.defense)
                self.locked_enemy.hp -= dmg; self.locked_enemy.hit_timer = 15; self.damage_dealt += dmg
                app.dmg_texts.append(DamageText(self.locked_enemy.x,self.locked_enemy.y-20, f"CRIT {dmg}!",(255,50,50)))
                for _ in range(15): app.particles.append(SparkParticle(self.locked_enemy.x,self.locked_enemy.y,(255,255,255)))
                app.particles.append(LightningParticle(old_x,old_y,self.x,self.y,(255,255,255)))
                if self.locked_enemy.hp<=0:
                    self.locked_enemy.is_alive=False; self.kills+=1
                    app.add_kill(self.name,self.locked_enemy.name,"Blink Strike 🗡️")

        elif sk=="Lifesteal Strike":
            if self.locked_enemy:
                d = math.hypot(self.x-self.locked_enemy.x, self.y-self.locked_enemy.y)
                if d <= self.get_attack_range() + 15:
                    dmg = max(1, int(self.get_total_attack()*1.2) - self.locked_enemy.defense)
                    self.locked_enemy.hp -= dmg; self.locked_enemy.hit_timer = 10; self.damage_dealt += dmg
                    heal = int(dmg * 0.5)
                    self.hp = min(self.max_hp, self.hp + heal)
                    app.dmg_texts.append(DamageText(self.x,self.y-20, f"+{heal}",(50,255,50)))
                    app.particles.append(LightningParticle(self.x,self.y,self.locked_enemy.x,self.locked_enemy.y,(255,50,50)))
                    if self.locked_enemy.hp<=0:
                        self.locked_enemy.is_alive=False; self.kills+=1
                        app.add_kill(self.name,self.locked_enemy.name,"Lifesteal 🩸")

        elif sk=="Meteor Strike":
            if self.locked_enemy:
                app.danger_zones.append({"x": self.locked_enemy.x, "y": self.locked_enemy.y, "radius": 120, "timer": 60, "shooter": self, "type": "METEOR", "dmg": self.get_total_attack()*3})
                app.particles.append(MeteorWarning(self.locked_enemy.x, self.locked_enemy.y, 120, 60))

        elif sk=="Poison Cloud":
            if self.locked_enemy:
                app.danger_zones.append({"x": self.locked_enemy.x, "y": self.locked_enemy.y, "radius": 100, "timer": 150, "shooter": self, "type": "POISON", "dmg": max(1, self.get_total_attack()//5)})

        elif sk=="Frost Nova":
            for h in heroes:
                if h!=self and h.is_alive:
                    d=math.hypot(self.x-h.x, self.y-h.y)
                    if d<130:
                        dmg=max(1,int(self.get_total_attack()*0.5)-h.defense)
                        h.hp-=dmg; h.hit_timer=8; h.frost_timer=90; self.damage_dealt+=dmg
                        app.dmg_texts.append(DamageText(h.x,h.y-20,str(dmg),(100,255,255)))
                        if h.hp<=0:
                            h.is_alive=False; self.kills+=1
                            app.add_kill(self.name,h.name,"Frost Nova ❄️")
            for _ in range(24):
                ang=random.uniform(0,math.pi*2)
                app.particles.append(SparkParticle(self.x+math.cos(ang)*20,self.y+math.sin(ang)*20,(100,255,255)))
                app.particles.append(SmokeParticle(self.x+math.cos(ang)*100,self.y+math.sin(ang)*100,(100,200,255)))

        elif sk=="Laser Beam":
            if self.locked_enemy:
                wc=self.equipped_weapon.color if self.equipped_weapon else (255,50,50)
                ba=math.atan2(self.locked_enemy.y-self.y, self.locked_enemy.x-self.x)
                tx = self.x + math.cos(ba)*800
                ty = self.y + math.sin(ba)*800
                app.projectiles.append(Projectile(self.x,self.y, tx,ty, self.get_total_attack()*2,self,wc,30.0,"LASER"))
                for h in heroes:
                    if h!=self and h.is_alive:
                        # Distance to line segment
                        d = abs((ty-self.y)*h.x - (tx-self.x)*h.y + tx*self.y - ty*self.x) / math.hypot(tx-self.x, ty-self.y)
                        if d < 20:
                            dot = (h.x-self.x)*(tx-self.x) + (h.y-self.y)*(ty-self.y)
                            if dot > 0 and dot < 800*800:
                                dmg = max(1, self.get_total_attack()-h.defense)
                                h.hp-=dmg; h.hit_timer=5; self.damage_dealt+=dmg
                                app.dmg_texts.append(DamageText(h.x,h.y-20,str(dmg),wc))
                                if h.hp<=0:
                                    h.is_alive=False; self.kills+=1
                                    app.add_kill(self.name,h.name,"Laser ⚡")

        elif sk=="Tornado":
            app.danger_zones.append({"x": self.x, "y": self.y, "radius": 70, "timer": 200, "shooter": self, "type": "TORNADO", "dmg": max(1, self.get_total_attack()//3), "vx": random.uniform(-2,2), "vy": random.uniform(-2,2)})

    # ---------- UPDATE ----------
    def update(self, map_size, items, heroes, app, safe_zone_radius, obstacles):
        if not self.is_alive: return
        nobs = self._nearby_obs(obstacles)

        # Cooldown ticks
        if self.stamina<self.max_stamina: self.stamina=min(self.max_stamina,self.stamina+0.32)
        if self.attack_cooldown>0: self.attack_cooldown-=1
        if self.hit_timer>0: self.hit_timer-=1
        if self.skill_cd>0: self.skill_cd-=1
        if self.poison_timer>0: 
            self.poison_timer-=1
            if self.poison_timer%15==0: 
                self.hp -= 2
                app.dmg_texts.append(DamageText(self.x,self.y-10,"-2",(50,200,50)))
                if self.hp<=0: self.is_alive=False; return
        if self.frost_timer>0: self.frost_timer-=1

        # Skill active duration
        if self.skill_active:
            self.skill_timer-=1
            if self.skill_timer<=0:
                self.skill_active=False; self.shield_active=False

        # Rotation animation
        self.rotation += self.rotation_speed
        if self.committed_state=="COMBAT": self.rotation_speed=0.08
        else: self.rotation_speed=max(abs(self.rotation_speed),0.03)*random.choice([1,-1]) if random.random()<0.01 else self.rotation_speed

        # Speed
        eff=self.base_speed
        if self.frost_timer>0: eff *= 0.4 # Slowed
        if self.equipped_weapon:
            wc=self.equipped_weapon.weapon_class
            if wc=="MELEE": eff*=1.32
            elif wc=="RANGED": eff*=0.90
            elif wc=="MAGIC": eff*=0.95
            if self.equipped_weapon.name == "Minigun": eff*=0.6 # Heavy

        if self.dash_timer>0:
            self.speed=eff*4.2; self.dash_timer-=1
            if app.frame_count%2==0:
                app.particles.append(GlowTrail(self.x,self.y,self.glow_color,self.hero_size))
        else:
            self.speed=eff

        # Zone damage
        cx,cy=map_size/2,map_size/2
        dtc=math.hypot(self.x-cx,self.y-cy)
        is_outside=dtc>safe_zone_radius
        if is_outside:
            dmg=0.65*(0.3 if self.shield_active else 1.0)
            self.hp-=dmg; self.hit_timer=2
            if app.frame_count%15==0:
                app.dmg_texts.append(DamageText(self.x,self.y-10,"-1",(105,255,105)))
            if self.hp<=0:
                self.is_alive=False; return

        # Dodge Danger Zones (Meteor / Poison)
        danger_dist = 9999
        danger_x, danger_y = 0, 0
        for dz in app.danger_zones:
            d = math.hypot(self.x-dz["x"], self.y-dz["y"])
            if d < dz["radius"] + 20:
                danger_dist = d; danger_x, danger_y = dz["x"], dz["y"]
                break
        if danger_dist < 9999:
            self.move_away(danger_x, danger_y, nobs)
            if self.stamina>=50 and self.dash_timer<=0: self.dash()

        # Dodge projectiles
        for p in app.projectiles:
            if p.shooter!=self and math.hypot(self.x-p.x,self.y-p.y)<72:
                if self.dash():
                    da=math.atan2(p.vy,p.vx)+(math.pi/2 if random.random()<0.5 else -math.pi/2)
                    self.x+=math.cos(da)*16; self.y+=math.sin(da)*16
                    break

        # Lock enemy
        if self.locked_enemy and not self.locked_enemy.is_alive:
            self.locked_enemy=None
        ce=None; ms=99999; mde=400
        for h in heroes:
            if h!=self and h.is_alive:
                d=math.hypot(self.x-h.x,self.y-h.y)
                if d<450 and self._can_see(h.x,h.y,nobs):
                    sc=d+(h.hp*1.5)
                    if h==self.locked_enemy: sc*=0.5
                    if sc<ms: ms=sc; ce=h; mde=d
        self.locked_enemy=ce

        # Find nearest item
        ci=None; mdi=165
        for it in items:
            if not it.is_picked_up:
                d=math.hypot(self.x-it.x,self.y-it.y)
                if it.item_type=="WEAPON" and self.equipped_weapon is None and d<mdi:
                    mdi=d; ci=it
                elif it.item_type=="POTION" and self.potions_count<2 and d<mdi:
                    mdi=d; ci=it
        self._pickup_nearby(items)

        # Skill trigger
        if self.skill_cd<=0 and ce:
            sk=self.skill_name; de=mde
            fire=False
            if sk=="Whirlwind" and de<85: fire=True
            elif sk=="Eagle Eye" and de>155 and not self.skill_active: fire=True
            elif sk in ("Arcane Nova","Chain Bolt") and self.hp<self.max_hp*0.32: fire=True
            elif sk=="Shadow Dash" and 100<de<210: fire=True
            elif sk=="Iron Skin" and self.hp<self.max_hp*0.52 and not self.skill_active: fire=True
            elif sk=="Volley" and de<210: fire=True
            elif sk=="Fireball" and de<158: fire=True
            elif sk=="Chain Lightning": fire=True
            elif sk=="Quake" and de<105: fire=True
            elif sk=="Rapid Fire" and de<168: fire=True
            elif sk=="Double Strike" and de<=self.get_attack_range()+14: fire=True
            elif sk=="Grenade" and de<230: fire=True
            elif sk=="Sniper Mark" and de>200: fire=True
            elif sk in ("Shockwave","Quake") and de<72: fire=True
            elif sk=="Blink Strike" and 60<de<200: fire=True
            elif sk=="Lifesteal Strike" and de<45 and self.hp<self.max_hp*0.8: fire=True
            elif sk=="Meteor Strike" and 100<de<300: fire=True
            elif sk=="Poison Cloud" and de<150: fire=True
            elif sk=="Frost Nova" and de<120: fire=True
            elif sk=="Laser Beam" and de<350: fire=True
            elif sk=="Tornado" and de<200: fire=True
            
            if fire: self._use_skill(app,heroes,nobs)

        # State machine
        if self.state_commit_timer>0: self.state_commit_timer-=1
        ds="PATROL"
        
        # SMART COVER Logic
        needs_cover = self.hp < self.max_hp * 0.35 and ce and mde < 300
        
        if is_outside or dtc>safe_zone_radius-55: ds="RUN ZONE"
        elif needs_cover: ds="FLEEING" # Force fleeing for cover
        elif self.hp<self.max_hp*self.heal_threshold and self.potions_count>0: ds="HEALING"
        elif ce:
            threat=self.evaluate_threat(ce)
            fl=self.flee_threshold*1.2 if self.committed_state=="FLEEING" else self.flee_threshold
            if self.hero_class==HeroClass.TANK: fl*=0.45
            if threat<fl: ds="FLEEING"
            elif ci and mde>self.loot_greed_dist: ds="LOOTING"
            else: ds="COMBAT"
        elif ci: ds="LOOTING"
        elif self.hp<self.max_hp: ds="RESTING"

        can_sw=(self.state_commit_timer<=0)
        if ds in ("RUN ZONE","HEALING") and self.committed_state!=ds: can_sw=True
        if can_sw and ds!=self.committed_state:
            self.committed_state=ds
            self.state_commit_timer=random.randint(35,55)
            self.rest_timer=0
        self.state_label=self.committed_state

        # Execute state
        if self.committed_state=="RUN ZONE":
            self.move_towards(cx,cy,nobs)

        elif self.committed_state=="HEALING":
            self.hp=min(self.max_hp,self.hp+52)
            self.potions_count-=1
            for _ in range(14):
                app.particles.append(SparkParticle(self.x,self.y+random.uniform(-12,12),(52,255,105)))
            app.particles.append(HealBurst(self.x,self.y))
            app.dmg_texts.append(DamageText(self.x,self.y-22,"+52 HP",(0,255,105)))
            self.committed_state="PATROL"; self.state_commit_timer=0

        elif self.committed_state=="FLEEING":
            if ce:
                if not needs_cover and (mde<46 or (self.hp<32 and mde<105)):
                    self.committed_state="COMBAT"; self.state_label="FIGHT BACK!"
                    self.state_commit_timer=62
                else:
                    cov=self._find_cover(ce.x,ce.y,nobs)
                    if cov and mde<250: # Smart Cover execution
                        dx=(cov.x+cov.w/2)-ce.x; dy=(cov.y+cov.h/2)-ce.y
                        d=math.hypot(dx,dy)
                        if d>0:
                            self.move_towards(cov.x+cov.w/2+(dx/d)*40,cov.y+cov.h/2+(dy/d)*40,nobs)
                            if self.potions_count>0 and self.hp<self.max_hp:
                                self.committed_state="HEALING"; self.state_commit_timer=0
                    else:
                        self.move_away(ce.x,ce.y,nobs)
            else:
                self.state_commit_timer=0

        elif self.committed_state=="LOOTING":
            if ci: self.move_towards(ci.x,ci.y,nobs)
            else: self.state_commit_timer=0

        elif self.committed_state=="COMBAT":
            if ce:
                ar=self.get_attack_range()
                is_ranged=self.equipped_weapon and self.equipped_weapon.weapon_class in ("RANGED","MAGIC")
                can_hit=self._can_see(ce.x,ce.y,nobs)

                if not is_ranged and 36<mde<185 and self.stamina>=50:
                    if self.dash(): self.move_towards(ce.x,ce.y,nobs)

                # KITING LOGIC
                if is_ranged:
                    if not can_hit: self.move_towards(ce.x,ce.y,nobs)
                    elif mde < ar*0.6: 
                        self.move_away(ce.x,ce.y,nobs) # Kiting
                        if self.stamina>=50 and random.random()<0.05: self.dash()
                    elif mde > ar*0.9: self.move_towards(ce.x,ce.y,nobs)
                    else:
                        ang=math.atan2(ce.y-self.y,ce.x-self.x)
                        sd=math.pi/2 if self.hero_id%2==0 else -math.pi/2
                        nx=self.x+math.cos(ang+sd)*self.speed*0.72
                        ny=self.y+math.sin(ang+sd)*self.speed*0.72
                        if not self._check_col(nx,ny,nobs): 
                            self.vx, self.vy = nx-self.x, ny-self.y
                            self.x,self.y=nx,ny
                else:
                    if not can_hit or mde>ar*0.62:
                        self.move_towards(ce.x,ce.y,nobs)
                    elif self.attack_cooldown>0:
                        ang=math.atan2(ce.y-self.y,ce.x-self.x)
                        nx=self.x+math.cos(ang+math.pi/2)*self.speed*0.82
                        ny=self.y+math.sin(ang+math.pi/2)*self.speed*0.82
                        if not self._check_col(nx,ny,nobs): 
                            self.vx, self.vy = nx-self.x, ny-self.y
                            self.x,self.y=nx,ny

                if mde<=ar and self.attack_cooldown<=0 and can_hit:
                    dmg=max(1,self.get_total_attack()-ce.defense)
                    if ce.shield_active: dmg=max(1,int(dmg*0.3))
                    self.attack_cooldown=self.get_cooldown()
                    wc=self.equipped_weapon.weapon_class if self.equipped_weapon else "MELEE"
                    wcol=self.equipped_weapon.color if self.equipped_weapon else (205,205,205)

                    if is_ranged:
                        sp=self.equipped_weapon.spread if self.equipped_weapon else 0.06
                        
                        # PREDICTION AIM
                        dist = math.hypot(ce.x-self.x, ce.y-self.y)
                        t = dist / 12.0 # approx bullet speed
                        pred_x = ce.x + ce.vx * t
                        pred_y = ce.y + ce.vy * t
                        
                        ba=math.atan2(pred_y-self.y, pred_x-self.x)
                        fa=ba+random.uniform(-sp,sp)
                        tx=self.x+math.cos(fa)*ar; ty=self.y+math.sin(fa)*ar
                        pt="MAGIC" if wc=="MAGIC" else "NORMAL"
                        app.projectiles.append(Projectile(self.x,self.y,tx,ty,dmg,self,wcol,11.5,pt))
                    else:
                        ce.hp-=dmg; ce.hit_timer=11; self.damage_dealt+=dmg
                        for _ in range(7): app.particles.append(BloodParticle(ce.x,ce.y))
                        for _ in range(4): app.particles.append(SparkParticle(ce.x,ce.y,(255,200,105)))
                        app.dmg_texts.append(DamageText(ce.x,ce.y-22,str(dmg)))
                        if ce.hp<=0:
                            ce.is_alive=False; self.kills+=1
                            wname=self.equipped_weapon.name if self.equipped_weapon else "Tay không"
                            app.add_kill(self.name,ce.name,wname)
            else:
                self.state_commit_timer=0

        elif self.committed_state=="RESTING":
            self.rest_timer+=1
            if self.rest_timer>62:
                self.hp=min(self.max_hp,self.hp+0.12)
                if app.frame_count%32==0:
                    app.dmg_texts.append(DamageText(self.x,self.y-12,"+",(155,255,155)))

        elif self.committed_state=="PATROL":
            self.rest_timer=0
            if self.wander_target is None or math.hypot(self.x-self.wander_target[0],self.y-self.wander_target[1])<22:
                rx=cx+random.uniform(-safe_zone_radius*0.42,safe_zone_radius*0.42)
                ry=cy+random.uniform(-safe_zone_radius*0.42,safe_zone_radius*0.42)
                self.wander_target=(rx,ry)
            self.move_towards(self.wander_target[0],self.wander_target[1],nobs)

        if self.vx == 0 and self.vy == 0:
            self.vx, self.vy = 0, 0 # Keep track of velocity for prediction
            
        self.x=max(12,min(self.x,map_size-12))
        self.y=max(12,min(self.y,map_size-12))

    def _pickup_nearby(self, items):
        for it in items:
            if not it.is_picked_up:
                if math.hypot(self.x-it.x,self.y-it.y)<24:
                    if it.item_type=="WEAPON" and self.equipped_weapon is None:
                        it.is_picked_up=True; self.equipped_weapon=it
                        if it.skill_name: self.skill_name=it.skill_name
                    elif it.item_type=="POTION" and self.potions_count<2:
                        it.is_picked_up=True; self.potions_count+=1

    def draw(self, surface, cam, fonts, show_states, frame_count):
        if not self.is_alive or not cam.is_visible(self.x,self.y,35): return
        sx,sy=cam.world_to_screen(self.x,self.y)
        sf=fonts["small"]
        hs=self.hero_size

        # Glow aura
        if cam.following==self or self.skill_active:
            gr=hs+10
            if self.skill_active:
                gr=int(hs+8+abs(math.sin(frame_count*0.12))*7)
            draw_glow(surface,self.glow_color,sx,sy,gr,130)

        # Shield ring
        if self.shield_active:
            pulse=abs(math.sin(frame_count*0.16))
            sr=hs+9+int(pulse*4)
            draw_poly(surface,(200,185,32),sx,sy,sr,6,self.rotation*0.45,2)
            draw_poly(surface,(255,220,60),sx,sy,sr+3,6,self.rotation*0.45+0.15,1)

        # Hit flash & Debuffs
        dc = self.color
        if self.hit_timer>0:
            dc=(255,105,105)
            draw_glow(surface,(255,52,52),sx,sy,hs+7,160)
        elif self.poison_timer>0:
            dc=(100,255,100)
            if frame_count%5==0: draw_glow(surface,(50,200,50),sx,sy,hs+12,80)
        elif self.frost_timer>0:
            dc=(100,200,255)
            if frame_count%5==0: draw_glow(surface,(100,255,255),sx,sy,hs+5,120)

        # Shadow
        pygame.draw.circle(surface,(4,6,11),(sx+4,sy+4),hs)

        # Body shape
        if self.hero_class==HeroClass.MAGE:
            draw_star(surface,dc,sx,sy,hs,hs*0.48,6,self.rotation)
            draw_star(surface,(min(255,dc[0]+80),min(255,dc[1]+80),min(255,dc[2]+80)), sx,sy,hs,hs*0.48,6,self.rotation,1)
        else:
            draw_poly(surface,dc,sx,sy,hs,self.shape_sides,self.rotation)
            oc=(min(255,dc[0]+82),min(255,dc[1]+82),min(255,dc[2]+82))
            draw_poly(surface,oc,sx,sy,hs,self.shape_sides,self.rotation,1)

        # Weapon indicator
        if self.equipped_weapon:
            wa=self.facing_angle
            wx=sx+int(math.cos(wa)*(hs+5))
            wy=sy+int(math.sin(wa)*(hs+5))
            pygame.draw.circle(surface,(22,22,28),(wx+2,wy+2),5)
            pygame.draw.circle(surface,self.equipped_weapon.color,(wx,wy),4)
            pygame.draw.circle(surface,(255,255,255),(wx,wy),2)

        # HP bar
        bw=30
        hpr=max(0,self.hp/self.max_hp)
        hpc=lerp_color((200,32,32),lerp_color((235,185,22),(32,205,82),min(1.0,hpr*2)),max(0,hpr*2-1))
        pygame.draw.rect(surface,(8,8,14),(sx-bw//2-1,sy-hs-16,bw+2,6))
        pygame.draw.rect(surface,(62,0,0),(sx-bw//2,sy-hs-15,bw,4))
        pygame.draw.rect(surface,hpc,(sx-bw//2,sy-hs-15,int(bw*hpr),4))

        # Stamina bar
        str_=max(0,self.stamina/self.max_stamina)
        pygame.draw.rect(surface,(0,42,105),(sx-bw//2,sy-hs-9,int(bw*str_),2))

        # Skill cooldown bar
        if self.skill_cd_max>0:
            skr=1.0-(self.skill_cd/self.skill_cd_max)
            skc=(255,222,52) if self.skill_cd<=0 else (125,105,22)
            pygame.draw.rect(surface,(32,28,0),(sx-bw//2,sy-hs-5,bw,2))
            pygame.draw.rect(surface,skc,(sx-bw//2,sy-hs-5,int(bw*skr),2))

        if show_states:
            tc=(255,255,255)
            if self.state_label=="FLEEING": tc=(255,105,105)
            elif self.state_label in ("COMBAT","FIGHT BACK!"): tc=(255,205,52)
            elif self.state_label=="HEALING": tc=(52,255,105)

            ns=sf.render(self.name,True,tc)
            surface.blit(ns,(sx-ns.get_width()//2,sy-hs-30))

            clabel=f"[{self.hero_class.value[0]}] {self.state_label}"
            cs=sf.render(clabel,True,(155,155,185))
            surface.blit(cs,(sx-cs.get_width()//2,sy+hs+5))

            if self.equipped_weapon:
                ws=fonts["tiny"].render(self.equipped_weapon.name,True,(120,120,155))
                surface.blit(ws,(sx-ws.get_width()//2,sy+hs+17))

# ==================== KILL FEED ====================
class KillEntry:
    def __init__(self, killer, victim, weapon):
        self.killer=killer; self.victim=victim; self.weapon=weapon
        self.life=self.max_life=255

# ==================== ARENA APP ====================
class ArenaApp:
    def __init__(self, map_size=8000, pop_size=300, max_frames=6000):
        pygame.init()
        self.map_size=map_size; self.pop_size=pop_size; self.max_frames=max_frames
        total_w=SCREEN_W+UI_WIDTH
        self.screen=pygame.display.set_mode((total_w,SCREEN_H))
        pygame.display.set_caption("⚔️  AI Battle Royale — ULTRA Edition v2")
        self.clock=pygame.time.Clock()

        self.fonts={
            "tiny":   pygame.font.SysFont("Arial",11),
            "small":  pygame.font.SysFont("Arial",12,bold=True),
            "normal": pygame.font.SysFont("Arial",14,bold=True),
            "large":  pygame.font.SysFont("Arial",20,bold=True),
            "title":  pygame.font.SysFont("Arial",28,bold=True),
            "huge":   pygame.font.SysFont("Arial",46,bold=True),
        }

        self.camera=Camera(SCREEN_W,SCREEN_H,map_size)
        self.camera.center_on(map_size/2,map_size/2)
        self.camera_shake = 0

        self.match_count=1
        self.population=[Hero(i) for i in range(pop_size)]
        self.obstacles=[]; self.items=[]
        self.particles=[]; self.projectiles=[]
        self.danger_zones=[]
        self.dmg_texts=[]; self.kill_feed=[]
        self.frame_count=0

        self.hero_ui_rects=[]
        self.max_radius=map_size*0.45
        self.final_radius=450.0
        self.safe_zone_radius=self.max_radius
        self.total_phases=4
        self.phase_duration=max_frames//self.total_phases
        self.current_phase=0
        self.phase_announce_timer=0

        self.render_enabled=True
        self.show_states=True
        self.show_minimap=True
        self.running=True
        self.focus_camera=False
        self.match_over=False

        self._bg=self._make_bg()
        self.obstacles=generate_obstacles(map_size,120)
        self.spawn_items()
        for h in self.population: h.reset(self.map_size)

    def _make_bg(self):
        surf=pygame.Surface((SCREEN_W,SCREEN_H))
        for y in range(SCREEN_H):
            r=y/SCREEN_H
            c=lerp_color((7,11,19),(14,21,34),r)
            pygame.draw.line(surf,c,(0,y),(SCREEN_W,y))
        return surf

    def add_kill(self, killer, victim, weapon):
        self.kill_feed.insert(0,KillEntry(killer,victim,weapon))
        if len(self.kill_feed)>8: self.kill_feed.pop()

    def spawn_items(self):
        self.items.clear()
        iid=0
        for _ in range(160):
            self.items.append(generate_random_weapon(iid,self.map_size)); iid+=1
        for _ in range(140):
            x=random.uniform(85,self.map_size-85)
            y=random.uniform(85,self.map_size-85)
            self.items.append(HealthPotion(iid,x,y,65)); iid+=1

    def start_new_match(self):
        winners=[h for h in self.population if h.is_alive]
        if winners:
            w=winners[0]
            wn=w.equipped_weapon.name if w.equipped_weapon else "Tay không"
            print(f"🏆 [{w.hero_class.value}] {w.name} | K:{w.kills} | DMG:{int(w.damage_dealt)} | {wn}")
        else:
            print("💀 Hòa!")
        self.match_count+=1; self.frame_count=0
        self.safe_zone_radius=self.max_radius
        self.particles.clear(); self.projectiles.clear(); self.danger_zones.clear()
        self.dmg_texts.clear(); self.kill_feed.clear()
        self.current_phase=0; self.phase_announce_timer=0
        self.obstacles=generate_obstacles(self.map_size,120)
        for h in self.population:
            if random.random()<0.28:
                h.hero_class=random.choice(list(HeroClass))
                cfg=HERO_CLASS_CONFIG[h.hero_class]
                h.color=cfg["color"]; h.glow_color=cfg["glow"]
                h.shape_sides=cfg["sides"]; h.hero_size=cfg["size"]
                h.skill_name=cfg["skill"]; h.skill_cd_max=cfg["skill_cd"]
            h.reset(self.map_size)
        self.spawn_items()

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: self.running=False
            elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                mx,my=ev.pos
                for rect,th in self.hero_ui_rects:
                    if rect.collidepoint(mx,my):
                        self.camera.following=th; self.focus_camera=False; break
            elif ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_RETURN and self.match_over:
                    self.match_over=False; self.start_new_match()
                elif ev.key==pygame.K_SPACE: self.render_enabled=not self.render_enabled
                elif ev.key==pygame.K_s: self.show_states=not self.show_states
                elif ev.key==pygame.K_m: self.show_minimap=not self.show_minimap
                elif ev.key==pygame.K_f: self.focus_camera=not self.focus_camera
                elif ev.key==pygame.K_c:
                    self.camera.center_on(self.map_size/2,self.map_size/2)
                    self.camera.following=None

        keys=pygame.key.get_pressed()
        dx=dy=0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx-=1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx+=1
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy-=1
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy+=1
        if dx or dy: self.camera.move(dx,dy)

        if self.camera.following:
            if self.camera.following.is_alive:
                self.camera.center_on(self.camera.following.x,self.camera.following.y,smooth=True)
            else:
                self.camera.following=None

    def draw(self):
        if not self.render_enabled: return
        
        # Shake Camera
        shake_x = random.uniform(-self.camera_shake, self.camera_shake)
        shake_y = random.uniform(-self.camera_shake, self.camera_shake)
        self.camera.x += shake_x; self.camera.y += shake_y

        cam=self.camera; scr=self.screen

        # BG
        scr.blit(self._bg,(0,0))

        # Grid
        gs=200; gc=(26,36,52)
        sx0=int(cam.x//gs)*gs; sy0=int(cam.y//gs)*gs
        for gx in range(sx0,int(cam.x+SCREEN_W)+gs,gs):
            px,_=cam.world_to_screen(gx,0)
            pygame.draw.line(scr,gc,(px,0),(px,SCREEN_H))
        for gy in range(sy0,int(cam.y+SCREEN_H)+gs,gs):
            _,py=cam.world_to_screen(0,gy)
            pygame.draw.line(scr,gc,(0,py),(SCREEN_W,py))

        # Safe zone
        cx,cy=self.map_size/2,self.map_size/2
        scx,scy=cam.world_to_screen(cx,cy)
        zr=int(self.safe_zone_radius)
        pulse=abs(math.sin(self.frame_count*0.04))

        # Danger overlay outside ring
        ds=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
        if zr>0:
            ds.fill((205,22,22,18))
            pygame.draw.circle(ds,(0,0,0,0),(scx,scy),zr)
        scr.blit(ds,(0,0))

        # Zone ring glow
        zc=(int(32+22*pulse),int(105+52*pulse),int(205+50*pulse))
        if zr>0:
            pygame.draw.circle(scr,zc,(scx,scy),zr,2)
            pygame.draw.circle(scr,(zc[0]//2,zc[1]//2,zc[2]//2),(scx,scy),zr+5,1)
            pygame.draw.circle(scr,(zc[0]//3,zc[1]//3,zc[2]//3),(scx,scy),zr+9,1)

        # Danger Zones (Poison, Tornado)
        for dz in self.danger_zones:
            if dz["type"] == "POISON":
                d_sx, d_sy = cam.world_to_screen(dz["x"], dz["y"])
                pygame.draw.circle(scr, (50,200,50,50), (d_sx, d_sy), int(dz["radius"]))
            elif dz["type"] == "TORNADO":
                d_sx, d_sy = cam.world_to_screen(dz["x"], dz["y"])
                pygame.draw.circle(scr, (150,150,150,30), (d_sx, d_sy), int(dz["radius"]))

        # Obstacles
        for obs in self.obstacles:
            if cam.is_rect_visible(obs.x,obs.y,obs.w,obs.h):
                obs.draw(scr,cam)

        # Items (bobbing)
        for it in self.items:
            if not it.is_picked_up and cam.is_visible(it.x,it.y):
                it.bob_timer+=0.08
                isx,isy=cam.world_to_screen(it.x,it.y)
                bob=int(math.sin(it.bob_timer)*3)
                if it.item_type=="WEAPON":
                    draw_glow(scr,it.color,isx,isy+bob,14,65)
                    pygame.draw.rect(scr,(8,8,14),(isx-5,isy-5+bob+2,10,10))
                    pygame.draw.rect(scr,it.color,(isx-4,isy-4+bob,8,8))
                    hl=(min(255,it.color[0]+65),min(255,it.color[1]+65),min(255,it.color[2]+65))
                    pygame.draw.rect(scr,hl,(isx-4,isy-4+bob,8,8),1)
                else:
                    draw_glow(scr,(52,255,52),isx,isy+bob,11,55)
                    pygame.draw.circle(scr,(18,18,18),(isx+2,isy+2+bob),7)
                    pygame.draw.circle(scr,(0,182,42),(isx,isy+bob),7)
                    pygame.draw.circle(scr,(105,255,125),(isx,isy+bob),4)
                    pygame.draw.circle(scr,(255,255,255),(isx-2,isy-2+bob),2)

        # Particles
        for p in self.particles: p.draw(scr,cam)

        # Heroes
        alive_count=0
        for h in self.population:
            if h.is_alive:
                alive_count+=1
                h.draw(scr,cam,self.fonts,self.show_states,self.frame_count)

        # Projectiles
        for p in self.projectiles: p.draw(scr,cam)

        # Damage texts
        for dt in self.dmg_texts: dt.draw(scr,cam,self.fonts["normal"])

        # Reset camera shake
        self.camera.x -= shake_x; self.camera.y -= shake_y

        # ====== MINIMAP ======
        if self.show_minimap:
            ms=195; mx=SCREEN_W-ms-10; my=SCREEN_H-ms-10
            msc=ms/self.map_size
            msurf=pygame.Surface((ms,ms),pygame.SRCALPHA)
            msurf.fill((8,12,20,210))
            scr.blit(msurf,(mx,my))
            pygame.draw.rect(scr,(55,75,100),(mx,my,ms,ms),1)
            # Zone
            zmr=int(self.safe_zone_radius*msc)
            zcx=int(mx+cx*msc); zcy=int(my+cy*msc)
            if zmr>0: pygame.draw.circle(scr,(52,105,205),(zcx,zcy),zmr,1)
            # Obstacles
            for obs in self.obstacles:
                ox=int(mx+obs.x*msc); oy=int(my+obs.y*msc)
                ow=max(1,int(obs.w*msc)); oh=max(1,int(obs.h*msc))
                oc=(32,82,32) if obs.obs_type=="TREE" else (58,58,68)
                pygame.draw.rect(scr,oc,(ox,oy,ow,oh))
            # Items
            for it in self.items:
                if not it.is_picked_up:
                    iix=int(mx+it.x*msc); iiy=int(my+it.y*msc)
                    ic=(205,205,82) if it.item_type=="WEAPON" else (52,205,52)
                    pygame.draw.rect(scr,ic,(iix,iiy,2,2))
            # Heroes
            for h in self.population:
                if h.is_alive:
                    hx=int(mx+h.x*msc); hy=int(my+h.y*msc)
                    hc=(0,255,255) if cam.following==h else h.color
                    sz=3 if cam.following==h else 2
                    pygame.draw.rect(scr,hc,(hx,hy,sz,sz))
            # Viewport
            vx=int(mx+cam.x*msc); vy=int(my+cam.y*msc)
            vw=int(SCREEN_W*msc); vh=int(SCREEN_H*msc)
            pygame.draw.rect(scr,(205,205,205),(vx,vy,vw,vh),1)
            scr.blit(self.fonts["tiny"].render("MINIMAP",True,(95,115,140)),(mx+5,my+3))

        # ====== KILL FEED ======
        for i,kf in enumerate(self.kill_feed):
            ratio=kf.life/kf.max_life
            a=int(255*min(1.0,ratio*3))
            txt=f"☠ {kf.killer[:14]} → {kf.victim[:14]}  [{kf.weapon}]"
            ks=self.fonts["tiny"].render(txt,True,(255,int(182*ratio),int(105*ratio)))
            ks.set_alpha(a)
            bgs=pygame.Surface((ks.get_width()+10,ks.get_height()+4),pygame.SRCALPHA)
            bgs.fill((0,0,0,int(125*ratio)))
            scr.blit(bgs,(8,8+i*19-2))
            scr.blit(ks,(12,8+i*19))

        # ====== HEADER ======
        hh=38
        hsurf=pygame.Surface((SCREEN_W,hh),pygame.SRCALPHA)
        hsurf.fill((0,0,0,165))
        scr.blit(hsurf,(0,0))
        pygame.draw.line(scr,(48,78,112),(0,hh),(SCREEN_W,hh),1)

        pnames=["Phase 1","Phase 2","Phase 3","FINAL"]
        pname=pnames[min(self.current_phase,3)]
        items=[
            (f"⚔️  TRẬN #{self.match_count}",(255,215,0)),
            (f"👥  {alive_count} / {self.pop_size}",(105,225,255)),
            (f"🔵  {int(self.safe_zone_radius)}m",(82,165,255)),
            (f"🎯  {pname}",(205,145,255)),
        ]
        hxo=14
        for text,col in items:
            ts=self.fonts["normal"].render(text,True,col)
            scr.blit(ts,(hxo,hh//2-ts.get_height()//2)); hxo+=ts.get_width()+28
        fps=int(self.clock.get_fps())
        fc=(52,255,52) if fps>=45 else (255,205,52) if fps>=25 else (255,52,52)
        fs=self.fonts["small"].render(f"FPS:{fps}",True,fc)
        scr.blit(fs,(SCREEN_W-fs.get_width()-12,hh//2-fs.get_height()//2))

        # ====== PHASE ANNOUNCEMENT ======
        if self.phase_announce_timer>0:
            ratio=self.phase_announce_timer/120
            alph=int(255*min(1.0,ratio*4)*min(1.0,(1-ratio)*4+0.2))
            pf=["🔵 PHASE 1 — BO THU!","🟡 PHASE 2 — NGUY HIỂM!","🟠 PHASE 3 — QUYẾT CHIẾN!","🔴 FINAL ZONE!"]
            atext=pf[min(self.current_phase-1,3)]
            asurf=self.fonts["huge"].render(atext,True,(255,220,52))
            asurf.set_alpha(alph)
            sc=1.0+0.18*math.sin(ratio*math.pi)
            aw=int(asurf.get_width()*sc); ah=int(asurf.get_height()*sc)
            ascl=pygame.transform.scale(asurf,(aw,ah))
            scr.blit(ascl,(SCREEN_W//2-aw//2,SCREEN_H//2-ah//2))
            self.phase_announce_timer-=1

        # ====== SIDE PANEL ======
        bx=SCREEN_W
        psurf=pygame.Surface((UI_WIDTH,SCREEN_H),pygame.SRCALPHA)
        psurf.fill((9,14,22,235))
        scr.blit(psurf,(bx,0))
        for i in range(4):
            pygame.draw.line(scr,(55-i*10,88-i*15,125-i*20),(bx+i,0),(bx+i,SCREEN_H),1)

        yo=45
        scr.blit(self.fonts["normal"].render("── CLASS LEGEND ──",True,(78,98,122)),(bx+12,yo))
        yo+=20
        for cls,cfg in HERO_CLASS_CONFIG.items():
            cnt=sum(1 for h in self.population if h.is_alive and h.hero_class==cls)
            draw_poly(scr,cfg["color"],bx+15,yo+6,5,cfg["sides"])
            cs=self.fonts["tiny"].render(f"  {cls.value}: {cnt}",True,cfg["color"])
            scr.blit(cs,(bx+22,yo)); yo+=14

        yo+=6
        pygame.draw.line(scr,(38,55,72),(bx+8,yo),(bx+UI_WIDTH-8,yo),1); yo+=10
        scr.blit(self.fonts["normal"].render("── TOP FIGHTERS ──",True,(0,200,225)),(bx+12,yo)); yo+=22

        self.hero_ui_rects.clear()
        living=sorted([h for h in self.population if h.is_alive],key=lambda x:(x.kills,x.damage_dealt),reverse=True)

        for h in living[:10]:
            wn=h.equipped_weapon.name if h.equipped_weapon else "Tay không"
            sel=(cam.following==h)
            irect=pygame.Rect(bx+8,yo,UI_WIDTH-16,46)
            self.hero_ui_rects.append((irect,h))

            bgc=(24,54,72,205) if sel else (17,24,34,185)
            isurf=pygame.Surface((irect.w,irect.h),pygame.SRCALPHA)
            isurf.fill(bgc)
            scr.blit(isurf,(irect.x,irect.y))
            bc=(0,205,235) if sel else (38,55,72)
            pygame.draw.rect(scr,bc,irect,1,border_radius=4)

            # Class shape
            draw_poly(scr,h.color,bx+20,yo+14,5,h.shape_sides,h.rotation)
            tc=(0,230,255) if sel else (225,225,242)
            scr.blit(self.fonts["small"].render(f"{h.name} ({h.kills}K)",True,tc),(bx+30,yo+4))

            bw2=UI_WIDTH-62
            hpr=max(0,h.hp/h.max_hp)
            hpc=lerp_color((200,32,32),lerp_color((235,185,22),(32,205,82),min(1.0,hpr*2)),max(0,hpr*2-1))
            pygame.draw.rect(scr,(32,0,0),(bx+30,yo+20,bw2,4))
            pygame.draw.rect(scr,hpc,(bx+30,yo+20,int(bw2*hpr),4))

            skr=1.0-(h.skill_cd/max(1,h.skill_cd_max))
            pygame.draw.rect(scr,(32,26,0),(bx+30,yo+26,bw2,3))
            pygame.draw.rect(scr,(205,185,32),(bx+30,yo+26,int(bw2*skr),3))

            stat=f"HP:{int(h.hp)} | {wn[:14]}"
            scr.blit(self.fonts["tiny"].render(stat,True,(128,138,162)),(bx+30,yo+32))
            yo+=50

        # Controls hint
        ctrls=["WASD/↑↓←→ : Di chuyển camera","F : Auto-follow top","Click tên : Follow hero",
               "S : Ẩn/hiện nhãn","M : Ẩn/hiện minimap","SPACE : Tắt render","C : Reset camera"]
        yc=SCREEN_H-len(ctrls)*14-10
        pygame.draw.line(scr,(38,55,72),(bx+8,yc-8),(bx+UI_WIDTH-8,yc-8),1)
        for ctrl in ctrls:
            scr.blit(self.fonts["tiny"].render(ctrl,True,(68,78,95)),(bx+10,yc)); yc+=14

        # ====== MATCH OVER ======
        if self.match_over:
            ov=pygame.Surface((SCREEN_W+UI_WIDTH,SCREEN_H),pygame.SRCALPHA)
            ov.fill((0,0,0,185))
            scr.blit(ov,(0,0))
            mcx=(SCREEN_W+UI_WIDTH)//2
            pw,ph=565,595
            pnl=pygame.Surface((pw,ph),pygame.SRCALPHA)
            pnl.fill((14,20,28,245))
            scr.blit(pnl,(mcx-pw//2,72))
            pygame.draw.rect(scr,(255,215,0),(mcx-pw//2,72,pw,ph),2,border_radius=9)
            pygame.draw.rect(scr,(105,82,0),(mcx-pw//2+3,75,pw-6,ph-6),1,border_radius=7)

            ts=self.fonts["title"].render(f"🏆 KẾT QUẢ TRẬN #{self.match_count}",True,(255,215,0))
            scr.blit(ts,(mcx-ts.get_width()//2,98))

            hs2=self.fonts["small"].render(f"{'#':<4}{'Tên':<20}{'Class':<11}{'K':<6}{'DMG':<8}Vũ Khí",True,(120,132,152))
            scr.blit(hs2,(mcx-252,148))
            pygame.draw.line(scr,(58,78,102),(mcx-256,166),(mcx+256,166),1)

            sh=sorted(self.population,key=lambda x:(x.is_alive,x.kills,x.damage_dealt),reverse=True)
            ys=172
            for i,h in enumerate(sh[:13]):
                wn=h.equipped_weapon.name if h.equipped_weapon else "Tay không"
                if i==0: rc=(255,215,0)
                elif i==1: rc=(192,192,192)
                elif i==2: rc=(205,128,52)
                elif h.is_alive: rc=(105,205,105)
                else: rc=(140,140,140)
                row=f"{i+1:<4}{h.name:<20}{h.hero_class.value:<11}{h.kills:<6}{int(h.damage_dealt):<8}{wn}"
                draw_poly(scr,h.color,mcx-258,ys+6,4,h.shape_sides)
                scr.blit(self.fonts["tiny"].render(row,True,rc),(mcx-250,ys)); ys+=24

            palph=int(185+70*abs(math.sin(self.frame_count*0.055)))
            ps=self.fonts["large"].render("[ ENTER ] → VÁN MỚI",True,(205,225,255))
            ps.set_alpha(palph)
            scr.blit(ps,(mcx-ps.get_width()//2,615))

        pygame.display.flip()

    def update(self):
        if self.match_over:
            self.frame_count+=1; return

        alive=sum(1 for h in self.population if h.is_alive)
        if alive<=1:
            self.match_over=True; return

        if self.focus_camera:
            al=[h for h in self.population if h.is_alive]
            if al:
                self.camera.following=max(al,key=lambda h:(h.kills,h.damage_dealt))
                
        # Camera Shake Decay
        if self.camera_shake > 0: self.camera_shake = max(0, self.camera_shake - 0.5)

        # Phase transition
        np=min(self.frame_count//self.phase_duration,self.total_phases-1)
        if np>self.current_phase:
            self.current_phase=np; self.phase_announce_timer=120

        tip=self.frame_count%self.phase_duration
        wt=self.phase_duration*0.6
        dpp=(self.max_radius-self.final_radius)/self.total_phases
        sr=self.max_radius-(dpp*self.current_phase)
        er=self.max_radius-(dpp*(self.current_phase+1))
        if tip>wt:
            st=self.phase_duration-wt
            self.safe_zone_radius=max(er,self.safe_zone_radius-(sr-er)/st)

        # Update heroes
        for h in self.population:
            h.update(self.map_size,self.items,self.population,self,self.safe_zone_radius,self.obstacles)

        # Update Danger Zones
        new_dz = []
        for dz in self.danger_zones:
            dz["timer"] -= 1
            if dz["timer"] <= 0:
                if dz["type"] == "METEOR":
                    self._explosion(dz["x"], dz["y"], dz["dmg"], dz["shooter"], dz["radius"])
                    self.camera_shake = 12 # Huge shake
                continue # Zone expires
            
            if dz["type"] == "POISON":
                if self.frame_count % 5 == 0:
                    ang = random.uniform(0, math.pi*2)
                    r = random.uniform(0, dz["radius"])
                    self.particles.append(SmokeParticle(dz["x"] + math.cos(ang)*r, dz["y"] + math.sin(ang)*r, (50,200,50)))
                # Apply poison
                for h in self.population:
                    if h.is_alive and h != dz["shooter"]:
                        if math.hypot(h.x-dz["x"], h.y-dz["y"]) < dz["radius"]:
                            h.poison_timer = max(h.poison_timer, 60)
            
            elif dz["type"] == "TORNADO":
                dz["x"] += dz.get("vx", 0)
                dz["y"] += dz.get("vy", 0)
                for _ in range(2): self.particles.append(WhirlwindParticle(dz["x"], dz["y"], (200,200,200)))
                # Apply tornado dmg & push
                for h in self.population:
                    if h.is_alive and h != dz["shooter"]:
                        dist = math.hypot(h.x-dz["x"], h.y-dz["y"])
                        if dist < dz["radius"]:
                            if self.frame_count % 10 == 0:
                                dmg = dz["dmg"]
                                if h.shield_active: dmg = max(1, int(dmg*0.3))
                                h.hp -= dmg; h.hit_timer = 5; dz["shooter"].damage_dealt += dmg
                                self.dmg_texts.append(DamageText(h.x,h.y-15, str(dmg), (200,200,200)))
                                if h.hp <= 0:
                                    h.is_alive=False; dz["shooter"].kills+=1
                                    self.add_kill(dz["shooter"].name, h.name, "Tornado 🌪️")
                            h.x += dz.get("vx", 0) * 1.5
                            h.y += dz.get("vy", 0) * 1.5

            new_dz.append(dz)
        self.danger_zones = new_dz

        # Update projectiles
        new_proj=[]
        for p in self.projectiles:
            if p.proj_type == "LASER":
                p.life -= 2
                if p.life <= 0: continue
                new_proj.append(p)
                continue
                
            p.step()
            if p.life<=0: continue
            hit=False
            for obs in self.obstacles:
                if obs.collides_point(p.x,p.y,p.hitbox_radius):
                    for _ in range(5): self.particles.append(SparkParticle(p.x,p.y,(205,205,105)))
                    if p.proj_type=="EXPLOSIVE": 
                        self._explosion(p.x,p.y,p.damage,p.shooter,62)
                        self.camera_shake = 5
                    hit=True; break
            if not hit:
                for h in self.population:
                    if h.is_alive and h!=p.shooter:
                        if math.hypot(p.x-h.x,p.y-h.y)<13+p.hitbox_radius:
                            adm=p.damage
                            if h.shield_active: adm=max(1,int(adm*0.3))
                            h.hp-=adm; h.hit_timer=11
                            p.shooter.damage_dealt+=adm
                            for _ in range(7): self.particles.append(BloodParticle(h.x,h.y))
                            for _ in range(3): self.particles.append(SparkParticle(h.x,h.y,(255,185,52)))
                            self.dmg_texts.append(DamageText(h.x,h.y-22,str(adm)))
                            if p.proj_type=="EXPLOSIVE": 
                                self._explosion(p.x,p.y,p.damage//2,p.shooter,52)
                                self.camera_shake = 5
                            if h.hp<=0:
                                h.is_alive=False; p.shooter.kills+=1
                                wn=p.shooter.equipped_weapon.name if p.shooter.equipped_weapon else "Ranged"
                                self.add_kill(p.shooter.name,h.name,wn)
                            hit=True; break
            if not hit: new_proj.append(p)
        self.projectiles=new_proj

        # Update particles
        self.particles=[p for p in self.particles if (p.update() or True) and p.life>0]
        if len(self.particles)>MAX_PARTICLES:
            self.particles=self.particles[-MAX_PARTICLES:]

        # Update texts
        self.dmg_texts=[dt for dt in self.dmg_texts if (dt.update() or True) and dt.life>0]

        # Update kill feed
        for kf in self.kill_feed: kf.life-=1
        self.kill_feed=[kf for kf in self.kill_feed if kf.life>0]

        self.frame_count+=1

    def _explosion(self, x, y, dmg, shooter, radius):
        for _ in range(int(radius//2)): self.particles.append(ExplosionParticle(x,y,(255,142,22)))
        for _ in range(int(radius//5)): self.particles.append(SmokeParticle(x,y,(82,82,82)))
        for _ in range(int(radius//4)): self.particles.append(SparkParticle(x,y,(255,225,52)))
        for h in self.population:
            if h.is_alive and h!=shooter:
                d=math.hypot(x-h.x,y-h.y)
                if d<radius:
                    adm=max(1,int(dmg*(1-d/radius)))
                    if h.shield_active: adm=max(1,int(adm*0.3))
                    h.hp-=adm; h.hit_timer=14; shooter.damage_dealt+=adm
                    self.dmg_texts.append(DamageText(h.x,h.y-22,str(adm),(255,142,22)))
                    if h.hp<=0:
                        h.is_alive=False; shooter.kills+=1
                        wn=shooter.equipped_weapon.name if shooter.equipped_weapon else "Explosive"
                        self.add_kill(shooter.name,h.name,wn+" 💥")

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            if self.render_enabled:
                self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

# ==================== MAIN ====================
if __name__=="__main__":
    app=ArenaApp(map_size=MAP_SIZE, pop_size=POP_SIZE, max_frames=MAX_FRAMES)
    app.run()