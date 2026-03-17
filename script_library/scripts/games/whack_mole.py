#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""极速打地鼠 — 连击系统、炸弹闪避、多种地鼠、限时挑战"""
import scene
import random
import math

MOLE_NORMAL = 0
MOLE_GOLDEN = 1
MOLE_HELMET = 2
MOLE_BOMB = 3
MOLE_SPEED = 4

class Particle:
    __slots__ = ('x','y','vx','vy','r','g','b','life','ml','sz')
    def __init__(self, x, y, r, g, b, spread=3, life=0.5):
        a = random.uniform(0, math.pi*2)
        s = random.uniform(0.5, spread)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a)*s, math.sin(a)*s
        self.r, self.g, self.b = r, g, b
        self.life = random.uniform(life*0.3, life)
        self.ml = self.life
        self.sz = random.uniform(2, 5)

class Mole:
    __slots__ = ('gx','gy','kind','state','timer','hp','popup_y','target_y','speed')
    def __init__(self, gx, gy, kind):
        self.gx, self.gy = gx, gy
        self.kind = kind
        self.state = 'rising'
        self.popup_y = 0
        self.target_y = 1.0
        self.speed = 0.06
        if kind == MOLE_SPEED:
            self.timer = random.uniform(0.5, 0.9)
            self.speed = 0.1
        elif kind == MOLE_GOLDEN:
            self.timer = random.uniform(0.7, 1.2)
        elif kind == MOLE_BOMB:
            self.timer = random.uniform(1.5, 2.5)
        else:
            self.timer = random.uniform(1.0, 2.0)
        self.hp = 2 if kind == MOLE_HELMET else 1

