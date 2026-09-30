import math
import random
import pygame
from config import HeroClass, HERO_CLASS_CONFIG
from utils import generate_random_name, draw_poly, draw_star, draw_glow, lerp_color
from particles import (DamageText, WhirlwindParticle, SparkParticle, 
                       ExplosionParticle, LightningParticle, SmokeParticle, 
                       GlowTrail, ShieldParticle, HealBurst, MeteorWarning, BloodParticle)
from projectiles import Projectile

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
                dist = math.hypot(self.locked_enemy.x-self.x, self.locked_enemy.y-self.y)
                t = dist / 20.0
                tx = self.locked_enemy.x + self.locked_enemy.vx * t
                ty = self.locked_enemy.y + self.locked_enemy.vy * t
                app.projectiles.append(Projectile(self.x,self.y, tx,ty, self.get_total_attack()*2,self,wc,20.0,"SNIPER"))

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

        if self.skill_active:
            self.skill_timer-=1
            if self.skill_timer<=0:
                self.skill_active=False; self.shield_active=False

        self.rotation += self.rotation_speed
        if self.committed_state=="COMBAT": self.rotation_speed=0.08
        else: self.rotation_speed=max(abs(self.rotation_speed),0.03)*random.choice([1,-1]) if random.random()<0.01 else self.rotation_speed

        eff=self.base_speed
        if self.frost_timer>0: eff *= 0.4
        if self.equipped_weapon:
            wc=self.equipped_weapon.weapon_class
            if wc=="MELEE": eff*=1.32
            elif wc=="RANGED": eff*=0.90
            elif wc=="MAGIC": eff*=0.95
            if self.equipped_weapon.name == "Minigun": eff*=0.6

        if self.dash_timer>0:
            self.speed=eff*4.2; self.dash_timer-=1
            if app.frame_count%2==0:
                app.particles.append(GlowTrail(self.x,self.y,self.glow_color,self.hero_size))
        else:
            self.speed=eff

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

        for p in app.projectiles:
            if p.shooter!=self and math.hypot(self.x-p.x,self.y-p.y)<72:
                if self.dash():
                    da=math.atan2(p.vy,p.vx)+(math.pi/2 if random.random()<0.5 else -math.pi/2)
                    self.x+=math.cos(da)*16; self.y+=math.sin(da)*16
                    break

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

        ci=None; mdi=165
        for it in items:
            if not it.is_picked_up:
                d=math.hypot(self.x-it.x,self.y-it.y)
                if it.item_type=="WEAPON" and self.equipped_weapon is None and d<mdi:
                    mdi=d; ci=it
                elif it.item_type=="POTION" and self.potions_count<2 and d<mdi:
                    mdi=d; ci=it
        self._pickup_nearby(items)

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

        if self.state_commit_timer>0: self.state_commit_timer-=1
        ds="PATROL"
        
        needs_cover = self.hp < self.max_hp * 0.35 and ce and mde < 300
        
        if is_outside or dtc>safe_zone_radius-55: ds="RUN ZONE"
        elif needs_cover: ds="FLEEING"
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
                    if cov and mde<250:
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

                if is_ranged:
                    if not can_hit: self.move_towards(ce.x,ce.y,nobs)
                    elif mde < ar*0.6: 
                        self.move_away(ce.x,ce.y,nobs)
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
                        
                        dist = math.hypot(ce.x-self.x, ce.y-self.y)
                        t = dist / 12.0
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
            self.vx, self.vy = 0, 0
            
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

        if cam.following==self or self.skill_active:
            gr=hs+10
            if self.skill_active:
                gr=int(hs+8+abs(math.sin(frame_count*0.12))*7)
            draw_glow(surface,self.glow_color,sx,sy,gr,130)

        if self.shield_active:
            pulse=abs(math.sin(frame_count*0.16))
            sr=hs+9+int(pulse*4)
            draw_poly(surface,(200,185,32),sx,sy,sr,6,self.rotation*0.45,2)
            draw_poly(surface,(255,220,60),sx,sy,sr+3,6,self.rotation*0.45+0.15,1)

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

        pygame.draw.circle(surface,(4,6,11),(sx+4,sy+4),hs)

        if self.hero_class==HeroClass.MAGE:
            draw_star(surface,dc,sx,sy,hs,hs*0.48,6,self.rotation)
            draw_star(surface,(min(255,dc[0]+80),min(255,dc[1]+80),min(255,dc[2]+80)), sx,sy,hs,hs*0.48,6,self.rotation,1)
        else:
            draw_poly(surface,dc,sx,sy,hs,self.shape_sides,self.rotation)
            oc=(min(255,dc[0]+82),min(255,dc[1]+82),min(255,dc[2]+82))
            draw_poly(surface,oc,sx,sy,hs,self.shape_sides,self.rotation,1)

        if self.equipped_weapon:
            wa=self.facing_angle
            wx=sx+int(math.cos(wa)*(hs+5))
            wy=sy+int(math.sin(wa)*(hs+5))
            pygame.draw.circle(surface,(22,22,28),(wx+2,wy+2),5)
            pygame.draw.circle(surface,self.equipped_weapon.color,(wx,wy),4)
            pygame.draw.circle(surface,(255,255,255),(wx,wy),2)

        bw=30
        hpr=max(0,self.hp/self.max_hp)
        hpc=lerp_color((200,32,32),lerp_color((235,185,22),(32,205,82),min(1.0,hpr*2)),max(0,hpr*2-1))
        pygame.draw.rect(surface,(8,8,14),(sx-bw//2-1,sy-hs-16,bw+2,6))
        pygame.draw.rect(surface,(62,0,0),(sx-bw//2,sy-hs-15,bw,4))
        pygame.draw.rect(surface,hpc,(sx-bw//2,sy-hs-15,int(bw*hpr),4))

        str_=max(0,self.stamina/self.max_stamina)
        pygame.draw.rect(surface,(0,42,105),(sx-bw//2,sy-hs-9,int(bw*str_),2))

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

            clabel=f"[{self.hero_class.value}] {self.state_label}"
            cs=sf.render(clabel,True,(155,155,185))
            surface.blit(cs,(sx-cs.get_width()//2,sy+hs+5))

            if self.equipped_weapon:
                ws=fonts["tiny"].render(self.equipped_weapon.name,True,(120,120,155))
                surface.blit(ws,(sx-ws.get_width()//2,sy+hs+17))
