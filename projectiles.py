import pygame
import math
from utils import lerp_color, draw_glow

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
