import pygame
import math
import random
from utils import lerp_color

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
