import pygame
import math
import random
from config import NAMES_DATA

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
    F = NAMES_DATA.get("first_names", ["Hero"])
    L = NAMES_DATA.get("last_names", ["Warrior"])
    if not F: F = ["Hero"]
    if not L: L = ["Warrior"]
    return f"{random.choice(F)} {random.choice(L)}"
