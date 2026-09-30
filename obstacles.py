import pygame
import math
import random

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
