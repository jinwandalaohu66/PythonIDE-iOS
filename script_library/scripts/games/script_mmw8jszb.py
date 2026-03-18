# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
# 霓虹塔防 - Neon Tower Defense
import scene
import math
import random

# ---------- constants ----------
TILE = 40
TOWER_COSTS = {'basic': 50, 'sniper': 100, 'splash': 150}
TOWER_RANGES = {'basic': 90, 'sniper': 200, 'splash': 120}
TOWER_DAMAGE = {'basic': 12, 'sniper': 40, 'splash': 18}
TOWER_COOLDOWNS = {'basic': 0.6, 'sniper': 1.4, 'splash': 1.0}
TOWER_COLORS = {
    'basic': (0.2, 1.0, 0.4),
    'sniper': (0.3, 0.6, 1.0),
    'splash': (1.0, 0.6, 0.15),
}
SPLASH_RADIUS = 55

ENEMY_TYPES = {
    'normal': {'hp': 80, 'speed': 50, 'color': (1.0, 0.3, 0.3), 'reward': 15, 'radius': 8},
    'fast':   {'hp': 45, 'speed': 100, 'color': (1.0, 1.0, 0.2), 'reward': 20, 'radius': 6},
    'tank':   {'hp': 250, 'speed': 30, 'color': (0.8, 0.2, 1.0), 'reward': 40, 'radius': 12},
}

WAVE_DEFS = [
    [('normal', 8)],
    [('normal', 6), ('fast', 4)],
    [('normal', 8), ('fast', 6)],
    [('tank', 3), ('normal', 8)],
    [('fast', 10), ('tank', 3)],
    [('normal', 10), ('fast', 8), ('tank', 4)],
    [('tank', 6), ('fast', 10)],
    [('normal', 12), ('fast', 10), ('tank', 6)],
    [('tank', 8), ('fast', 12), ('normal', 10)],
    [('tank', 10), ('fast', 15), ('normal', 12)],
]
TOTAL_WAVES = len(WAVE_DEFS)


def dist(ax, ay, bx, by):
    return math.hypot(bx - ax, by - ay)


def lerp_pt(p0, p1, t):
    return (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)


class Projectile:
    def __init__(self, sx, sy, target, damage, is_splash=False):
        self.x, self.y = sx, sy
        self.target = target
        self.damage = damage
        self.is_splash = is_splash
        self.speed = 350
        self.alive = True

    def update(self, dt, enemies):
        if not self.target.alive:
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        d = math.hypot(dx, dy)
        if d < 8:
            self._hit(enemies)
            return
        vx, vy = dx / d * self.speed, dy / d * self.speed
        self.x += vx * dt
        self.y += vy * dt

    def _hit(self, enemies):
        self.alive = False
        if self.is_splash:
            for e in enemies:
                if e.alive and dist(self.x, self.y, e.x, e.y) < SPLASH_RADIUS:
                    e.take_damage(self.damage)
        else:
            self.target.take_damage(self.damage)


class Enemy:
    def __init__(self, etype, path):
        info = ENEMY_TYPES[etype]
        self.etype = etype
        self.max_hp = info['hp']
        self.hp = self.max_hp
        self.speed = info['speed']
        self.color = info['color']
        self.reward = info['reward']
        self.radius = info['radius']
        self.path = path
        self.seg = 0
        self.seg_t = 0.0
        self.x, self.y = path[0]
        self.alive = True
        self.reached_end = False

    def update(self, dt):
        if not self.alive:
            return
        if self.seg >= len(self.path) - 1:
            self.alive = False
            self.reached_end = True
            return
        p0 = self.path[self.seg]
        p1 = self.path[self.seg + 1]
        seg_len = dist(p0[0], p0[1], p1[0], p1[1])
        if seg_len < 0.1:
            self.seg += 1
            return
        self.seg_t += (self.speed * dt) / seg_len
        while self.seg_t >= 1.0 and self.seg < len(self.path) - 1:
            self.seg_t -= 1.0
            self.seg += 1
            if self.seg >= len(self.path) - 1:
                self.alive = False
                self.reached_end = True
                return
        p0 = self.path[self.seg]
        p1 = self.path[self.seg + 1] if self.seg + 1 < len(self.path) else p0
        self.x, self.y = lerp_pt(p0, p1, self.seg_t)

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    @property
    def progress(self):
        return self.seg + self.seg_t


