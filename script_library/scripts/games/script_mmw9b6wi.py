# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
# 水果忍者 - Fruit Ninja
# A Pythonista-compatible Scene game

import scene
import random
import math

FRUITS = [
    {'name': 'apple',      'color': (0.9, 0.15, 0.15), 'splash': (1.0, 0.3, 0.2),  'emoji': '🍎'},
    {'name': 'orange',     'color': (1.0, 0.6, 0.0),   'splash': (1.0, 0.7, 0.2),  'emoji': '🍊'},
    {'name': 'watermelon', 'color': (0.2, 0.8, 0.3),   'splash': (0.3, 0.9, 0.4),  'emoji': '🍉'},
    {'name': 'grape',      'color': (0.6, 0.2, 0.8),   'splash': (0.7, 0.3, 0.9),  'emoji': '🍇'},
    {'name': 'lemon',      'color': (1.0, 0.9, 0.2),   'splash': (1.0, 0.95, 0.4), 'emoji': '🍋'},
    {'name': 'peach',      'color': (1.0, 0.7, 0.6),   'splash': (1.0, 0.8, 0.7),  'emoji': '🍑'},
    {'name': 'pineapple',  'color': (0.9, 0.8, 0.1),   'splash': (1.0, 0.9, 0.3),  'emoji': '🍍'},
    {'name': 'strawberry', 'color': (0.95, 0.1, 0.3),  'splash': (1.0, 0.2, 0.4),  'emoji': '🍓'},
]

GRAVITY = -600
BOMB_COLOR = (0.15, 0.15, 0.15)
BOMB_HIGHLIGHT = (1.0, 0.3, 0.1)


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'r', 'g', 'b', 'life', 'max_life', 'size')

    def __init__(self, x, y, vx, vy, r, g, b, life=0.6, size=6):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r = r
        self.g = g
        self.b = b
        self.life = life
        self.max_life = life
        self.size = size


class TrailPoint:
    __slots__ = ('x', 'y', 'life')

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 0.25


class Fruit:
    __slots__ = ('x', 'y', 'vx', 'vy', 'radius', 'info', 'is_bomb',
                 'sliced', 'rotation', 'rot_speed', 'alive')

    def __init__(self, x, y, vx, vy, radius, info, is_bomb=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.info = info
        self.is_bomb = is_bomb
        self.sliced = False
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-180, 180)
        self.alive = True


class SlicedHalf:
    __slots__ = ('x', 'y', 'vx', 'vy', 'rotation', 'rot_speed',
                 'r', 'g', 'b', 'radius', 'life', 'side', 'inner_r', 'inner_g', 'inner_b')

    def __init__(self, x, y, vx, vy, r, g, b, radius, side):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r = r
        self.g = g
        self.b = b
        ir, ig, ib = min(r + 0.3, 1.0), min(g + 0.3, 1.0), min(b + 0.2, 1.0)
        self.inner_r = ir
        self.inner_g = ig
        self.inner_b = ib
        self.radius = radius
        self.life = 1.5
        self.side = side
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-200, 200)


