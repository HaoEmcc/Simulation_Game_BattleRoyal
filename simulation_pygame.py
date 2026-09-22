import pygame
import math
import random
import sys

# ==================== 1. VẬT PHẨM & VŨ KHÍ ====================
class Item:
    def __init__(self, item_id, item_type, name, x, y):
        self.item_id = item_id
        self.item_type = item_type
        self.name = name
        self.x = x
        self.y = y
        self.is_picked_up = False

class Weapon(Item):
    def __init__(self, item_id, name, x, y, bonus_attack, attack_range, cooldown, weapon_class, color):
        super().__init__(item_id, "WEAPON", name, x, y)
        self.bonus_attack = bonus_attack
        self.attack_range = attack_range
        self.cooldown = cooldown
        self.weapon_class = weapon_class
        self.color = color

class HealthPotion(Item):
    def __init__(self, item_id, x, y, heal_amount=50.0):
        super().__init__(item_id, "POTION", "Bình Máu", x, y)
        self.heal_amount = heal_amount

def generate_random_weapon(item_id, map_size):
    x = random.uniform(80, map_size-80)
    y = random.uniform(80, map_size-80)
    w_type = random.choice([
        {"name": "Dao găm", "atk": 12, "rng": 22, "cd": 8, "cls": "MELEE", "col": (180, 180, 180)},
        {"name": "Kiếm", "atk": 20, "rng": 30, "cd": 15, "cls": "MELEE", "col": (200, 200, 200)},
        {"name": "Rìu chiến", "atk": 45, "rng": 25, "cd": 35, "cls": "MELEE", "col": (150, 100, 50)},
        {"name": "Giáo dài", "atk": 25, "rng": 50, "cd": 22, "cls": "MELEE", "col": (210, 180, 140)},
        {"name": "Shotgun", "atk": 40, "rng": 100, "cd": 45, "cls": "RANGED", "col": (169, 169, 169)},
        {"name": "Cung ngắn", "atk": 15, "rng": 180, "cd": 20, "cls": "RANGED", "col": (139, 69, 19)},
        {"name": "Nỏ", "atk": 30, "rng": 220, "cd": 40, "cls": "RANGED", "col": (100, 50, 20)},
        {"name": "Súng tỉa", "atk": 85, "rng": 350, "cd": 80, "cls": "RANGED", "col": (50, 50, 50)},
        {"name": "Trượng phép", "atk": 25, "rng": 150, "cd": 30, "cls": "RANGED", "col": (148, 0, 211)},
    ])
    return Weapon(item_id, w_type["name"], x, y, w_type["atk"], w_type["rng"], w_type["cd"], w_type["cls"], w_type["col"])

