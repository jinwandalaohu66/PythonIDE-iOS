#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""霓虹贪吃蛇 — 赛博朋克风格，道具系统，粒子尾迹"""
import scene
import random
import math

NEON_THEMES = [
    {'head': (0.2, 0.9, 1.0), 'body': (0.1, 0.6, 0.8), 'name': '冰蓝'},
    {'head': (1.0, 0.3, 0.6), 'body': (0.8, 0.15, 0.4), 'name': '玫红'},
    {'head': (0.3, 1.0, 0.5), 'body': (0.15, 0.7, 0.3), 'name': '翠绿'},
    {'head': (1.0, 0.7, 0.1), 'body': (0.8, 0.5, 0.05), 'name': '金橙'},
]

DIRS = {'up': (0, 1), 'down': (0, -1), 'left': (-1, 0), 'right': (1, 0)}
OPP = {'up':'down','down':'up','left':'right','right':'left'}

class Particle:
    __slots__ = ('x','y','vx','vy','r','g','b','life','ml','sz')
    def __init__(self, x, y, r, g, b, spread=2):
        a = random.uniform(0, math.pi*2)
        s = random.uniform(0.3, spread)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a)*s, math.sin(a)*s
        self.r, self.g, self.b = r, g, b
        self.life = random.uniform(0.2, 0.5)
        self.ml = self.life
        self.sz = random.uniform(2, 4)