class FruitNinja(scene.Scene):

    def setup(self):
        self.game_state = 'menu'
        self.score = 0
        self.best_score = 0
        self.lives = 3
        self.max_lives = 3
        self.combo = 0
        self.combo_timer = 0.0
        self.combo_display_timer = 0.0
        self.last_combo = 0
        self.combo_x = 0
        self.combo_y = 0

        self.fruits = []
        self.particles = []
        self.trail_points = []
        self.sliced_halves = []
        self.miss_texts = []

        self.spawn_timer = 0.0
        self.spawn_interval = 1.8
        self.difficulty_timer = 0.0
        self.bomb_chance = 0.08
        self.wave_count = 0
        self.fruits_per_wave_min = 1
        self.fruits_per_wave_max = 3

        self.swiping = False
        self.swipe_points = []

        self.menu_pulse = 0.0
        self.game_over_alpha = 0.0

    def start_game(self):
        self.game_state = 'playing'
        self.score = 0
        self.lives = 3
        self.combo = 0
        self.combo_timer = 0.0
        self.combo_display_timer = 0.0
        self.fruits.clear()
        self.particles.clear()
        self.trail_points.clear()
        self.sliced_halves.clear()
        self.miss_texts.clear()
        self.spawn_timer = 0.0
        self.spawn_interval = 1.8
        self.difficulty_timer = 0.0
        self.bomb_chance = 0.08
        self.wave_count = 0
        self.fruits_per_wave_min = 1
        self.fruits_per_wave_max = 3
        self.game_over_alpha = 0.0

    def spawn_wave(self):
        w, h = self.size.w, self.size.h
        count = random.randint(self.fruits_per_wave_min, self.fruits_per_wave_max)
        for _ in range(count):
            is_bomb = random.random() < self.bomb_chance
            radius = random.uniform(28, 40) if not is_bomb else random.uniform(30, 38)
            margin = radius + 20
            x = random.uniform(margin, w - margin)
            target_x = w * 0.5 + random.uniform(-w * 0.25, w * 0.25)
            vx = (target_x - x) * random.uniform(0.3, 0.7)
            vx = max(-250, min(250, vx))
            min_vy = h * 0.7
            max_vy = h * 1.1
            vy = random.uniform(min_vy, max_vy)
            info = random.choice(FRUITS) if not is_bomb else None
            self.fruits.append(Fruit(x, -radius, vx, vy, radius, info, is_bomb))
        self.wave_count += 1

    def spawn_juice(self, x, y, color, count=15):
        r, g, b = color
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(60, 250)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.4, 0.9)
            size = random.uniform(3, 9)
            pr = min(1.0, r + random.uniform(-0.1, 0.1))
            pg = min(1.0, g + random.uniform(-0.1, 0.1))
            pb = min(1.0, b + random.uniform(-0.1, 0.1))
            self.particles.append(Particle(x, y, vx, vy, pr, pg, pb, life, size))

    def spawn_bomb_explosion(self, x, y):
        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(80, 300)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.3, 0.8)
            size = random.uniform(4, 10)
            t = random.random()
            r = 1.0 * t + 0.2 * (1 - t)
            g = 0.4 * t
            b = 0.05 * t
            self.particles.append(Particle(x, y, vx, vy, r, g, b, life, size))

    def slice_fruit(self, fruit):
        fruit.sliced = True
        fruit.alive = False
        if fruit.is_bomb:
            self.spawn_bomb_explosion(fruit.x, fruit.y)
            self.lives = 0
            self.game_state = 'gameover'
            self.game_over_alpha = 0.0
            if self.score > self.best_score:
                self.best_score = self.score
            return

        col = fruit.info['splash']
        self.spawn_juice(fruit.x, fruit.y, col, 20)

        left_vx = fruit.vx - random.uniform(60, 120)
        right_vx = fruit.vx + random.uniform(60, 120)
        r, g, b = fruit.info['color']
        self.sliced_halves.append(
            SlicedHalf(fruit.x, fruit.y, left_vx, fruit.vy * 0.5 + 50,
                       r, g, b, fruit.radius, -1))
        self.sliced_halves.append(
            SlicedHalf(fruit.x, fruit.y, right_vx, fruit.vy * 0.5 + 50,
                       r, g, b, fruit.radius, 1))

        self.combo += 1
        self.combo_timer = 0.4
        points = 1
        if self.combo >= 3:
            points = self.combo
            self.last_combo = self.combo
            self.combo_display_timer = 1.2
            self.combo_x = fruit.x
            self.combo_y = fruit.y
        self.score += points

    def check_swipe_hits(self, x1, y1, x2, y2):
        for fruit in self.fruits:
            if fruit.sliced or not fruit.alive:
                continue
            dx = fruit.x - (x1 + x2) * 0.5
            dy = fruit.y - (y1 + y2) * 0.5
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < fruit.radius + 15:
                self.slice_fruit(fruit)
                continue
            seg_len = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            if seg_len < 1:
                continue
            nx = (x2 - x1) / seg_len
            ny = (y2 - y1) / seg_len
            fx = fruit.x - x1
            fy = fruit.y - y1
            proj = fx * nx + fy * ny
            proj = max(0, min(seg_len, proj))
            closest_x = x1 + nx * proj
            closest_y = y1 + ny * proj
            dx = fruit.x - closest_x
            dy = fruit.y - closest_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < fruit.radius + 10:
                self.slice_fruit(fruit)

    def update(self):
        dt = self.dt
        if dt > 0.1:
            dt = 0.016

        if self.game_state == 'menu':
            self.menu_pulse += dt
            return

        if self.game_state == 'gameover':
            self.game_over_alpha = min(1.0, self.game_over_alpha + dt * 2.0)
            for p in self.particles:
                p.x += p.vx * dt
                p.y += p.vy * dt
                p.vy += GRAVITY * 0.3 * dt
                p.life -= dt
            self.particles = [p for p in self.particles if p.life > 0]
            return

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_wave()
            self.spawn_timer = self.spawn_interval

        self.difficulty_timer += dt
        if self.difficulty_timer > 8.0:
            self.difficulty_timer = 0.0
            self.spawn_interval = max(0.6, self.spawn_interval - 0.12)
            self.bomb_chance = min(0.28, self.bomb_chance + 0.02)
            if self.wave_count > 5 and self.fruits_per_wave_max < 5:
                self.fruits_per_wave_max += 1
            if self.wave_count > 12 and self.fruits_per_wave_min < 3:
                self.fruits_per_wave_min += 1

        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        if self.combo_display_timer > 0:
            self.combo_display_timer -= dt

        for fruit in self.fruits:
            if not fruit.alive:
                continue
            fruit.x += fruit.vx * dt
            fruit.y += fruit.vy * dt
            fruit.vy += GRAVITY * dt
            fruit.rotation += fruit.rot_speed * dt
            if fruit.y < -fruit.radius * 2 and fruit.vy < 0 and not fruit.sliced:
                fruit.alive = False
                if not fruit.is_bomb:
                    self.lives -= 1
                    self.miss_texts.append({
                        'x': max(40, min(self.size.w - 40, fruit.x)),
                        'y': 60 + self.safe_area_insets.bottom,
                        'life': 1.0
                    })
                    if self.lives <= 0:
                        self.game_state = 'gameover'
                        self.game_over_alpha = 0.0
                        if self.score > self.best_score:
                            self.best_score = self.score

        self.fruits = [f for f in self.fruits if f.alive]

        for h in self.sliced_halves:
            h.x += h.vx * dt
            h.y += h.vy * dt
            h.vy += GRAVITY * dt
            h.rotation += h.rot_speed * dt
            h.life -= dt
        self.sliced_halves = [h for h in self.sliced_halves if h.life > 0]

        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += GRAVITY * 0.3 * dt
            p.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]

        for tp in self.trail_points:
            tp.life -= dt
        self.trail_points = [tp for tp in self.trail_points if tp.life > 0]

        for mt in self.miss_texts:
            mt['life'] -= dt
            mt['y'] += 30 * dt
        self.miss_texts = [mt for mt in self.miss_texts if mt['life'] > 0]

    def draw(self):
        if self.game_state == 'menu':
            self.draw_menu()
            return

        scene.background(0.06, 0.04, 0.12)
        self.draw_background_pattern()
        self.draw_particles()
        self.draw_sliced_halves()
        self.draw_fruits()
        self.draw_trail()
        self.draw_hud()

        if self.game_state == 'gameover':
            self.draw_game_over()

    def draw_background_pattern(self):
        w, h = self.size.w, self.size.h
        scene.no_stroke()
        for i in range(5):
            a = 0.015 + i * 0.005
            scene.fill(0.1, 0.05, 0.2, a)
            y = (h * 0.15) * i
            scene.rect(0, y, w, h * 0.15)

    def draw_fruits(self):
        scene.no_stroke()
        for fruit in self.fruits:
            if not fruit.alive:
                continue
            scene.push_matrix()
            scene.translate(fruit.x, fruit.y)
            scene.rotate(fruit.rotation)
            x = -fruit.radius
            y = -fruit.radius
            s = fruit.radius * 2
            if fruit.is_bomb:
                scene.fill(0.15, 0.15, 0.15, 1)
                scene.ellipse(x, y, s, s)
                scene.fill(0.3, 0.3, 0.3, 1)
                scene.ellipse(x + 4, y + 4, s - 8, s - 8)
                scene.fill(1.0, 0.3, 0.1, 0.9)
                fuse_s = fruit.radius * 0.35
                scene.ellipse(-fuse_s * 0.5, fruit.radius * 0.7, fuse_s, fuse_s)
                glow_s = fruit.radius * 0.5
                pulse = 0.5 + 0.5 * math.sin(self.t * 12)
                scene.fill(1.0, 0.5, 0.1, 0.3 * pulse)
                scene.ellipse(-glow_s * 0.5, fruit.radius * 0.6, glow_s, glow_s)
                scene.fill(1, 1, 1, 0.9)
                scene.pop_matrix()
                scene.text('💣', 'Helvetica', int(fruit.radius * 0.7),
                           fruit.x, fruit.y, 5)
            else:
                r, g, b = fruit.info['color']
                scene.fill(r * 0.6, g * 0.6, b * 0.6, 1)
                scene.ellipse(x - 2, y - 2, s + 4, s + 4)
                scene.fill(r, g, b, 1)
                scene.ellipse(x, y, s, s)
                scene.fill(min(1, r + 0.25), min(1, g + 0.25), min(1, b + 0.15), 0.5)
                hs = fruit.radius * 0.7
                scene.ellipse(-hs * 0.3, hs * 0.1, hs, hs * 0.6)
                scene.pop_matrix()
                scene.tint(1, 1, 1, 1)
                scene.text(fruit.info['emoji'], 'Helvetica',
                           int(fruit.radius * 0.9), fruit.x, fruit.y, 5)
                scene.no_tint()

    def draw_sliced_halves(self):
        scene.no_stroke()
        for h in self.sliced_halves:
            alpha = min(1.0, h.life)
            scene.push_matrix()
            scene.translate(h.x, h.y)
            scene.rotate(h.rotation)
            r2 = h.radius
            scene.fill(h.r, h.g, h.b, alpha)
            if h.side < 0:
                scene.rect(-r2, -r2, r2, r2 * 2)
                scene.fill(h.inner_r, h.inner_g, h.inner_b, alpha * 0.8)
                scene.rect(-r2 + 3, -r2 + 3, r2 - 6, r2 * 2 - 6)
            else:
                scene.rect(0, -r2, r2, r2 * 2)
                scene.fill(h.inner_r, h.inner_g, h.inner_b, alpha * 0.8)
                scene.rect(3, -r2 + 3, r2 - 6, r2 * 2 - 6)
            scene.pop_matrix()

    def draw_particles(self):
        scene.no_stroke()
        for p in self.particles:
            alpha = (p.life / p.max_life)
            scene.fill(p.r, p.g, p.b, alpha)
            s = p.size * alpha
            scene.ellipse(p.x - s * 0.5, p.y - s * 0.5, s, s)

    def draw_trail(self):
        if len(self.trail_points) < 2:
            return
        for i in range(1, len(self.trail_points)):
            tp = self.trail_points[i]
            tp_prev = self.trail_points[i - 1]
            alpha = tp.life / 0.25
            w = 6 * alpha
            scene.stroke(0.9, 0.95, 1.0, alpha * 0.9)
            scene.stroke_weight(w)
            scene.line(tp_prev.x, tp_prev.y, tp.x, tp.y)

            if alpha > 0.3:
                scene.stroke(0.6, 0.8, 1.0, alpha * 0.3)
                scene.stroke_weight(w * 3)
                scene.line(tp_prev.x, tp_prev.y, tp.x, tp.y)
        scene.no_stroke()

    def draw_hud(self):
        w = self.size.w
        h = self.size.h
        top = h - self.safe_area_insets.top - 10
        left = self.safe_area_insets.left + 16
        right = w - self.safe_area_insets.right - 16

        scene.tint(1, 1, 1, 1)
        scene.text('水果忍者', 'Helvetica-Bold', 18, w * 0.5, top - 2, 8)
        scene.no_tint()

        scene.tint(1, 0.95, 0.3, 1)
        score_str = str(self.score)
        scene.text(score_str, 'Helvetica-Bold', 32, left + 4, top - 30, 7)
        scene.no_tint()

        heart_y = top - 30
        for i in range(self.max_lives):
            hx = right - i * 30
            if i < self.lives:
                scene.tint(1, 0.2, 0.3, 1)
                scene.text('❤️', 'Helvetica', 22, hx, heart_y, 9)
            else:
                scene.tint(0.4, 0.4, 0.4, 0.5)
                scene.text('♡', 'Helvetica', 22, hx, heart_y, 9)
        scene.no_tint()

        if self.combo_display_timer > 0 and self.last_combo >= 3:
            ca = min(1.0, self.combo_display_timer)
            scale = 1.0 + (1.0 - ca) * 0.3
            fs = int(36 * scale)
            scene.tint(1.0, 0.8, 0.0, ca)
            combo_str = 'x{} COMBO!'.format(self.last_combo)
            scene.text(combo_str, 'Helvetica-Bold', fs,
                       self.combo_x, self.combo_y + 50, 5)
            scene.no_tint()

        for mt in self.miss_texts:
            a = min(1.0, mt['life'])
            scene.tint(1, 0.3, 0.3, a)
            scene.text('MISS', 'Helvetica-Bold', 20, mt['x'], mt['y'], 5)
        scene.no_tint()

    def draw_menu(self):
        scene.background(0.06, 0.04, 0.12)
        w, h = self.size.w, self.size.h
        cx, cy = w * 0.5, h * 0.5

        scene.no_stroke()
        for i in range(8):
            a = 0.02 + i * 0.005
            scene.fill(0.12, 0.06, 0.22, a)
            scene.rect(0, i * h / 8, w, h / 8)

        pulse = 0.8 + 0.2 * math.sin(self.menu_pulse * 2.5)

        scene.tint(1, 0.3, 0.2, pulse)
        scene.text('🍉', 'Helvetica', 80, cx, cy + 120, 5)
        scene.no_tint()

        scene.tint(1.0, 0.95, 0.9, 1)
        scene.text('水果忍者', 'Helvetica-Bold', 52, cx, cy + 20, 5)
        scene.no_tint()

        scene.tint(0.7, 0.8, 1.0, 0.7)
        scene.text('Fruit Ninja', 'Helvetica', 22, cx, cy - 25, 5)
        scene.no_tint()

        tap_alpha = 0.5 + 0.5 * math.sin(self.menu_pulse * 3)
        scene.tint(1, 1, 1, tap_alpha)
        scene.text('轻触开始 / Tap to Start', 'Helvetica', 20,
                    cx, cy - 90, 5)
        scene.no_tint()

        if self.best_score > 0:
            scene.tint(1, 0.85, 0.3, 0.8)
            best_str = '最高分: {}'.format(self.best_score)
            scene.text(best_str, 'Helvetica-Bold', 20,
                       cx, cy - 130, 5)
            scene.no_tint()

        bottom_y = self.safe_area_insets.bottom + 30
        scene.tint(0.5, 0.5, 0.6, 0.4)
        scene.text('滑动切水果 · 避开炸弹', 'Helvetica', 14, cx, bottom_y, 5)
        scene.no_tint()

    def draw_game_over(self):
        w, h = self.size.w, self.size.h
        cx, cy = w * 0.5, h * 0.5
        a = self.game_over_alpha

        scene.fill(0, 0, 0, a * 0.7)
        scene.no_stroke()
        scene.rect(0, 0, w, h)

        scene.tint(1, 0.2, 0.2, a)
        scene.text('GAME OVER', 'Helvetica-Bold', 48, cx, cy + 60, 5)
        scene.no_tint()

        scene.tint(1, 1, 1, a)
        score_str = '得分: {}'.format(self.score)
        scene.text(score_str, 'Helvetica-Bold', 30, cx, cy, 5)
        scene.no_tint()

        if self.score >= self.best_score and self.score > 0:
            scene.tint(1, 0.85, 0.2, a)
            scene.text('🏆 新纪录!', 'Helvetica-Bold', 22, cx, cy - 40, 5)
            scene.no_tint()

        tap_a = a * (0.5 + 0.5 * math.sin(self.t * 3))
        scene.tint(0.8, 0.9, 1, tap_a)
        scene.text('轻触重新开始', 'Helvetica', 20, cx, cy - 90, 5)
        scene.no_tint()

    def touch_began(self, touch):
        if self.game_state == 'menu':
            self.start_game()
            return

        if self.game_state == 'gameover' and self.game_over_alpha > 0.5:
            self.game_state = 'menu'
            return

        if self.game_state == 'playing':
            self.swiping = True
            self.swipe_points = [(touch.location.x, touch.location.y)]
            self.trail_points.append(TrailPoint(touch.location.x, touch.location.y))

    def touch_moved(self, touch):
        if self.game_state != 'playing' or not self.swiping:
            return
        x, y = touch.location.x, touch.location.y
        px, py = touch.prev_location.x, touch.prev_location.y

        self.trail_points.append(TrailPoint(x, y))
        self.swipe_points.append((x, y))

        trail_particles = 3
        for _ in range(trail_particles):
            t = random.random()
            px2 = px + (x - px) * t
            py2 = py + (y - py) * t
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(10, 40)
            self.particles.append(
                Particle(px2, py2,
                         math.cos(angle) * speed, math.sin(angle) * speed,
                         0.7, 0.85, 1.0, 0.2, 2))

        self.check_swipe_hits(px, py, x, y)

    def touch_ended(self, touch):
        if self.game_state == 'playing':
            self.swiping = False
            self.swipe_points = []


scene.run(FruitNinja())