class WhackMole(scene.Scene):
    def setup(self):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        self.grid_cols = 3
        self.grid_rows = 4
        self.cell_w = W / self.grid_cols
        play_top = H - insets.top - 55
        play_bot = insets.bottom + 20
        self.play_top = play_top
        self.play_bot = play_bot
        play_h = play_top - play_bot
        self.cell_h = play_h / self.grid_rows

        self.moles = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0
        self.game_time = 60.0
        self.game_over = False
        self.frame = 0
        self.spawn_cd = 0.5
        self.particles = []
        self.floats = []
        self.hits = 0
        self.misses = 0
        self.shakes = []
        self.level_speed = 1.0
        self.flash_alpha = 0

    def _cell_center(self, gx, gy):
        cx = gx * self.cell_w + self.cell_w / 2
        cy = self.play_bot + gy * self.cell_h + self.cell_h / 2
        return cx, cy

    def touch_began(self, touch):
        if self.game_over:
            self.setup()
            return

        x, y = touch.location.x, touch.location.y
        hit = False
        for m in self.moles:
            if m.state == 'hiding' or m.state == 'gone':
                continue
            cx, cy = self._cell_center(m.gx, m.gy)
            hole_r = min(self.cell_w, self.cell_h) * 0.35
            dist = math.sqrt((x - cx)**2 + (y - (cy + hole_r * m.popup_y * 0.5))**2)
            if dist < hole_r * 1.3:
                if m.kind == MOLE_BOMB:
                    self.score = max(0, self.score - 50)
                    self.combo = 0
                    self.combo_timer = 0
                    self.flash_alpha = 0.6
                    m.state = 'gone'
                    for _ in range(15):
                        self.particles.append(Particle(cx, cy, 1, 0.3, 0.1, 5, 0.6))
                    self.shakes.append(12)
                    self.floats.append({'x': cx, 'y': cy, 'text': '-50', 'life': 1.0, 'color': (1, 0.2, 0.2)})
                else:
                    m.hp -= 1
                    if m.hp <= 0:
                        m.state = 'gone'
                        self.combo += 1
                        if self.combo > self.max_combo:
                            self.max_combo = self.combo
                        self.combo_timer = 2.0
                        pts = 10 * self.combo
                        if m.kind == MOLE_GOLDEN:
                            pts *= 3
                        elif m.kind == MOLE_SPEED:
                            pts *= 2
                        self.score += pts
                        self.hits += 1
                        colors = {
                            MOLE_NORMAL: (0.6, 0.4, 0.25),
                            MOLE_GOLDEN: (1, 0.85, 0.15),
                            MOLE_HELMET: (0.5, 0.5, 0.6),
                            MOLE_SPEED: (0.2, 0.9, 1.0),
                        }
                        c = colors.get(m.kind, (0.6, 0.4, 0.25))
                        for _ in range(8):
                            self.particles.append(Particle(cx, cy, c[0], c[1], c[2], 4, 0.5))
                        self.floats.append({'x': cx, 'y': cy + 20, 'text': f'+{pts}', 'life': 1.0,
                                            'color': (1, 0.85, 0.15) if m.kind == MOLE_GOLDEN else (1,1,1)})
                    else:
                        for _ in range(4):
                            self.particles.append(Particle(cx, cy, 0.7, 0.7, 0.8, 2, 0.3))
                        self.floats.append({'x': cx, 'y': cy + 15, 'text': '叮!', 'life': 0.5, 'color': (0.7, 0.7, 0.8)})
                hit = True
                break

        if not hit:
            self.misses += 1
            if self.combo > 0:
                self.combo = 0
                self.combo_timer = 0

    def touch_moved(self, touch):
        pass

    def touch_ended(self, touch):
        pass

    def update(self):
        self.frame += 1
        dt = 1/60

        if self.game_over:
            self._upd_particles()
            return

        self.game_time -= dt
        if self.game_time <= 0:
            self.game_time = 0
            self.game_over = True
            return

        self.level_speed = 1.0 + (60 - self.game_time) / 60 * 1.5

        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        if self.flash_alpha > 0:
            self.flash_alpha -= dt * 2

        new_shakes = []
        for s in self.shakes:
            s -= 1
            if s > 0:
                new_shakes.append(s)
        self.shakes = new_shakes

        self.spawn_cd -= dt * self.level_speed
        if self.spawn_cd <= 0:
            occupied = {(m.gx, m.gy) for m in self.moles if m.state != 'gone'}
            free = []
            for gx in range(self.grid_cols):
                for gy in range(self.grid_rows):
                    if (gx, gy) not in occupied:
                        free.append((gx, gy))
            if free:
                gx, gy = random.choice(free)
                r = random.random()
                if r < 0.05:
                    kind = MOLE_BOMB
                elif r < 0.12:
                    kind = MOLE_GOLDEN
                elif r < 0.22:
                    kind = MOLE_HELMET
                elif r < 0.35:
                    kind = MOLE_SPEED
                else:
                    kind = MOLE_NORMAL
                self.moles.append(Mole(gx, gy, kind))
            self.spawn_cd = random.uniform(0.3, 0.8) / self.level_speed

        for m in list(self.moles):
            if m.state == 'rising':
                m.popup_y += m.speed * self.level_speed
                if m.popup_y >= m.target_y:
                    m.popup_y = m.target_y
                    m.state = 'showing'
            elif m.state == 'showing':
                m.timer -= dt * self.level_speed
                if m.timer <= 0:
                    m.state = 'hiding'
            elif m.state == 'hiding':
                m.popup_y -= 0.08 * self.level_speed
                if m.popup_y <= 0:
                    m.state = 'gone'
                    if m.kind != MOLE_BOMB:
                        self.misses += 1

        self.moles = [m for m in self.moles if m.state != 'gone']

        self._upd_particles()
        for f in self.floats:
            f['y'] += 0.8; f['life'] -= dt
        self.floats = [f for f in self.floats if f['life'] > 0]

    def _upd_particles(self):
        dt = 1/60
        for p in self.particles:
            p.x += p.vx; p.y += p.vy; p.vy -= 2*dt; p.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        fc = self.frame

        shake_x, shake_y = 0, 0
        if self.shakes:
            s = self.shakes[0]
            shake_x = random.uniform(-s, s) * 0.5
            shake_y = random.uniform(-s, s) * 0.5
        if shake_x != 0 or shake_y != 0:
            scene.push_matrix()
            scene.translate(shake_x, shake_y)

        scene.background(0.12, 0.18, 0.1)

        for gy in range(self.grid_rows):
            for gx in range(self.grid_cols):
                cx, cy = self._cell_center(gx, gy)
                hw = min(self.cell_w, self.cell_h) * 0.38
                scene.fill(0.08, 0.12, 0.06)
                scene.ellipse(cx - hw, cy - hw*0.5, hw*2, hw)
                scene.fill(0.18, 0.28, 0.14)
                scene.ellipse(cx - hw + 3, cy - hw*0.5 + 3, hw*2 - 6, hw - 6)

        for m in self.moles:
            cx, cy = self._cell_center(m.gx, m.gy)
            hole_r = min(self.cell_w, self.cell_h) * 0.35
            pop = m.popup_y
            if pop <= 0:
                continue
            mole_y = cy - hole_r * 0.25 + hole_r * pop * 0.6
            mole_sz = hole_r * 0.7

            if m.kind == MOLE_NORMAL:
                scene.fill(0.55, 0.38, 0.22)
                scene.ellipse(cx - mole_sz, mole_y - mole_sz*0.3, mole_sz*2, mole_sz*1.4)
                scene.fill(0.65, 0.48, 0.32)
                scene.ellipse(cx - mole_sz*0.8, mole_y + mole_sz*0.3, mole_sz*1.6, mole_sz*0.6)
                scene.fill(0.2, 0.15, 0.1)
                scene.ellipse(cx - mole_sz*0.35, mole_y + mole_sz*0.45, 6, 6)
                scene.ellipse(cx + mole_sz*0.35 - 6, mole_y + mole_sz*0.45, 6, 6)
                scene.fill(0.3, 0.2, 0.15)
                scene.ellipse(cx - 4, mole_y + mole_sz*0.2, 8, 6)
                scene.fill(1, 1, 1, 0.3)
                scene.ellipse(cx - mole_sz*0.25, mole_y + mole_sz*0.55, 5, 5)

            elif m.kind == MOLE_GOLDEN:
                glow = 0.6 + 0.4 * math.sin(fc * 0.1)
                scene.fill(1, 0.85, 0.15, 0.15 * glow)
                scene.ellipse(cx - mole_sz*1.3, mole_y - mole_sz*0.6, mole_sz*2.6, mole_sz*2)
                scene.fill(1, 0.8, 0.15)
                scene.ellipse(cx - mole_sz, mole_y - mole_sz*0.3, mole_sz*2, mole_sz*1.4)
                scene.fill(1, 0.9, 0.4)
                scene.ellipse(cx - mole_sz*0.8, mole_y + mole_sz*0.3, mole_sz*1.6, mole_sz*0.6)
                scene.fill(0.4, 0.2, 0.05)
                scene.ellipse(cx - mole_sz*0.35, mole_y + mole_sz*0.45, 6, 6)
                scene.ellipse(cx + mole_sz*0.35 - 6, mole_y + mole_sz*0.45, 6, 6)
                scene.fill(0.6, 0.3, 0.05)
                scene.ellipse(cx - 4, mole_y + mole_sz*0.2, 8, 6)
                scene.fill(1, 1, 0.8, 0.5)
                scene.ellipse(cx - mole_sz*0.3, mole_y + mole_sz*0.6, 6, 6)

            elif m.kind == MOLE_HELMET:
                scene.fill(0.55, 0.38, 0.22)
                scene.ellipse(cx - mole_sz, mole_y - mole_sz*0.3, mole_sz*2, mole_sz*1.4)
                scene.fill(0.65, 0.48, 0.32)
                scene.ellipse(cx - mole_sz*0.8, mole_y + mole_sz*0.3, mole_sz*1.6, mole_sz*0.6)
                scene.fill(0.5, 0.5, 0.6)
                scene.rect(cx - mole_sz*0.9, mole_y + mole_sz*0.4, mole_sz*1.8, mole_sz*0.6, 8)
                scene.fill(0.7, 0.7, 0.8, 0.4)
                scene.rect(cx - mole_sz*0.7, mole_y + mole_sz*0.8, mole_sz*1.4, 3, 1)
                scene.fill(0.2, 0.15, 0.1)
                scene.ellipse(cx - mole_sz*0.35, mole_y + mole_sz*0.3, 6, 6)
                scene.ellipse(cx + mole_sz*0.35 - 6, mole_y + mole_sz*0.3, 6, 6)
                if m.hp < 2:
                    scene.stroke(0.8, 0.3, 0.2, 0.5)
                    scene.stroke_weight(1)
                    scene.line(cx - mole_sz*0.5, mole_y + mole_sz*0.5,
                              cx + mole_sz*0.3, mole_y + mole_sz*0.9)
                    scene.no_stroke()

            elif m.kind == MOLE_BOMB:
                pulse = 0.5 + 0.5*math.sin(fc*0.15)
                scene.fill(1, 0.15, 0.1, 0.1*pulse)
                scene.ellipse(cx - mole_sz*1.2, mole_y - mole_sz*0.5, mole_sz*2.4, mole_sz*1.8)
                scene.fill(0.15, 0.15, 0.2)
                scene.ellipse(cx - mole_sz, mole_y - mole_sz*0.3, mole_sz*2, mole_sz*1.4)
                scene.fill(0.25, 0.25, 0.3)
                scene.ellipse(cx - mole_sz*0.8, mole_y + mole_sz*0.3, mole_sz*1.6, mole_sz*0.6)
                scene.fill(1, 0.15, 0.1)
                scene.ellipse(cx - 5, mole_y + mole_sz*0.45, 5, 5)
                scene.ellipse(cx + 2, mole_y + mole_sz*0.45, 5, 5)
                flicker = random.uniform(0.5, 1.0)
                scene.fill(1, 0.6, 0.1, flicker)
                scene.ellipse(cx - 3, mole_y + mole_sz*0.9, 6, 8)

            elif m.kind == MOLE_SPEED:
                scene.fill(0.15, 0.7, 0.85)
                scene.ellipse(cx - mole_sz, mole_y - mole_sz*0.3, mole_sz*2, mole_sz*1.4)
                scene.fill(0.25, 0.85, 0.95)
                scene.ellipse(cx - mole_sz*0.8, mole_y + mole_sz*0.3, mole_sz*1.6, mole_sz*0.6)
                scene.fill(0.05, 0.2, 0.3)
                scene.ellipse(cx - mole_sz*0.35, mole_y + mole_sz*0.45, 6, 6)
                scene.ellipse(cx + mole_sz*0.35 - 6, mole_y + mole_sz*0.45, 6, 6)
                scene.fill(0.1, 0.4, 0.5)
                scene.ellipse(cx - 4, mole_y + mole_sz*0.2, 8, 6)
                scene.fill(0.5, 1, 1, 0.3)
                scene.ellipse(cx - mole_sz*0.2, mole_y + mole_sz*0.55, 4, 4)
                for i in range(3):
                    a = 0.3 - i*0.1
                    scene.fill(0.2, 0.8, 1.0, a)
                    scene.rect(cx - mole_sz*1.3 - i*4, mole_y + mole_sz*0.2 + i*3, 6, 2, 1)

            scene.fill(0.08, 0.12, 0.06)
            scene.ellipse(cx - hole_r, cy - hole_r*0.3, hole_r*2, hole_r*0.35)

        for p in self.particles:
            a = p.life / p.ml
            scene.fill(p.r, p.g, p.b, a*0.8)
            sz = p.sz * a
            scene.ellipse(p.x-sz/2, p.y-sz/2, sz, sz)

        for f in self.floats:
            c = f['color']
            scene.tint(c[0], c[1], c[2], f['life'])
            scene.text(f['text'], 'Arial-BoldMT', 16, f['x'], f['y'])
        scene.no_tint()

        if self.flash_alpha > 0:
            scene.fill(1, 0.1, 0.05, self.flash_alpha * 0.3)
            scene.rect(0, 0, W, H)

        hud_top = H - insets.top
        hud_h = 52
        scene.fill(0.1, 0.15, 0.08, 0.85)
        scene.rect(0, hud_top - hud_h, W, hud_h + insets.top)
        cy = hud_top - hud_h / 2

        t = max(0, self.game_time)
        if t < 10:
            pulse = 0.5 + 0.5*math.sin(fc*0.15)
            scene.tint(1, 0.3, 0.2, pulse)
        else:
            scene.tint(0.9, 0.85, 0.7)
        scene.text(f'{int(t)}s', 'Arial-BoldMT', 18, 35, cy + 2)

        scene.tint(1,1,1)
        scene.text(f'{self.score}', 'Arial-BoldMT', 24, W/2, cy + 2)
        scene.tint(0.5, 0.5, 0.6)
        scene.text('分数', 'Arial', 10, W/2, cy + 19)

        if self.combo > 1:
            ca = 0.6 + 0.4*math.sin(fc*0.12)
            scene.tint(1, 0.8, 0.2, ca)
            scene.text(f'×{self.combo}', 'Arial-BoldMT', 16, W/2, cy - 14)

        acc = self.hits / max(1, self.hits + self.misses) * 100
        scene.tint(0.6, 0.8, 0.5)
        scene.text(f'命中 {acc:.0f}%', 'Arial', 13, W - 55, cy + 2)
        scene.no_tint()

        if shake_x != 0 or shake_y != 0:
            scene.pop_matrix()

        if self.game_over:
            scene.fill(0, 0, 0, 0.85)
            scene.rect(0, 0, W, H)
            p = 1 + 0.03*math.sin(fc*0.06)
            scene.push_matrix()
            scene.translate(W/2, H/2+80)
            scene.scale(p, p)
            scene.tint(1, 0.7, 0.2)
            scene.text('时间到!', 'Arial-BoldMT', 42, 0, 0)
            scene.pop_matrix()
            scene.tint(1, 0.95, 0.7)
            scene.text(f'{self.score}', 'Arial-BoldMT', 52, W/2, H/2+20)
            scene.tint(0.6, 0.6, 0.7)
            scene.text('最终分数', 'Arial', 14, W/2, H/2+48)
            scene.tint(0.8, 0.8, 0.9)
            acc = self.hits / max(1, self.hits + self.misses) * 100
            scene.text(f'命中 {acc:.0f}%  |  最高连击 ×{self.max_combo}', 'Arial', 16, W/2, H/2-10)
            scene.tint(0.7, 0.75, 0.6)
            scene.text(f'击中 {self.hits} 只地鼠', 'Arial', 15, W/2, H/2-30)
            blink = 0.4+0.6*abs(math.sin(fc*0.04))
            scene.tint(0.6, 0.7, 0.9, blink)
            scene.text('轻触屏幕再来一局', 'Arial', 18, W/2, H/2-60)
            scene.no_tint()

if __name__ == '__main__':
    scene.run(WhackMole())
