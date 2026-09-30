import pygame
import math
import random
import sys

from config import (MAP_SIZE, POP_SIZE, MAX_FRAMES, SCREEN_W, SCREEN_H, UI_WIDTH, 
                    FPS, MAX_PARTICLES, HeroClass, HERO_CLASS_CONFIG)
from utils import lerp_color, draw_poly
from particles import (ExplosionParticle, SparkParticle, SmokeParticle, 
                       WhirlwindParticle, DamageText, BloodParticle)
from items import HealthPotion, generate_random_weapon
from obstacles import generate_obstacles
from projectiles import Projectile
from hero import Hero
from camera import Camera
from kill_feed import KillEntry

# ==================== ARENA APP ====================
class ArenaApp:
    def __init__(self, map_size=8000, pop_size=300, max_frames=6000):
        pygame.init()
        self.map_size=map_size; self.pop_size=pop_size; self.max_frames=max_frames
        total_w=SCREEN_W+UI_WIDTH
        self.screen=pygame.display.set_mode((total_w,SCREEN_H))
        pygame.display.set_caption("⚔️  AI Battle Royale — ULTRA Edition v2 (Modular)")
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
        
        shake_x = random.uniform(-self.camera_shake, self.camera_shake)
        shake_y = random.uniform(-self.camera_shake, self.camera_shake)
        self.camera.x += shake_x; self.camera.y += shake_y

        cam=self.camera; scr=self.screen

        scr.blit(self._bg,(0,0))

        gs=200; gc=(26,36,52)
        sx0=int(cam.x//gs)*gs; sy0=int(cam.y//gs)*gs
        for gx in range(sx0,int(cam.x+SCREEN_W)+gs,gs):
            px,_=cam.world_to_screen(gx,0)
            pygame.draw.line(scr,gc,(px,0),(px,SCREEN_H))
        for gy in range(sy0,int(cam.y+SCREEN_H)+gs,gs):
            _,py=cam.world_to_screen(0,gy)
            pygame.draw.line(scr,gc,(0,py),(SCREEN_W,py))

        cx,cy=self.map_size/2,self.map_size/2
        scx,scy=cam.world_to_screen(cx,cy)
        zr=int(self.safe_zone_radius)
        pulse=abs(math.sin(self.frame_count*0.04))

        ds=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
        if zr>0:
            ds.fill((205,22,22,18))
            pygame.draw.circle(ds,(0,0,0,0),(scx,scy),zr)
        scr.blit(ds,(0,0))

        zc=(int(32+22*pulse),int(105+52*pulse),int(205+50*pulse))
        if zr>0:
            pygame.draw.circle(scr,zc,(scx,scy),zr,2)
            pygame.draw.circle(scr,(zc[0]//2,zc[1]//2,zc[2]//2),(scx,scy),zr+5,1)
            pygame.draw.circle(scr,(zc[0]//3,zc[1]//3,zc[2]//3),(scx,scy),zr+9,1)

        for dz in self.danger_zones:
            if dz["type"] == "POISON":
                d_sx, d_sy = cam.world_to_screen(dz["x"], dz["y"])
                pygame.draw.circle(scr, (50,200,50,50), (d_sx, d_sy), int(dz["radius"]))
            elif dz["type"] == "TORNADO":
                d_sx, d_sy = cam.world_to_screen(dz["x"], dz["y"])
                pygame.draw.circle(scr, (150,150,150,30), (d_sx, d_sy), int(dz["radius"]))

        for obs in self.obstacles:
            if cam.is_rect_visible(obs.x,obs.y,obs.w,obs.h):
                obs.draw(scr,cam)

        for it in self.items:
            if not it.is_picked_up and cam.is_visible(it.x,it.y):
                it.bob_timer+=0.08
                isx,isy=cam.world_to_screen(it.x,it.y)
                bob=int(math.sin(it.bob_timer)*3)
                if it.item_type=="WEAPON":
                    from utils import draw_glow
                    draw_glow(scr,it.color,isx,isy+bob,14,65)
                    pygame.draw.rect(scr,(8,8,14),(isx-5,isy-5+bob+2,10,10))
                    pygame.draw.rect(scr,it.color,(isx-4,isy-4+bob,8,8))
                    hl=(min(255,it.color[0]+65),min(255,it.color[1]+65),min(255,it.color[2]+65))
                    pygame.draw.rect(scr,hl,(isx-4,isy-4+bob,8,8),1)
                else:
                    from utils import draw_glow
                    draw_glow(scr,(52,255,52),isx,isy+bob,11,55)
                    pygame.draw.circle(scr,(18,18,18),(isx+2,isy+2+bob),7)
                    pygame.draw.circle(scr,(0,182,42),(isx,isy+bob),7)
                    pygame.draw.circle(scr,(105,255,125),(isx,isy+bob),4)
                    pygame.draw.circle(scr,(255,255,255),(isx-2,isy-2+bob),2)

        for p in self.particles: p.draw(scr,cam)

        alive_count=0
        for h in self.population:
            if h.is_alive:
                alive_count+=1
                h.draw(scr,cam,self.fonts,self.show_states,self.frame_count)

        for p in self.projectiles: p.draw(scr,cam)
        for dt in self.dmg_texts: dt.draw(scr,cam,self.fonts["normal"])

        self.camera.x -= shake_x; self.camera.y -= shake_y

        # ====== MINIMAP ======
        if self.show_minimap:
            ms=195; mx=SCREEN_W-ms-10; my=SCREEN_H-ms-10
            msc=ms/self.map_size
            msurf=pygame.Surface((ms,ms),pygame.SRCALPHA)
            msurf.fill((8,12,20,210))
            scr.blit(msurf,(mx,my))
            pygame.draw.rect(scr,(55,75,100),(mx,my,ms,ms),1)
            zmr=int(self.safe_zone_radius*msc)
            zcx=int(mx+cx*msc); zcy=int(my+cy*msc)
            if zmr>0: pygame.draw.circle(scr,(52,105,205),(zcx,zcy),zmr,1)
            for obs in self.obstacles:
                ox=int(mx+obs.x*msc); oy=int(my+obs.y*msc)
                ow=max(1,int(obs.w*msc)); oh=max(1,int(obs.h*msc))
                oc=(32,82,32) if obs.obs_type=="TREE" else (58,58,68)
                pygame.draw.rect(scr,oc,(ox,oy,ow,oh))
            for it in self.items:
                if not it.is_picked_up:
                    iix=int(mx+it.x*msc); iiy=int(my+it.y*msc)
                    ic=(205,205,82) if it.item_type=="WEAPON" else (52,205,52)
                    pygame.draw.rect(scr,ic,(iix,iiy,2,2))
            for h in self.population:
                if h.is_alive:
                    hx=int(mx+h.x*msc); hy=int(my+h.y*msc)
                    hc=(0,255,255) if cam.following==h else h.color
                    sz=3 if cam.following==h else 2
                    pygame.draw.rect(scr,hc,(hx,hy,sz,sz))
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
                
        if self.camera_shake > 0: self.camera_shake = max(0, self.camera_shake - 0.5)

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

        for h in self.population:
            h.update(self.map_size,self.items,self.population,self,self.safe_zone_radius,self.obstacles)

        new_dz = []
        for dz in self.danger_zones:
            dz["timer"] -= 1
            if dz["timer"] <= 0:
                if dz["type"] == "METEOR":
                    self._explosion(dz["x"], dz["y"], dz["dmg"], dz["shooter"], dz["radius"])
                    self.camera_shake = 12
                continue
            
            if dz["type"] == "POISON":
                if self.frame_count % 5 == 0:
                    ang = random.uniform(0, math.pi*2)
                    r = random.uniform(0, dz["radius"])
                    self.particles.append(SmokeParticle(dz["x"] + math.cos(ang)*r, dz["y"] + math.sin(ang)*r, (50,200,50)))
                for h in self.population:
                    if h.is_alive and h != dz["shooter"]:
                        if math.hypot(h.x-dz["x"], h.y-dz["y"]) < dz["radius"]:
                            h.poison_timer = max(h.poison_timer, 60)
            
            elif dz["type"] == "TORNADO":
                dz["x"] += dz.get("vx", 0)
                dz["y"] += dz.get("vy", 0)
                for _ in range(2): self.particles.append(WhirlwindParticle(dz["x"], dz["y"], (200,200,200)))
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

        self.particles=[p for p in self.particles if (p.update() or True) and p.life>0]
        if len(self.particles)>MAX_PARTICLES:
            self.particles=self.particles[-MAX_PARTICLES:]

        self.dmg_texts=[dt for dt in self.dmg_texts if (dt.update() or True) and dt.life>0]
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