class Tower:
    def __init__(self, ttype, gx, gy, cx, cy):
        self.ttype = ttype
        self.gx, self.gy = gx, gy
        self.x, self.y = cx, cy
        self.range = TOWER_RANGES[ttype]
        self.damage = TOWER_DAMAGE[ttype]
        self.cooldown = TOWER_COOLDOWNS[ttype]
        self.timer = 0.0
        self.color = TOWER_COLORS[ttype]

    def update(self, dt, enemies, projectiles):
        self.timer -= dt
        if self.timer > 0:
            return
        best = None
        best_prog = -1
        for e in enemies:
            if e.alive and dist(self.x, self.y, e.x, e.y) <= self.range:
                if e.progress > best_prog:
                    best_prog = e.progress
                    best = e
        if best:
            self.timer = self.cooldown
            projectiles.append(Projectile(
                self.x, self.y, best, self.damage,
                is_splash=(self.ttype == 'splash')
            ))


class NeonTowerDefense(scene.Scene):

    def setup(self):
        self.game_state = 'playing'
        self.gold = 200
        self.lives = 20
        self.score = 0
        self.wave_num = 0
        self.spawning = False
        self.spawn_queue = []
        self.spawn_timer = 0.0
        self.wave_active = False
        self.wave_clear_timer = 0.0
        self.between_waves = True

        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.particles = []
        self.selected_tower_type = 'basic'
        self.selected_tower_obj = None

        sa = self.safe_area_insets
        self.ox = sa.left + 10
        self.oy = sa.bottom + 60
        self.play_w = self.size.w - sa.left - sa.right - 20
        self.play_h = self.size.h - sa.top - sa.bottom - 120

        self._build_path()
        self._build_grid()
        self._start_wave()

    # ---- path & grid ----
    def _build_path(self):
        w, h = self.play_w, self.play_h
        ox, oy = self.ox, self.oy
        rows = 5
        margin_y = h * 0.10
        usable_h = h - margin_y * 2
        row_h = usable_h / (rows - 1)
        pts = []
        x_margin = 30
        for i in range(rows):
            y = oy + margin_y + i * row_h
            if i % 2 == 0:
                pts.append((ox + x_margin, y))
                pts.append((ox + w - x_margin, y))
            else:
                pts.append((ox + w - x_margin, y))
                pts.append((ox + x_margin, y))
        self.path_points = pts

    def _build_grid(self):
        self.occupied = set()
        for i in range(len(self.path_points) - 1):
            p0 = self.path_points[i]
            p1 = self.path_points[i + 1]
            seg_len = dist(p0[0], p0[1], p1[0], p1[1])
            steps = int(seg_len / (TILE * 0.5)) + 1
            for s in range(steps + 1):
                t = s / max(steps, 1)
                px, py = lerp_pt(p0, p1, t)
                gx = int((px - self.ox) / TILE)
                gy = int((py - self.oy) / TILE)
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        self.occupied.add((gx + dx, gy + dy))

    # ---- waves ----
    def _start_wave(self):
        if self.wave_num >= TOTAL_WAVES:
            self.game_state = 'victory'
            return
        self.spawn_queue = []
        for etype, count in WAVE_DEFS[self.wave_num]:
            self.spawn_queue.extend([etype] * count)
        random.shuffle(self.spawn_queue)
        self.spawning = True
        self.spawn_timer = 0.0
        self.wave_active = True
        self.between_waves = False

    def _spawn_enemy(self):
        if not self.spawn_queue:
            self.spawning = False
            return
        etype = self.spawn_queue.pop(0)
        self.enemies.append(Enemy(etype, self.path_points))
        self.spawn_timer = 0.8 if etype != 'fast' else 0.5

    # ---- update ----
    def update(self):
        if self.game_state != 'playing':
            return
        dt = self.dt

        if self.spawning:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self._spawn_enemy()

        for e in self.enemies:
            e.update(dt)

        for t in self.towers:
            t.update(dt, self.enemies, self.projectiles)

        for p in self.projectiles:
            p.update(dt, self.enemies)
        self.projectiles = [p for p in self.projectiles if p.alive]

        for e in list(self.enemies):
            if not e.alive:
                if e.reached_end:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_state = 'gameover'
                        return
                else:
                    self.gold += e.reward
                    self.score += e.reward
                    self._add_particles(e.x, e.y, e.color)
        self.enemies = [e for e in self.enemies if e.alive]

        self._update_particles(dt)

        if self.wave_active and not self.spawning and not self.enemies:
            self.wave_num += 1
            if self.wave_num >= TOTAL_WAVES:
                self.game_state = 'victory'
                return
            self.between_waves = True
            self.wave_clear_timer = 2.5
            self.wave_active = False

        if self.between_waves:
            self.wave_clear_timer -= dt
            if self.wave_clear_timer <= 0:
                self._start_wave()

    # ---- particles ----
    def _add_particles(self, x, y, color):
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(30, 80)
            self.particles.append({
                'x': x, 'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.uniform(0.3, 0.7),
                'max_life': 0.7,
                'color': color,
            })

    def _update_particles(self, dt):
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt
        self.particles = [p for p in self.particles if p['life'] > 0]

    # ---- drawing ----
    def draw(self):
        scene.background(0.05, 0.05, 0.12)
        if self.game_state == 'gameover':
            self._draw_gameover()
            return
        if self.game_state == 'victory':
            self._draw_victory()
            return

        self._draw_path()
        self._draw_towers()
        self._draw_enemies()
        self._draw_projectiles()
        self._draw_particles()
        self._draw_hud()
        self._draw_shop()
        if self.selected_tower_obj:
            self._draw_range(self.selected_tower_obj)
        if self.between_waves and self.wave_num < TOTAL_WAVES:
            self._draw_wave_banner()

    def _draw_path(self):
        scene.no_fill()
        scene.stroke(0.15, 0.8, 0.9, 0.35)
        scene.stroke_weight(TILE * 1.2)
        for i in range(len(self.path_points) - 1):
            p0 = self.path_points[i]
            p1 = self.path_points[i + 1]
            scene.line(p0[0], p0[1], p1[0], p1[1])

        scene.stroke(0.1, 0.6, 0.7, 0.6)
        scene.stroke_weight(2)
        for i in range(len(self.path_points) - 1):
            p0 = self.path_points[i]
            p1 = self.path_points[i + 1]
            scene.line(p0[0], p0[1], p1[0], p1[1])
        scene.no_stroke()

        sp = self.path_points[0]
        ep = self.path_points[-1]
        scene.fill(0.2, 1.0, 0.4, 0.7)
        scene.ellipse(sp[0] - 10, sp[1] - 10, 20, 20)
        scene.fill(1.0, 0.2, 0.2, 0.7)
        scene.ellipse(ep[0] - 10, ep[1] - 10, 20, 20)

    def _draw_towers(self):
        scene.no_stroke()
        for t in self.towers:
            r, g, b = t.color
            scene.fill(r, g, b, 0.15)
            scene.ellipse(t.x - 18, t.y - 18, 36, 36)
            scene.fill(r, g, b, 1.0)
            scene.rect(t.x - 8, t.y - 8, 16, 16)
            scene.fill(r * 0.5, g * 0.5, b * 0.5, 1.0)
            scene.rect(t.x - 4, t.y - 4, 8, 8)
            if t.ttype == 'sniper':
                scene.stroke(r, g, b, 0.8)
                scene.stroke_weight(2)
                scene.line(t.x, t.y, t.x, t.y + 14)
                scene.no_stroke()
            elif t.ttype == 'splash':
                scene.fill(r, g, b, 0.5)
                scene.ellipse(t.x - 12, t.y - 12, 24, 24)

    def _draw_range(self, tower):
        scene.no_fill()
        scene.stroke(tower.color[0], tower.color[1], tower.color[2], 0.25)
        scene.stroke_weight(1.5)
        r = tower.range
        scene.ellipse(tower.x - r, tower.y - r, r * 2, r * 2)
        scene.no_stroke()

    def _draw_enemies(self):
        scene.no_stroke()
        for e in self.enemies:
            r, g, b = e.color
            rad = e.radius
            scene.fill(r, g, b, 0.25)
            scene.ellipse(e.x - rad - 3, e.y - rad - 3, (rad + 3) * 2, (rad + 3) * 2)
            scene.fill(r, g, b, 1.0)
            scene.ellipse(e.x - rad, e.y - rad, rad * 2, rad * 2)
            bar_w = rad * 2.5
            bar_h = 3
            bx = e.x - bar_w / 2
            by = e.y + rad + 4
            scene.fill(0.3, 0.0, 0.0, 0.8)
            scene.rect(bx, by, bar_w, bar_h)
            hp_ratio = max(e.hp / e.max_hp, 0)
            if hp_ratio > 0.5:
                scene.fill(0.2, 1.0, 0.3, 0.9)
            elif hp_ratio > 0.25:
                scene.fill(1.0, 0.8, 0.1, 0.9)
            else:
                scene.fill(1.0, 0.2, 0.2, 0.9)
            scene.rect(bx, by, bar_w * hp_ratio, bar_h)

    def _draw_projectiles(self):
        scene.no_stroke()
        for p in self.projectiles:
            if p.is_splash:
                scene.fill(1.0, 0.6, 0.15, 0.9)
                scene.ellipse(p.x - 4, p.y - 4, 8, 8)
            else:
                scene.fill(1.0, 1.0, 1.0, 0.95)
                scene.ellipse(p.x - 3, p.y - 3, 6, 6)

    def _draw_particles(self):
        scene.no_stroke()
        for p in self.particles:
            a = max(p['life'] / p['max_life'], 0)
            r, g, b = p['color']
            scene.fill(r, g, b, a * 0.8)
            scene.ellipse(p['x'] - 2, p['y'] - 2, 4, 4)

    def _draw_hud(self):
        sa = self.safe_area_insets
        top_y = self.size.h - sa.top - 30

        scene.fill(0.1, 0.1, 0.18, 0.85)
        scene.rect(0, self.size.h - sa.top - 45, self.size.w, 45 + sa.top)

        scene.tint(0.9, 0.9, 0.2, 1.0)
        scene.text(f'金币: {self.gold}', 'Helvetica-Bold', 16,
                   sa.left + 15, top_y, 7)
        scene.tint(1.0, 0.3, 0.3, 1.0)
        scene.text(f'生命: {self.lives}', 'Helvetica-Bold', 16,
                   self.size.w / 2 - 60, top_y, 7)
        scene.tint(0.3, 0.8, 1.0, 1.0)
        scene.text(f'波次: {self.wave_num + 1}/{TOTAL_WAVES}', 'Helvetica-Bold', 16,
                   self.size.w / 2 + 40, top_y, 7)
        scene.tint(0.6, 1.0, 0.6, 1.0)
        scene.text(f'分数: {self.score}', 'Helvetica-Bold', 16,
                   self.size.w - sa.right - 15, top_y, 9)
        scene.no_tint()

    def _draw_shop(self):
        sa = self.safe_area_insets
        y = sa.bottom + 5
        bw, bh = 80, 42
        gap = 12
        total_w = bw * 3 + gap * 2
        sx = (self.size.w - total_w) / 2

        scene.fill(0.08, 0.08, 0.15, 0.9)
        scene.rect(0, 0, self.size.w, sa.bottom + 55)

        types = ['basic', 'sniper', 'splash']
        labels = ['基础', '狙击', '溅射']
        for i, (tt, label) in enumerate(zip(types, labels)):
            bx = sx + i * (bw + gap)
            r, g, b = TOWER_COLORS[tt]
            selected = (self.selected_tower_type == tt)
            if selected:
                scene.fill(r, g, b, 0.35)
                scene.stroke(r, g, b, 0.9)
                scene.stroke_weight(2)
            else:
                scene.fill(0.15, 0.15, 0.22, 0.8)
                scene.stroke(r, g, b, 0.4)
                scene.stroke_weight(1)
            scene.rect(bx, y, bw, bh)
            scene.no_stroke()

            cost = TOWER_COSTS[tt]
            can_afford = self.gold >= cost
            alpha = 1.0 if can_afford else 0.4
            scene.tint(r, g, b, alpha)
            scene.text(label, 'Helvetica-Bold', 13, bx + bw / 2, y + bh - 10, 8)
            scene.tint(0.9, 0.85, 0.3, alpha)
            scene.text(f'{cost}G', 'Helvetica', 11, bx + bw / 2, y + 8, 8)
            scene.no_tint()

    def _draw_wave_banner(self):
        cx, cy = self.size.w / 2, self.size.h / 2
        scene.fill(0.05, 0.05, 0.12, 0.7)
        scene.rect(cx - 140, cy - 30, 280, 60)
        scene.stroke(0.1, 0.8, 1.0, 0.6)
        scene.stroke_weight(1.5)
        scene.rect(cx - 140, cy - 30, 280, 60)
        scene.no_stroke()
        scene.tint(0.2, 1.0, 0.9, 1.0)
        scene.text(f'第 {self.wave_num + 1} 波即将来临...',
                   'Helvetica-Bold', 20, cx, cy, 5)
        scene.no_tint()

    def _draw_gameover(self):
        cx, cy = self.size.w / 2, self.size.h / 2
        scene.fill(0.0, 0.0, 0.0, 0.7)
        scene.rect(0, 0, self.size.w, self.size.h)
        scene.tint(1.0, 0.2, 0.2, 1.0)
        scene.text('游戏结束', 'Helvetica-Bold', 36, cx, cy + 40, 5)
        scene.tint(0.8, 0.8, 0.8, 1.0)
        scene.text(f'最终分数: {self.score}', 'Helvetica-Bold', 22, cx, cy - 10, 5)
        scene.tint(0.5, 1.0, 0.8, 1.0)
        scene.text('点击重新开始', 'Helvetica', 18, cx, cy - 55, 5)
        scene.no_tint()

    def _draw_victory(self):
        cx, cy = self.size.w / 2, self.size.h / 2
        pulse = 0.7 + 0.3 * math.sin(self.t * 3)
        scene.fill(0.0, 0.0, 0.0, 0.7)
        scene.rect(0, 0, self.size.w, self.size.h)
        scene.tint(0.3, 1.0, 0.5, pulse)
        scene.text('胜利!', 'Helvetica-Bold', 42, cx, cy + 40, 5)
        scene.tint(0.9, 0.85, 0.3, 1.0)
        scene.text(f'总分: {self.score}  剩余生命: {self.lives}',
                   'Helvetica-Bold', 20, cx, cy - 10, 5)
        scene.tint(0.5, 1.0, 0.8, 1.0)
        scene.text('点击重新开始', 'Helvetica', 18, cx, cy - 55, 5)
        scene.no_tint()

    # ---- input ----
    def touch_began(self, touch):
        if self.game_state in ('gameover', 'victory'):
            self.setup()
            return

        tx, ty = touch.location.x, touch.location.y
        sa = self.safe_area_insets

        shop_top = sa.bottom + 55
        if ty < shop_top:
            self._handle_shop_tap(tx, ty)
            return

        hud_bottom = self.size.h - sa.top - 45
        if ty > hud_bottom:
            return

        for t in self.towers:
            if dist(tx, ty, t.x, t.y) < 20:
                self.selected_tower_obj = t if self.selected_tower_obj != t else None
                return

        self.selected_tower_obj = None
        self._try_place_tower(tx, ty)

    def touch_moved(self, touch):
        pass

    def touch_ended(self, touch):
        pass

    def _handle_shop_tap(self, tx, ty):
        sa = self.safe_area_insets
        y = sa.bottom + 5
        bw, bh = 80, 42
        gap = 12
        total_w = bw * 3 + gap * 2
        sx = (self.size.w - total_w) / 2

        types = ['basic', 'sniper', 'splash']
        for i, tt in enumerate(types):
            bx = sx + i * (bw + gap)
            if bx <= tx <= bx + bw and y <= ty <= y + bh:
                self.selected_tower_type = tt
                return

    def _try_place_tower(self, tx, ty):
        tt = self.selected_tower_type
        cost = TOWER_COSTS[tt]
        if self.gold < cost:
            return

        gx = int((tx - self.ox) / TILE)
        gy = int((ty - self.oy) / TILE)

        if gx < 0 or gy < 0:
            return
        if gx * TILE + self.ox > self.ox + self.play_w:
            return
        if gy * TILE + self.oy > self.oy + self.play_h:
            return

        if (gx, gy) in self.occupied:
            return

        for t in self.towers:
            if t.gx == gx and t.gy == gy:
                return

        cx = self.ox + gx * TILE + TILE / 2
        cy = self.oy + gy * TILE + TILE / 2
        self.towers.append(Tower(tt, gx, gy, cx, cy))
        self.occupied.add((gx, gy))
        self.gold -= cost


scene.run(NeonTowerDefense())