# ==================== 2. VẬT CẢN (OBSTACLES) ====================
class Obstacle:
    def __init__(self, x, y, w, h, obs_type="ROCK"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.obs_type = obs_type # ROCK, TREE, WALL
        
        if obs_type == "ROCK":
            self.color = (80, 80, 90)
        elif obs_type == "TREE":
            self.color = (30, 100, 30)
        else:
            self.color = (100, 90, 80)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    def collides_point(self, px, py, radius=10):
        """Kiểm tra va chạm giữa hình tròn (Hero) và hình chữ nhật (Obstacle)."""
        closest_x = max(self.x, min(px, self.x + self.w))
        closest_y = max(self.y, min(py, self.y + self.h))
        dist = math.hypot(px - closest_x, py - closest_y)
        return dist < radius
    
    def blocks_line(self, x1, y1, x2, y2):
        """Kiểm tra xem đường thẳng từ (x1,y1) đến (x2,y2) có bị chặn bởi obstacle không."""
        rect = self.get_rect()
        # Kiểm tra nhanh bằng cách chia đường thẳng thành 5 điểm
        for t in [0.2, 0.4, 0.5, 0.6, 0.8]:
            px = x1 + (x2 - x1) * t
            py = y1 + (y2 - y1) * t
            if rect.collidepoint(px, py):
                return True
        return False

def generate_obstacles(map_size, count=60):
    obstacles = []
    for _ in range(count):
        obs_type = random.choice(["ROCK", "ROCK", "TREE", "TREE", "WALL"])
        if obs_type == "WALL":
            w = random.randint(80, 200)
            h = random.randint(15, 25)
            if random.random() < 0.5:
                w, h = h, w
        elif obs_type == "TREE":
            size = random.randint(20, 40)
            w, h = size, size
        else: # ROCK
            w = random.randint(30, 70)
            h = random.randint(30, 70)
        
        x = random.uniform(100, map_size - 100 - w)
        y = random.uniform(100, map_size - 100 - h)
        
        # Không đặt vật cản quá gần tâm bản đồ (chừa chỗ cho vòng bo cuối)
        cx, cy = map_size / 2, map_size / 2
        if math.hypot(x + w/2 - cx, y + h/2 - cy) < 150:
            continue
            
        obstacles.append(Obstacle(x, y, w, h, obs_type))
    return obstacles

# ==================== 3. HIỆU ỨNG (ANIMATIONS) ====================
class Projectile:
    def __init__(self, x, y, target_x, target_y, damage, shooter, color, speed=8.0):
        self.x = x
        self.y = y
        self.damage = damage
        self.shooter = shooter
        self.color = color
        self.hitbox_radius = 4
        
        # Tính toán hướng và vận tốc (speed = 8.0 để đạn bay chậm, dễ nhìn)
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = (dx / dist) * speed
            self.vy = (dy / dist) * speed
        else:
            self.vx = speed
            self.vy = 0
            
        self.life = 80 # Tồn tại tối đa 80 frame nếu không trúng gì
class DamageText:
    def __init__(self, x, y, text, color=(255, 50, 50)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 60

class AttackAnim:
    def __init__(self, x1, y1, x2, y2, weapon_class, color):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.weapon_class = weapon_class
        self.color = color
        self.life = 25

class BloodParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(10, 20)

# ==================== 4. CAMERA ====================
class Camera:
    def __init__(self, screen_w, screen_h, map_size):
        self.x = 0.0
        self.y = 0.0
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.map_size = map_size
        self.speed = 15.0
        self.following = None 
    
    def center_on(self, target_x, target_y, smooth=False):
        tx = target_x - self.screen_w / 2
        ty = target_y - self.screen_h / 2
        
        if smooth:
            # Nội suy tuyến tính (Lerp) giúp camera di chuyển mượt
            self.x += (tx - self.x) * 0.08
            self.y += (ty - self.y) * 0.08
        else:
            self.x = tx
            self.y = ty
            
        self._clamp()
    
    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.following = None # Ngưng theo dõi khi di chuyển thủ công
        self._clamp()
    
    def _clamp(self):
        self.x = max(0, min(self.x, self.map_size - self.screen_w))
        self.y = max(0, min(self.y, self.map_size - self.screen_h))
        
    def world_to_screen(self, wx, wy):
        return int(wx - self.x), int(wy - self.y)
    
    def is_visible(self, wx, wy, margin=50):
        """Kiểm tra xem 1 điểm có nằm trong viewport không (để tối ưu rendering)."""
        return (-margin < wx - self.x < self.screen_w + margin and
                -margin < wy - self.y < self.screen_h + margin)
    
    def is_rect_visible(self, rx, ry, rw, rh, margin=50):
        return not (rx + rw < self.x - margin or rx > self.x + self.screen_w + margin or
                    ry + rh < self.y - margin or ry > self.y + self.screen_h + margin)

# ==================== 5. HERO ====================
class Hero:
    def __init__(self, hero_id):
        self.hero_id = hero_id
        
        self.max_hp = random.randint(100, 150)
        self.hp = self.max_hp
        self.max_stamina = 100
        self.stamina = self.max_stamina
        
        self.base_attack = random.randint(5, 15)
        self.defense = random.randint(1, 4)
        self.base_speed = random.uniform(1.2, 2.0) 
        self.speed = self.base_speed
        
        self.base_attack_range = 20.0
        self.base_cooldown = 20
        
        self.x = 0.0
        self.y = 0.0
        self.wander_target = None
        
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
        
        self.state_label = "IDLE"
        self.committed_state = None
        self.state_commit_timer = 0
        
        self.color = (random.randint(50,150), random.randint(100,200), random.randint(150,255))

    def reset(self, map_size):
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.x = random.uniform(150, map_size - 150)
        self.y = random.uniform(150, map_size - 150)
        self.equipped_weapon = None
        self.potions_count = 0
        self.kills = 0
        self.damage_dealt = 0
        self.is_alive = True
        self.hit_timer = 0
        self.attack_cooldown = 0
        self.dash_timer = 0
        self.wander_target = None
        self.state_label = "IDLE"
        self.committed_state = None
        self.state_commit_timer = 0

    def get_total_attack(self):
        return self.base_attack + (self.equipped_weapon.bonus_attack if self.equipped_weapon else 0)

    def get_attack_range(self):
        return self.equipped_weapon.attack_range if self.equipped_weapon else self.base_attack_range

    def get_cooldown(self):
        return self.equipped_weapon.cooldown if self.equipped_weapon else self.base_cooldown
        
    def evaluate_threat(self, enemy):
        my_power = self.hp * self.get_total_attack()
        enemy_power = max(1, enemy.hp * enemy.get_total_attack())
        score = my_power / enemy_power
        my_range = self.get_attack_range()
        enemy_range = enemy.get_attack_range()
        if enemy_range > my_range * 2:
            score *= 0.7
        return score
        
    def move_towards(self, target_x, target_y, obstacles=None):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            base_angle = math.atan2(dy, dx)
            # Quét các góc: Thẳng, lệch 30, 60, 90 độ hai bên để tìm đường lách
            angles_to_try = [0, 0.52, -0.52, 1.04, -1.04, 1.57, -1.57]
            
            for offset in angles_to_try:
                angle = base_angle + offset
                new_x = self.x + math.cos(angle) * self.speed
                new_y = self.y + math.sin(angle) * self.speed
                
                if not obstacles or not self._check_collision(new_x, new_y, obstacles):
                    self.x = new_x
                    self.y = new_y
                    return

    def move_away(self, target_x, target_y, obstacles=None):
        dx = self.x - target_x
        dy = self.y - target_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            base_angle = math.atan2(dy, dx)
            angles_to_try = [0, 0.52, -0.52, 1.04, -1.04, 1.57, -1.57]
            
            for offset in angles_to_try:
                angle = base_angle + offset
                new_x = self.x + math.cos(angle) * self.speed
                new_y = self.y + math.sin(angle) * self.speed
                
                if not obstacles or not self._check_collision(new_x, new_y, obstacles):
                    self.x = new_x
                    self.y = new_y
                    return

    def _check_collision(self, px, py, obstacles):
        for obs in obstacles:
            if obs.collides_point(px, py, 10):
                return True
        return False
            
    def dash(self):
        if self.stamina >= 50 and self.dash_timer <= 0:
            self.stamina -= 50
            self.dash_timer = 10 
            return True
        return False
    
    def _can_see(self, tx, ty, obstacles):
        """Kiểm tra tầm nhìn có bị vật cản chắn không."""
        for obs in obstacles:
            if obs.blocks_line(self.x, self.y, tx, ty):
                return False
        return True

    def _find_nearest_cover(self, enemy_x, enemy_y, obstacles):
        """Tìm vật cản gần nhất có thể núp phía sau (so với kẻ thù)."""
        best_obs = None
        best_dist = 9999
        for obs in obstacles:
            cx = obs.x + obs.w / 2
            cy = obs.y + obs.h / 2
            # Kiểm tra vật cản nằm giữa mình và kẻ thù
            dist_to_me = math.hypot(cx - self.x, cy - self.y)
            dist_enemy_to_obs = math.hypot(cx - enemy_x, cy - enemy_y)
            if dist_to_me < 200 and dist_to_me < best_dist:
                # Điểm núp: phía sau vật cản (xa kẻ thù nhất)
                best_dist = dist_to_me
                best_obs = obs
        return best_obs

    def _get_nearby_obstacles(self, obstacles):
        """Chỉ lấy các vật cản xung quanh bán kính 200px để tối ưu CPU"""
        nearby = []
        for obs in obstacles:
            if abs(obs.x - self.x) < 200 and abs(obs.y - self.y) < 200:
                nearby.append(obs)
        return nearby

    def update(self, map_size, items, heroes, app, safe_zone_radius, obstacles):
        if not self.is_alive: return

        nearby_obstacles = self._get_nearby_obstacles(obstacles)

        if self.stamina < self.max_stamina:
            self.stamina += 0.2
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hit_timer > 0:
            self.hit_timer -= 1
            
        if self.dash_timer > 0:
            self.speed = self.base_speed * 4.0 
            self.dash_timer -= 1
        else:
            self.speed = self.base_speed
            
        center_x, center_y = map_size/2, map_size/2
        dist_to_center = math.hypot(self.x - center_x, self.y - center_y)
        is_outside_zone = dist_to_center > safe_zone_radius
        
        if is_outside_zone:
            self.hp -= 0.5
            self.hit_timer = 2
            if app.frame_count % 15 == 0:
                app.dmg_texts.append(DamageText(self.x, self.y - 10, "-1", (100, 255, 100)))
            if self.hp <= 0:
                self.is_alive = False
                return

        # Dò tìm kẻ thù (Có hệ thống điểm ưu tiên & Khóa mục tiêu)
        if self.locked_enemy and not self.locked_enemy.is_alive:
            self.locked_enemy = None
            
        closest_enemy = None
        min_score = 99999
        min_dist_e = 250
        
        for h in heroes:
            if h != self and h.is_alive:
                dist = math.hypot(self.x - h.x, self.y - h.y)
                if dist < 350 and self._can_see(h.x, h.y, nearby_obstacles):
                    # Chấm điểm: Càng gần và càng ít máu thì điểm càng thấp (càng ưu tiên)
                    score = dist + (h.hp * 1.5)
                    
                    # Hệ thống chống do dự: Tăng ưu tiên (giảm 50% điểm) nếu đang là mục tiêu bị khóa
                    if h == self.locked_enemy:
                        score *= 0.5
                        
                    if score < min_score:
                        min_score = score
                        closest_enemy = h
                        min_dist_e = dist
                        
        self.locked_enemy = closest_enemy

        closest_item = None
        min_dist_i = 150 
        for it in items:
            if not it.is_picked_up:
                if it.item_type == "WEAPON" and self.equipped_weapon is None:
                    dist = math.hypot(self.x - it.x, self.y - it.y)
                    if dist < min_dist_i:
                        min_dist_i = dist
                        closest_item = it
                elif it.item_type == "POTION" and self.potions_count < 2:
                    dist = math.hypot(self.x - it.x, self.y - it.y)
                    if dist < min_dist_i:
                        min_dist_i = dist
                        closest_item = it

        self._pickup_nearby(items)

        # STATE MACHINE
        if self.state_commit_timer > 0:
            self.state_commit_timer -= 1

        desired_state = "PATROL"
        
        if is_outside_zone or dist_to_center > safe_zone_radius - 50:
            desired_state = "RUN ZONE"
        elif self.hp < self.max_hp * 0.5 and self.potions_count > 0:
            desired_state = "HEALING"
        elif closest_enemy and self.evaluate_threat(closest_enemy) < 0.8:
            desired_state = "FLEEING"
        elif closest_item and (not closest_enemy or min_dist_e > 120):
            desired_state = "LOOTING"
        elif closest_enemy:
            desired_state = "COMBAT"
        elif self.hp < self.max_hp:
            desired_state = "RESTING"

        priority = {"RUN ZONE": 7, "HEALING": 6, "FLEEING": 5, "LOOTING": 4, "COMBAT": 3, "RESTING": 2, "PATROL": 1, "IDLE": 0}
        current_priority = priority.get(self.committed_state, 0)
        desired_priority = priority.get(desired_state, 0)
        
        if self.state_commit_timer <= 0 or desired_priority > current_priority:
            if desired_state != self.committed_state:
                self.committed_state = desired_state
                self.state_commit_timer = 20
                self.rest_timer = 0
        
        self.state_label = self.committed_state

        # THỰC THI
        if self.committed_state == "RUN ZONE":
            self.move_towards(center_x, center_y, nearby_obstacles)
            
        elif self.committed_state == "HEALING":
            self.hp = min(self.max_hp, self.hp + 50)
            self.potions_count -= 1
            app.dmg_texts.append(DamageText(self.x, self.y - 20, "+50", (0, 255, 0)))
            self.committed_state = "PATROL"
            self.state_commit_timer = 0
            
        elif self.committed_state == "FLEEING":
            if closest_enemy:
                # Tìm vật cản gần nhất để núp
                cover = self._find_nearest_cover(closest_enemy.x, closest_enemy.y, nearby_obstacles)
                if cover and min_dist_e < 100:
                    # Chạy về phía sau vật cản
                    dx = (cover.x + cover.w/2) - closest_enemy.x
                    dy = (cover.y + cover.h/2) - closest_enemy.y
                    d = math.hypot(dx, dy)
                    if d > 0:
                        hide_x = cover.x + cover.w/2 + (dx/d) * 30
                        hide_y = cover.y + cover.h/2 + (dy/d) * 30
                        self.move_towards(hide_x, hide_y, nearby_obstacles)
                else:
                    if min_dist_e < 60:
                        self.dash()
                    self.move_away(closest_enemy.x, closest_enemy.y, nearby_obstacles)
            else:
                self.state_commit_timer = 0
                
        elif self.committed_state == "LOOTING":
            if closest_item:
                self.move_towards(closest_item.x, closest_item.y, nearby_obstacles)
            else:
                self.state_commit_timer = 0

        elif self.committed_state == "COMBAT":
            if closest_enemy:
                atk_range = self.get_attack_range()
                is_ranged = self.equipped_weapon and self.equipped_weapon.weapon_class == "RANGED"
                
                # 1. Kiểm tra tầm nhìn trước để quyết định cách di chuyển
                can_hit = self._can_see(closest_enemy.x, closest_enemy.y, nearby_obstacles)
                
                # 2. HỆ THỐNG DI CHUYỂN TRONG COMBAT (Sửa lỗi đứng im)
                if is_ranged:
                    if not can_hit:
                        # Khuất tầm nhìn -> Bắt buộc phải chạy tới tìm góc bắn
                        self.move_towards(closest_enemy.x, closest_enemy.y, nearby_obstacles)
                    elif min_dist_e < atk_range * 0.5:
                        # Bị áp sát quá gần -> Thả diều (Lùi lại)
                        self.move_away(closest_enemy.x, closest_enemy.y, nearby_obstacles)
                    elif min_dist_e > atk_range * 0.9:
                        # Hơi xa mục tiêu -> Tiến lên
                        self.move_towards(closest_enemy.x, closest_enemy.y, nearby_obstacles)
                    else:
                        # Đang ở tầm lý tưởng -> Di chuyển ngang (Strafe) để lách đạn
                        # Hướng lách phụ thuộc vào ID để mỗi nhân vật lách một kiểu
                        angle = math.atan2(closest_enemy.y - self.y, closest_enemy.x - self.x)
                        strafe_dir = math.pi / 2 if self.hero_id % 2 == 0 else -math.pi / 2
                        nx = self.x + math.cos(angle + strafe_dir) * (self.speed * 0.7)
                        ny = self.y + math.sin(angle + strafe_dir) * (self.speed * 0.7)
                        if not self._check_collision(nx, ny, nearby_obstacles):
                            self.x, self.y = nx, ny
                else: 
                    # MELEE (Vũ khí Cận chiến)
                    if not can_hit or min_dist_e > atk_range * 0.6:
                        # Luôn lao thẳng vào kẻ thù cho tới khi cực kỳ sát
                        self.move_towards(closest_enemy.x, closest_enemy.y, nearby_obstacles)
                    elif self.attack_cooldown > 0:
                        # Đã áp sát nhưng kỹ năng đang hồi -> Đi vòng tròn quanh kẻ thù
                        angle = math.atan2(closest_enemy.y - self.y, closest_enemy.x - self.x)
                        nx = self.x + math.cos(angle + math.pi/2) * (self.speed * 0.8)
                        ny = self.y + math.sin(angle + math.pi/2) * (self.speed * 0.8)
                        if not self._check_collision(nx, ny, nearby_obstacles):
                            self.x, self.y = nx, ny

                # 3. HỆ THỐNG TẤN CÔNG (Sử dụng đạn hoặc chém)
                if min_dist_e <= atk_range and self.attack_cooldown <= 0 and can_hit:
                    damage = max(1, self.get_total_attack() - closest_enemy.defense)
                    self.attack_cooldown = self.get_cooldown()
                    
                    w_cls = self.equipped_weapon.weapon_class if self.equipped_weapon else "MELEE"
                    w_col = self.equipped_weapon.color if self.equipped_weapon else (200,200,200)
                    
                    if is_ranged:
                        # Bắn đạn bay (Projectiles)
                        app.projectiles.append(Projectile(self.x, self.y, closest_enemy.x, closest_enemy.y, damage, self, w_col, speed=9.0))
                    else:
                        # Cận chiến: Sát thương lập tức
                        closest_enemy.hp -= damage
                        closest_enemy.hit_timer = 10 
                        self.damage_dealt += damage
                        
                        app.animations.append(AttackAnim(self.x, self.y, closest_enemy.x, closest_enemy.y, w_cls, w_col))
                        app.dmg_texts.append(DamageText(closest_enemy.x, closest_enemy.y - 20, str(damage)))
                        for _ in range(5):
                            app.particles.append(BloodParticle(closest_enemy.x, closest_enemy.y))

                        if closest_enemy.hp <= 0:
                            closest_enemy.is_alive = False
                            self.kills += 1
            else:
                self.state_commit_timer = 0

        elif self.committed_state == "RESTING":
            self.rest_timer += 1
            if self.rest_timer > 60: 
                self.hp = min(self.max_hp, self.hp + 0.1)
                if app.frame_count % 30 == 0:
                    app.dmg_texts.append(DamageText(self.x, self.y - 10, "+", (150, 255, 150)))
            
        elif self.committed_state == "PATROL":
            self.rest_timer = 0
            if self.wander_target is None or math.hypot(self.x - self.wander_target[0], self.y - self.wander_target[1]) < 20:
                rx = center_x + random.uniform(-safe_zone_radius*0.4, safe_zone_radius*0.4)
                ry = center_y + random.uniform(-safe_zone_radius*0.4, safe_zone_radius*0.4)
                self.wander_target = (rx, ry)
            self.move_towards(self.wander_target[0], self.wander_target[1], nearby_obstacles)

        self._clamp_bounds(map_size)
        
    def _clamp_bounds(self, map_size):
        self.x = max(10, min(self.x, map_size - 10))
        self.y = max(10, min(self.y, map_size - 10))
        
    def _pickup_nearby(self, items):
        for it in items:
            if not it.is_picked_up:
                dist = math.hypot(self.x - it.x, self.y - it.y)
                if dist < 20:
                    if it.item_type == "WEAPON" and self.equipped_weapon is None:
                        it.is_picked_up = True
                        self.equipped_weapon = it
                    elif it.item_type == "POTION" and self.potions_count < 2:
                        it.is_picked_up = True
                        self.potions_count += 1

# ==================== 6. SIMULATION MANAGER ====================
class ArenaApp:
    def __init__(self, map_size=3000, pop_size=80, max_frames=4000):
        pygame.init()
        self.map_size = map_size
        self.pop_size = pop_size
        self.max_frames = max_frames
        
        self.screen_w = 1000
        self.screen_h = 800
        self.ui_width = 260
        self.screen = pygame.display.set_mode((self.screen_w + self.ui_width, self.screen_h))
        pygame.display.set_caption("AI Battle Royale - V8 Obstacles & Camera")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 12)
        
        self.camera = Camera(self.screen_w, self.screen_h, map_size)
        self.camera.center_on(map_size/2, map_size/2)
        
        self.match_count = 1
        self.population = [Hero(i) for i in range(pop_size)]
        self.obstacles = []
        self.items = []
        self.dmg_texts = []
        self.animations = []
        self.particles = []
        self.projectiles = []
        self.frame_count = 0
        
        self.safe_zone_radius = self.map_size * 0.45
        
        self.render_enabled = True
        self.show_states = True
        self.show_minimap = True
        self.running = True
        
        self.obstacles = generate_obstacles(map_size, 80)
        self.spawn_items()
        for h in self.population:
            h.reset(self.map_size)
        self.match_over = False
        

    def spawn_items(self):
        self.items.clear()
        item_id = 0
        for _ in range(80): 
            self.items.append(generate_random_weapon(item_id, self.map_size))
            item_id += 1
        for _ in range(100): 
            x = random.uniform(80, self.map_size-80)
            y = random.uniform(80, self.map_size-80)
            self.items.append(HealthPotion(item_id, x, y, 40))
            item_id += 1

    def start_new_match(self):
        print(f"\n--- TRẬN {self.match_count} KẾT THÚC ---")
        winners = [h for h in self.population if h.is_alive]
        if winners:
            w = winners[0]
            w_name = w.equipped_weapon.name if w.equipped_weapon else "Tay không"
            print(f"🏆 Người chiến thắng: Player {w.hero_id} | Kills: {w.kills} | Dmg: {w.damage_dealt} | VK: {w_name}")
        else:
            print("💀 Hòa!")
        total_kills = sum(h.kills for h in self.population)
        print(f"📊 Tổng Kills: {total_kills} | Số người tham chiến: {self.pop_size}")
        
        self.match_count += 1
        self.frame_count = 0
        self.safe_zone_radius = self.map_size * 0.45
        self.dmg_texts.clear()
        self.animations.clear()
        self.particles.clear()
        self.projectiles.clear()
        
        self.obstacles = generate_obstacles(self.map_size, 80)
        
        for h in self.population:
            h.reset(self.map_size)
            h.hero_id = random.randint(100, 999)
        self.spawn_items()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.match_over:
                    self.match_over = False
                    self.start_new_match()
                elif event.key == pygame.K_SPACE:
                    self.render_enabled = not self.render_enabled 
                elif event.key == pygame.K_s:
                    self.show_states = not self.show_states
                elif event.key == pygame.K_m:
                    self.show_minimap = not self.show_minimap
                elif event.key == pygame.K_f:
                    # Theo dõi Top 1 Kill
                    alive = [h for h in self.population if h.is_alive]
                    if alive:
                        top = max(alive, key=lambda h: (h.kills, h.damage_dealt))
                        self.camera.following = top
                elif event.key == pygame.K_c:
                    # Về giữa bản đồ
                    self.camera.center_on(self.map_size/2, self.map_size/2)
                    self.camera.following = None
                    
        # Di chuyển camera bằng mũi tên
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s if False else pygame.K_DOWN]:
            dy += 1
        if dx != 0 or dy != 0:
            self.camera.move(dx, dy)
            
        # Nếu đang theo dõi 1 Hero
        if self.camera.following:
            if self.camera.following.is_alive:
                self.camera.center_on(self.camera.following.x, self.camera.following.y)
            else:
                self.camera.following = None

    def draw(self):
        if not self.render_enabled:
            return
            
        self.screen.fill((20, 25, 30))
        
        cam = self.camera
        
        # Lưới bản đồ
        grid_size = 200
        start_x = int(cam.x // grid_size) * grid_size
        start_y = int(cam.y // grid_size) * grid_size
        for gx in range(start_x, int(cam.x + self.screen_w) + grid_size, grid_size):
            sx, _ = cam.world_to_screen(gx, 0)
            pygame.draw.line(self.screen, (35, 40, 45), (sx, 0), (sx, self.screen_h))
        for gy in range(start_y, int(cam.y + self.screen_h) + grid_size, grid_size):
            _, sy = cam.world_to_screen(0, gy)
            pygame.draw.line(self.screen, (35, 40, 45), (0, sy), (self.screen_w, sy))
            
        # Vòng bo
        center_x, center_y = self.map_size/2, self.map_size/2
        scx, scy = cam.world_to_screen(center_x, center_y)
        pygame.draw.circle(self.screen, (50, 150, 255), (scx, scy), int(self.safe_zone_radius), 2)
        
        # Vật cản (Vẽ bóng đổ trước, vẽ hình sau)
        for obs in self.obstacles:
            if cam.is_rect_visible(obs.x, obs.y, obs.w, obs.h):
                sx, sy = cam.world_to_screen(obs.x, obs.y)
                # Vẽ bóng đổ (Shadow)
                pygame.draw.rect(self.screen, (10, 15, 20), (sx + 8, sy + 8, obs.w, obs.h), border_radius=4)
                # Vẽ khối vật cản (Bo góc mềm mại)
                pygame.draw.rect(self.screen, obs.color, (sx, sy, obs.w, obs.h), border_radius=4)
                # Viền sáng 3D
                pygame.draw.rect(self.screen, (min(255, obs.color[0]+40), min(255, obs.color[1]+40), min(255, obs.color[2]+40)), 
                                 (sx, sy, obs.w, obs.h), 2, border_radius=4)

        # Vật cản
        for obs in self.obstacles:
            if cam.is_rect_visible(obs.x, obs.y, obs.w, obs.h):
                sx, sy = cam.world_to_screen(obs.x, obs.y)
                pygame.draw.rect(self.screen, obs.color, (sx, sy, obs.w, obs.h))
                # Viền sáng hơn
                pygame.draw.rect(self.screen, (obs.color[0]+30, obs.color[1]+30, obs.color[2]+30), (sx, sy, obs.w, obs.h), 1)
        
        # Items
        for it in self.items:
            if not it.is_picked_up and cam.is_visible(it.x, it.y):
                sx, sy = cam.world_to_screen(it.x, it.y)
                if it.item_type == "WEAPON":
                    pygame.draw.rect(self.screen, it.color, (sx-4, sy-4, 8, 8))
                elif it.item_type == "POTION":
                    pygame.draw.circle(self.screen, (50, 255, 50), (sx, sy), 5)
                    pygame.draw.circle(self.screen, (255, 255, 255), (sx, sy), 2)
                    
        # Heroes
        alive_count = 0
        for h in self.population:
            if h.is_alive:
                alive_count += 1
                if not cam.is_visible(h.x, h.y):
                    continue
                    
                sx, sy = cam.world_to_screen(h.x, h.y)
                draw_color = (255, 50, 50) if h.hit_timer > 0 else h.color
                
                # Bóng đổ nhân vật
                pygame.draw.circle(self.screen, (10, 15, 20), (sx + 4, sy + 4), 10)
                
                if h.equipped_weapon: # Vẽ vũ khí
                    pygame.draw.circle(self.screen, (30, 30, 30), (sx+7, sy-5), 5) # Bóng vũ khí
                    pygame.draw.circle(self.screen, h.equipped_weapon.color, (sx+6, sy-6), 4)

                pygame.draw.circle(self.screen, draw_color, (sx, sy), 10)
                
                # Thanh máu (Có viền đen bọc ngoài)
                hp_ratio = max(0, h.hp / h.max_hp)
                pygame.draw.rect(self.screen, (0, 0, 0), (sx-13, sy-23, 26, 6)) # Viền đen
                pygame.draw.rect(self.screen, (200, 50, 50), (sx-12, sy-22, 24, 4)) # Nền đỏ
                pygame.draw.rect(self.screen, (50, 200, 50), (sx-12, sy-22, int(24*hp_ratio), 4)) # Máu xanh
                
                if h.equipped_weapon:
                    pygame.draw.circle(self.screen, h.equipped_weapon.color, (sx+6, sy-6), 4)

                pygame.draw.circle(self.screen, draw_color, (sx, sy), 10)
                
                hp_ratio = max(0, h.hp / h.max_hp)
                pygame.draw.rect(self.screen, (200,0,0), (sx-12, sy-22, 24, 4))
                pygame.draw.rect(self.screen, (0,200,0), (sx-12, sy-22, int(24*hp_ratio), 4))
                
                st_ratio = max(0, h.stamina / h.max_stamina)
                pygame.draw.rect(self.screen, (0,100,255), (sx-12, sy-16, int(24*st_ratio), 2))
                
                if self.show_states:
                    c_text = (255,255,255)
                    if h.state_label == "FLEEING": c_text = (255, 100, 100)
                    elif h.state_label == "COMBAT": c_text = (255, 200, 50)
                    elif h.state_label == "RESTING": c_text = (100, 255, 100)
                    st_surf = self.small_font.render(h.state_label, True, c_text)
                    self.screen.blit(st_surf, (sx-15, sy+12))
        
        # Particles
        for p in list(self.particles):
            if cam.is_visible(p.x, p.y):
                sx, sy = cam.world_to_screen(p.x, p.y)
                pygame.draw.rect(self.screen, (200, 0, 0), (sx, sy, 3, 3))
            p.x += p.vx
            p.y += p.vy
            p.life -= 1
            if p.life <= 0:
                self.particles.remove(p)

        # Animations
        for anim in list(self.animations):
            if cam.is_visible(anim.x1, anim.y1) or cam.is_visible(anim.x2, anim.y2):
                sx1, sy1 = cam.world_to_screen(anim.x1, anim.y1)
                sx2, sy2 = cam.world_to_screen(anim.x2, anim.y2)
                if anim.weapon_class == "RANGED":
                    progress = 1.0 - (anim.life / 25.0)
                    cx = sx1 + (sx2 - sx1) * progress
                    cy = sy1 + (sy2 - sy1) * progress
                    pygame.draw.circle(self.screen, anim.color, (int(cx), int(cy)), 4)
                else:
                    pygame.draw.line(self.screen, (255,255,255), (sx1, sy1), (sx2, sy2), 4)
            anim.life -= 1
            if anim.life <= 0:
                self.animations.remove(anim)
        # Vẽ đạn bay (Projectiles)
        for p in self.projectiles:
            if cam.is_visible(p.x, p.y):
                sx, sy = cam.world_to_screen(p.x, p.y)
                
                # Vẽ đuôi đạn (vệt sáng mờ phía sau)
                tail_x, tail_y = cam.world_to_screen(p.x - p.vx * 1.5, p.y - p.vy * 1.5)
                pygame.draw.line(self.screen, p.color, (sx, sy), (tail_x, tail_y), 3)
                
                # Vẽ đầu đạn
                pygame.draw.circle(self.screen, (255, 255, 255), (int(sx), int(sy)), p.hitbox_radius)
                pygame.draw.circle(self.screen, p.color, (int(sx), int(sy)), p.hitbox_radius, 1)

        # Damage Texts
        for dt in list(self.dmg_texts):
            if cam.is_visible(dt.x, dt.y):
                sx, sy = cam.world_to_screen(dt.x, dt.y)
                surface = self.font.render(dt.text, True, dt.color)
                self.screen.blit(surface, (sx, sy))
            dt.y -= 0.5 
            dt.life -= 1
            if dt.life <= 0:
                self.dmg_texts.remove(dt)

        # ==================== MINIMAP ====================
        if self.show_minimap:
            mm_size = 180
            mm_x = self.screen_w - mm_size - 10
            mm_y = self.screen_h - mm_size - 10
            mm_scale = mm_size / self.map_size
            
            pygame.draw.rect(self.screen, (10, 15, 20), (mm_x, mm_y, mm_size, mm_size))
            pygame.draw.rect(self.screen, (80, 80, 80), (mm_x, mm_y, mm_size, mm_size), 1)
            
            # Bo trên minimap
            pygame.draw.circle(self.screen, (50, 100, 200), 
                (int(mm_x + center_x * mm_scale), int(mm_y + center_y * mm_scale)), 
                int(self.safe_zone_radius * mm_scale), 1)
            
            # Obstacles trên minimap
            for obs in self.obstacles:
                ox = int(mm_x + obs.x * mm_scale)
                oy = int(mm_y + obs.y * mm_scale)
                ow = max(1, int(obs.w * mm_scale))
                oh = max(1, int(obs.h * mm_scale))
                pygame.draw.rect(self.screen, (60, 60, 60), (ox, oy, ow, oh))
            
            # Heroes trên minimap
            for h in self.population:
                if h.is_alive:
                    hx = int(mm_x + h.x * mm_scale)
                    hy = int(mm_y + h.y * mm_scale)
                    pygame.draw.rect(self.screen, h.color, (hx, hy, 2, 2))
            
            # Viewport trên minimap
            vx = int(mm_x + cam.x * mm_scale)
            vy = int(mm_y + cam.y * mm_scale)
            vw = int(self.screen_w * mm_scale)
            vh = int(self.screen_h * mm_scale)
            pygame.draw.rect(self.screen, (255, 255, 255), (vx, vy, vw, vh), 1)
                
        # ==================== INFO BOARD ====================
        board_x = self.screen_w
        pygame.draw.rect(self.screen, (15, 20, 25), (board_x, 0, self.ui_width, self.screen_h))
        pygame.draw.line(self.screen, (80, 80, 80), (board_x, 0), (board_x, self.screen_h), 2)
        
        y_off = 15
        title = self.title_font.render(f"TRẬN #{self.match_count}", True, (255,215,0))
        self.screen.blit(title, (board_x + 15, y_off))
        y_off += 35
        
        info_lines = [
            f"Còn sống: {alive_count} / {self.pop_size}",
            f"Bo: {int(self.safe_zone_radius)}m",
            f"Map: {self.map_size}x{self.map_size}",
            "",
            "Phím tắt:",
            "WASD/Mũi tên: Di chuyển cam",
            "F: Theo dõi Top 1",
            "C: Về giữa bản đồ",
            "M: Bật/Tắt Minimap",
            "S: Bật/Tắt Trạng thái",
            "Space: Bật/Tắt Render",
        ]
        for text in info_lines:
            surface = self.small_font.render(text, True, (180, 180, 180))
            self.screen.blit(surface, (board_x + 15, y_off))
            y_off += 18
            
        y_off += 15
        self.screen.blit(self.font.render("--- LEADERBOARD ---", True, (255,255,255)), (board_x + 15, y_off))
        y_off += 25
        
        sorted_heroes = sorted([h for h in self.population if h.is_alive], key=lambda x: (x.kills, x.damage_dealt), reverse=True)
        
        for i, h in enumerate(sorted_heroes[:5]): 
            w_name = h.equipped_weapon.name if h.equipped_weapon else "Không"
            c = (0, 255, 0) if i == 0 else (200, 200, 200)
            
            self.screen.blit(self.font.render(f"#{i+1} P{h.hero_id} ({h.kills}K)", True, c), (board_x + 15, y_off))
            y_off += 16
            self.screen.blit(self.small_font.render(f"HP:{int(h.hp)} VK:{w_name} [{h.state_label}]", True, (140, 140, 140)), (board_x + 25, y_off))
            y_off += 22

        # ==================== END MATCH STATS ====================
        if self.match_over:
            # Làm mờ nền
            overlay = pygame.Surface((self.screen_w + self.ui_width, self.screen_h))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Vẽ bảng
            cx = (self.screen_w + self.ui_width) // 2
            pygame.draw.rect(self.screen, (30, 35, 40), (cx - 250, 100, 500, 550), border_radius=10)
            pygame.draw.rect(self.screen, (255, 215, 0), (cx - 250, 100, 500, 550), 2, border_radius=10)
            
            title = self.title_font.render(f"KẾT QUẢ TRẬN {self.match_count}", True, (255, 215, 0))
            self.screen.blit(title, (cx - title.get_width()//2, 130))
            
            headers = self.font.render("Hạng    Người chơi      Kills    Sát thương    Vũ khí", True, (150, 150, 150))
            self.screen.blit(headers, (cx - 200, 180))
            pygame.draw.line(self.screen, (100, 100, 100), (cx - 210, 200), (cx + 210, 200))
            
            sorted_heroes = sorted(self.population, key=lambda x: (x.is_alive, x.kills, x.damage_dealt), reverse=True)
            
            y_stat = 220
            for i, h in enumerate(sorted_heroes[:10]):
                w_name = h.equipped_weapon.name if h.equipped_weapon else "Tay không"
                color = (0, 255, 0) if h.is_alive else (200, 200, 200)
                if i == 0: color = (255, 215, 0) # Top 1 màu vàng
                
                row_text = f"#{i+1:<7} P{h.hero_id:<14} {h.kills:<8} {int(h.damage_dealt):<13} {w_name}"
                stat_surf = self.font.render(row_text, True, color)
                self.screen.blit(stat_surf, (cx - 200, y_stat))
                y_stat += 30
                
            prompt = self.title_font.render("NHẤN [ENTER] ĐỂ BẮT ĐẦU VÁN MỚI", True, (255, 255, 255))
            self.screen.blit(prompt, (cx - prompt.get_width()//2, 580))
            
        pygame.display.flip()

    def update(self):
        if self.match_over:
            return # Dừng update game khi hiển thị bảng thống kê

        alive_count = sum(1 for h in self.population if h.is_alive)
        if alive_count <= 1 or self.frame_count >= self.max_frames:
            self.match_over = True # Kích hoạt bảng thống kê thay vì reset ngay
            return
            
        shrink_rate = (self.map_size * 0.45) / (self.max_frames * 0.8) 
        self.safe_zone_radius = max(0, self.safe_zone_radius - shrink_rate)
            
        for h in self.population:
            h.update(self.map_size, self.items, self.population, self, self.safe_zone_radius, self.obstacles)

        # Cập nhật đường đạn bay và va chạm
        for p in list(self.projectiles):
            p.x += p.vx
            p.y += p.vy
            p.life -= 1
            hit = False
            
            # 1. Đạn va chạm vật cản
            for obs in self.obstacles:
                if obs.collides_point(p.x, p.y, p.hitbox_radius):
                    hit = True
                    break
                    
            # 2. Đạn va chạm Hero (Hitbox)
            if not hit:
                for h in self.population:
                    if h.is_alive and h != p.shooter:
                        dist = math.hypot(p.x - h.x, p.y - h.y)
                        if dist < 10 + p.hitbox_radius:  # 10 là bán kính của Hero
                            # Đạn trúng mục tiêu, gây sát thương
                            h.hp -= p.damage
                            h.hit_timer = 10
                            p.shooter.damage_dealt += p.damage
                            
                            self.dmg_texts.append(DamageText(h.x, h.y - 20, str(p.damage)))
                            for _ in range(5):
                                self.particles.append(BloodParticle(h.x, h.y))
                                
                            if h.hp <= 0:
                                h.is_alive = False
                                p.shooter.kills += 1
                                
                            hit = True
                            break # Chỉ trúng 1 mục tiêu
                            
            # Xóa đạn nếu trúng đích hoặc hết thời gian bay
            if hit or p.life <= 0:
                if p in self.projectiles:
                    self.projectiles.remove(p)
            
        self.frame_count += 1

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            if self.render_enabled:
                self.clock.tick(60) 
                
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = ArenaApp(map_size=6000, pop_size=10, max_frames=4000)
    app.run()