class NeonSnake(scene.Scene):
    def setup(self):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        self.cell = 18

        self.dpad_h = 130
        self.dpad_btn = 52

        play_top = H - insets.top - 55
        play_bot = insets.bottom + self.dpad_h + 10
        self.play_top = play_top
        self.play_bot = play_bot
        self.cols = int(W // self.cell)
        self.rows = int((play_top - play_bot) // self.cell)
        self.grid_w = self.cols * self.cell
        self.grid_h = self.rows * self.cell
        self.offset_x = (W - self.grid_w) / 2
        self.offset_y = play_bot + ((play_top - play_bot) - self.grid_h) / 2

        mid_c = self.cols // 2
        mid_r = self.rows // 2
        self.snake = [(mid_c, mid_r), (mid_c - 1, mid_r), (mid_c - 2, mid_r)]
        self.direction = 'right'
        self.next_dir = 'right'
        self.food = None
        self.powerup = None
        self.powerup_timer = 0
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.speed = 8
        self.tick = 0
        self.frame = 0
        self.game_over = False
        self.particles = []
        self.theme = random.choice(NEON_THEMES)
        self.effects = {}
        self.walls = []
        self.combo = 0
        self.combo_timer = 0
        self.floats = []
        self.swipe_start = None
        self.hint_timer = 180
        self.pressed_btn = None
        self._gen_walls()
        self._spawn_food()

    def _dpad_layout(self):
        W = self.size.w
        insets = self.safe_area_insets
        cx = W / 2
        cy = insets.bottom + self.dpad_h / 2
        s = self.dpad_btn
        gap = 4
        return {
            'up':    (cx, cy + s/2 + gap, s, s),
            'down':  (cx, cy - s/2 - gap, s, s),
            'left':  (cx - s - gap, cy, s, s),
            'right': (cx + s + gap, cy, s, s),
        }

    def _gen_walls(self):
        self.walls = []
        if self.level < 2:
            return
        for _ in range(min(self.level * 2, 12)):
            wc = random.randint(2, self.cols - 3)
            wr = random.randint(2, self.rows - 3)
            if any(abs(wc - sc) + abs(wr - sr) < 3 for sc, sr in self.snake):
                continue
            self.walls.append((wc, wr))

    def _spawn_food(self):
        occupied = set(self.snake)
        if self.walls:
            occupied |= set(self.walls)
        while True:
            fx = random.randint(1, self.cols - 2)
            fy = random.randint(1, self.rows - 2)
            if (fx, fy) not in occupied:
                self.food = (fx, fy)
                break
        if random.random() < 0.25 and not self.powerup:
            while True:
                px = random.randint(1, self.cols - 2)
                py = random.randint(1, self.rows - 2)
                if (px, py) not in occupied and (px, py) != self.food:
                    kinds = ['speed', 'ghost', 'double']
                    self.powerup = (px, py, random.choice(kinds))
                    self.powerup_timer = 300
                    break

    def _hit_dpad(self, tx, ty):
        layout = self._dpad_layout()
        for d, (bx, by, bw, bh) in layout.items():
            if abs(tx - bx) < bw * 0.6 and abs(ty - by) < bh * 0.6:
                return d
        return None

    def _try_set_dir(self, nd):
        if nd and nd != OPP.get(self.direction):
            self.next_dir = nd

    def touch_began(self, touch):
        if self.game_over:
            self.setup()
            return
        tx, ty = touch.location.x, touch.location.y
        btn = self._hit_dpad(tx, ty)
        if btn:
            self.pressed_btn = btn
            self._try_set_dir(btn)
        else:
            self.swipe_start = (tx, ty)
            self.pressed_btn = None

    def touch_moved(self, touch):
        if self.game_over:
            return
        tx, ty = touch.location.x, touch.location.y
        if self.pressed_btn is not None:
            btn = self._hit_dpad(tx, ty)
            if btn and btn != self.pressed_btn:
                self.pressed_btn = btn
                self._try_set_dir(btn)
        elif self.swipe_start:
            self._detect_swipe(tx, ty)

    def touch_ended(self, touch):
        if self.game_over:
            return
        if self.swipe_start:
            self._detect_swipe(touch.location.x, touch.location.y)
        self.swipe_start = None
        self.pressed_btn = None

    def _detect_swipe(self, ex, ey):
        sx, sy = self.swipe_start
        dx, dy = ex - sx, ey - sy
        if abs(dx) < 10 and abs(dy) < 10:
            return
        if abs(dx) > abs(dy):
            nd = 'right' if dx > 0 else 'left'
        else:
            nd = 'up' if dy > 0 else 'down'
        self._try_set_dir(nd)
        self.swipe_start = (ex, ey)

    def update(self):
        self.frame += 1
        if self.hint_timer > 0:
            self.hint_timer -= 1
        if self.game_over:
            self._upd_particles()
            return

        if self.powerup:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.powerup = None

        for key in list(self.effects.keys()):
            self.effects[key] -= 1
            if self.effects[key] <= 0:
                del self.effects[key]

        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo = 0

        speed = self.speed
        if 'speed' in self.effects:
            speed = int(speed * 1.5)

        self.tick += 1
        if self.tick < max(2, 60 // speed):
            self._upd_particles()
            return
        self.tick = 0

        self.direction = self.next_dir
        dd = DIRS[self.direction]
        head = self.snake[0]
        nh = (head[0] + dd[0], head[1] + dd[1])

        if 'ghost' not in self.effects:
            if nh[0] < 0 or nh[0] >= self.cols or nh[1] < 0 or nh[1] >= self.rows:
                self._die()
                return
            if nh in self.snake[1:]:
                self._die()
                return
            if nh in self.walls:
                self._die()
                return
        else:
            nh = (nh[0] % self.cols, nh[1] % self.rows)

        self.snake.insert(0, nh)

        ate = False
        if nh == self.food:
            ate = True
            self.combo += 1
            self.combo_timer = 120
            pts = 10 * self.combo
            if 'double' in self.effects:
                pts *= 2
            self.score += pts
            self.floats.append({'x': self.offset_x + nh[0]*self.cell + self.cell/2,
                                'y': self.offset_y + nh[1]*self.cell + self.cell/2,
                                'text': f'+{pts}', 'life': 1.0})
            fc = self.theme['head']
            for _ in range(10):
                self.particles.append(Particle(
                    self.offset_x + nh[0]*self.cell + self.cell/2,
                    self.offset_y + nh[1]*self.cell + self.cell/2,
                    fc[0], fc[1], fc[2], 3))
            if len(self.snake) % 10 == 0:
                self.level += 1
                self.speed = min(20, 8 + self.level)
                self._gen_walls()
            self._spawn_food()

        if self.powerup and nh == (self.powerup[0], self.powerup[1]):
            kind = self.powerup[2]
            self.effects[kind] = 300
            for _ in range(8):
                self.particles.append(Particle(
                    self.offset_x + nh[0]*self.cell + self.cell/2,
                    self.offset_y + nh[1]*self.cell + self.cell/2,
                    1, 1, 0.3, 3))
            self.powerup = None
            self.score += 25

        if not ate:
            tail = self.snake.pop()
            tc = self.theme['body']
            if random.random() < 0.3:
                self.particles.append(Particle(
                    self.offset_x + tail[0]*self.cell + self.cell/2,
                    self.offset_y + tail[1]*self.cell + self.cell/2,
                    tc[0]*0.5, tc[1]*0.5, tc[2]*0.5, 1))

        self._upd_particles()

    def _die(self):
        self.game_over = True
        if self.score > self.high_score:
            self.high_score = self.score
        hc = self.theme['head']
        for seg in self.snake[:10]:
            px = self.offset_x + seg[0]*self.cell + self.cell/2
            py = self.offset_y + seg[1]*self.cell + self.cell/2
            for _ in range(5):
                self.particles.append(Particle(px, py, hc[0], hc[1], hc[2], 5))

    def _upd_particles(self):
        dt = 1/60
        for p in self.particles:
            p.x += p.vx; p.y += p.vy; p.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]
        for f in self.floats:
            f['y'] += 0.8; f['life'] -= dt
        self.floats = [f for f in self.floats if f['life'] > 0]

    def _draw_dpad(self):
        W = self.size.w
        th = self.theme
        hc = th['head']
        layout = self._dpad_layout()
        arrows = {'up': '▲', 'down': '▼', 'left': '◀', 'right': '▶'}

        for d, (bx, by, bw, bh) in layout.items():
            pressed = (self.pressed_btn == d)
            is_active = (d == self.direction)
            if pressed:
                scene.fill(hc[0], hc[1], hc[2], 0.35)
            elif is_active:
                scene.fill(hc[0]*0.2, hc[1]*0.2, hc[2]*0.2, 0.4)
            else:
                scene.fill(0.15, 0.12, 0.22, 0.5)
            scene.rect(bx - bw/2, by - bh/2, bw, bh, 12)

            scene.fill(hc[0]*0.4, hc[1]*0.4, hc[2]*0.4, 0.15)
            scene.rect(bx - bw/2 + 2, by + bh/2 - 6, bw - 4, 3, 4)

            if pressed:
                scene.tint(1, 1, 1, 0.95)
            elif is_active:
                scene.tint(hc[0], hc[1], hc[2], 0.8)
            else:
                scene.tint(0.6, 0.55, 0.7, 0.6)
            scene.text(arrows[d], 'Arial', 22, bx, by)
            scene.no_tint()

    def draw(self):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        fc = self.frame
        th = self.theme

        scene.background(0.04, 0.03, 0.08)

        self._draw_dpad()

        ox, oy = self.offset_x, self.offset_y
        scene.stroke(0.12, 0.1, 0.18)
        scene.stroke_weight(0.5)
        for c in range(self.cols + 1):
            scene.line(ox + c*self.cell, oy, ox + c*self.cell, oy + self.grid_h)
        for r in range(self.rows + 1):
            scene.line(ox, oy + r*self.cell, ox + self.grid_w, oy + r*self.cell)
        scene.no_stroke()

        scene.stroke(th['body'][0]*0.3, th['body'][1]*0.3, th['body'][2]*0.3, 0.3)
        scene.stroke_weight(1.5)
        scene.no_fill()
        scene.rect(ox, oy, self.grid_w, self.grid_h)
        scene.no_stroke()

        for wc, wr in self.walls:
            scene.fill(0.25, 0.2, 0.35)
            scene.rect(ox + wc*self.cell + 1, oy + wr*self.cell + 1, self.cell - 2, self.cell - 2, 3)
            scene.fill(0.35, 0.3, 0.5, 0.4)
            scene.rect(ox + wc*self.cell + 3, oy + wr*self.cell + self.cell - 5, self.cell - 6, 2, 1)

        if self.food:
            fx = ox + self.food[0]*self.cell + self.cell/2
            fy = oy + self.food[1]*self.cell + self.cell/2
            pulse = 0.6 + 0.4*math.sin(fc*0.08)
            scene.fill(1.0, 0.3, 0.4, 0.15*pulse)
            scene.ellipse(fx - 12, fy - 12, 24, 24)
            scene.fill(1.0, 0.25, 0.35)
            scene.ellipse(fx - 6, fy - 6, 12, 12)
            scene.fill(1, 0.7, 0.7, 0.4)
            scene.ellipse(fx - 3, fy + 1, 5, 5)

        if self.powerup:
            ppx = ox + self.powerup[0]*self.cell + self.cell/2
            ppy = oy + self.powerup[1]*self.cell + self.cell/2
            kind = self.powerup[2]
            colors = {'speed': (0.2, 0.9, 1.0), 'ghost': (0.7, 0.3, 1.0), 'double': (1.0, 0.8, 0.1)}
            pc = colors.get(kind, (1,1,1))
            pulse = 0.7 + 0.3*math.sin(fc*0.1)
            scene.fill(pc[0], pc[1], pc[2], 0.12*pulse)
            scene.ellipse(ppx - 14, ppy - 14, 28, 28)
            scene.fill(pc[0], pc[1], pc[2])
            scene.rect(ppx - 7, ppy - 7, 14, 14, 4)
            labels = {'speed': '⚡', 'ghost': '👻', 'double': '×2'}
            scene.tint(1,1,1)
            scene.text(labels.get(kind, '?'), 'Arial', 11, ppx, ppy)
            scene.no_tint()

        for i, seg in enumerate(reversed(self.snake)):
            t = i / max(len(self.snake) - 1, 1)
            bc = th['body']
            hc = th['head']
            cr = bc[0] + (hc[0]-bc[0])*t
            cg = bc[1] + (hc[1]-bc[1])*t
            cb = bc[2] + (hc[2]-bc[2])*t
            sx = ox + seg[0]*self.cell
            sy = oy + seg[1]*self.cell
            if 'ghost' in self.effects:
                scene.fill(cr, cg, cb, 0.5)
            else:
                scene.fill(cr*0.15, cg*0.15, cb*0.15, 0.3)
                scene.rect(sx + 1, sy - 1, self.cell - 2, self.cell - 2, 4)
                scene.fill(cr, cg, cb)
            scene.rect(sx + 1, sy + 1, self.cell - 2, self.cell - 2, 4)

        if self.snake:
            hs = self.snake[0]
            hx = ox + hs[0]*self.cell + self.cell/2
            hy = oy + hs[1]*self.cell + self.cell/2
            hc = th['head']
            scene.fill(hc[0], hc[1], hc[2], 0.08)
            scene.ellipse(hx - self.cell, hy - self.cell, self.cell*2, self.cell*2)
            dd = DIRS[self.direction]
            e1x = hx + dd[0]*3 + (-dd[1])*3
            e1y = hy + dd[1]*3 + dd[0]*3
            e2x = hx + dd[0]*3 - (-dd[1])*3
            e2y = hy + dd[1]*3 - dd[0]*3
            scene.fill(1, 1, 1, 0.9)
            scene.ellipse(e1x-2, e1y-2, 4, 4)
            scene.ellipse(e2x-2, e2y-2, 4, 4)
            scene.fill(0.1, 0.1, 0.15)
            scene.ellipse(e1x+dd[0]-1, e1y+dd[1]-1, 2, 2)
            scene.ellipse(e2x+dd[0]-1, e2y+dd[1]-1, 2, 2)

        for p in self.particles:
            a = p.life / p.ml
            scene.fill(p.r, p.g, p.b, a*0.7)
            sz = p.sz * a
            scene.ellipse(p.x-sz/2, p.y-sz/2, sz, sz)

        for f in self.floats:
            scene.tint(th['head'][0], th['head'][1], th['head'][2], f['life'])
            scene.text(f['text'], 'Arial-BoldMT', 14, f['x'], f['y'])
        scene.no_tint()

        if self.hint_timer > 0 and not self.game_over:
            ha = min(1.0, self.hint_timer / 60)
            scene.tint(0.7, 0.7, 0.8, ha * 0.8)
            hint_y = insets.bottom + self.dpad_h + 20
            scene.text('点击方向键 或 滑动屏幕 控制蛇的方向', 'Arial', 14, W/2, hint_y)
            scene.no_tint()

        hud_top = H - insets.top
        hud_h = 50
        scene.fill(0.04, 0.03, 0.08, 0.85)
        scene.rect(0, hud_top - hud_h, W, hud_h + insets.top)
        cy = hud_top - hud_h / 2
        scene.tint(th['head'][0]*0.7, th['head'][1]*0.7, th['head'][2]*0.7)
        scene.text(f'Lv.{self.level}', 'Arial-BoldMT', 14, 35, cy + 12)
        scene.tint(1,1,1)
        scene.text(f'{self.score}', 'Arial-BoldMT', 22, W/2, cy + 2)
        scene.tint(0.5, 0.5, 0.6)
        scene.text('分数', 'Arial', 10, W/2, cy + 17)
        if self.combo > 1:
            ca = 0.5 + 0.5*math.sin(fc*0.1)
            scene.tint(1, 0.8, 0.2, ca)
            scene.text(f'×{self.combo}', 'Arial-BoldMT', 15, W/2, cy - 13)
        scene.tint(0.6, 0.6, 0.7)
        scene.text(f'长度 {len(self.snake)}', 'Arial', 13, W - 55, cy + 2)
        scene.no_tint()

        ey = cy - 15
        for key, timer in self.effects.items():
            colors = {'speed': (0.2, 0.9, 1.0), 'ghost': (0.7, 0.3, 1.0), 'double': (1.0, 0.8, 0.1)}
            labels = {'speed': '⚡', 'ghost': '👻', 'double': '×2'}
            pc = colors.get(key, (1,1,1))
            ratio = timer / 300
            scene.fill(pc[0], pc[1], pc[2], 0.3)
            scene.rect(28, ey, 40, 5, 2)
            scene.fill(pc[0], pc[1], pc[2])
            scene.rect(28, ey, 40*ratio, 5, 2)
            scene.tint(pc[0], pc[1], pc[2], 0.8)
            scene.text(labels.get(key, '?'), 'Arial', 10, 18, ey+2)
            scene.no_tint()
            ey -= 12

        if self.game_over:
            scene.fill(0, 0, 0, 0.85)
            scene.rect(0, 0, W, H)
            p = 1 + 0.03*math.sin(fc*0.06)
            scene.push_matrix()
            scene.translate(W/2, H/2+70)
            scene.scale(p, p)
            scene.tint(th['head'][0], th['head'][1], th['head'][2])
            scene.text('游戏结束', 'Arial-BoldMT', 40, 0, 0)
            scene.pop_matrix()
            scene.tint(1,0.95,0.7)
            scene.text(f'{self.score}', 'Arial-BoldMT', 48, W/2, H/2+15)
            scene.tint(0.6, 0.6, 0.7)
            scene.text('最终分数', 'Arial', 14, W/2, H/2+40)
            if self.high_score > 0:
                scene.tint(0.8, 0.75, 0.5)
                scene.text(f'最高 {self.high_score}', 'Arial', 16, W/2, H/2-15)
            scene.tint(0.7, 0.7, 0.8)
            scene.text(f'关卡 {self.level}  |  长度 {len(self.snake)}', 'Arial', 15, W/2, H/2-35)
            blink = 0.4+0.6*abs(math.sin(fc*0.04))
            scene.tint(0.6, 0.7, 0.9, blink)
            scene.text('轻触屏幕再来一局', 'Arial', 18, W/2, H/2-65)
            scene.no_tint()

if __name__ == '__main__':
    scene.run(NeonSnake())
