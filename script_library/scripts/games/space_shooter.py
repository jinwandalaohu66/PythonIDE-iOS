#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""太空射击 — 纵向卷轴射击游戏"""
import scene
import random
import math

ENEMY_COLORS = [
    (1.0, 0.3, 0.3), (1.0, 0.6, 0.15), (0.9, 0.2, 0.8),
    (0.3, 0.9, 0.5), (0.4, 0.6, 1.0),
]

class Particle:
    __slots__ = ('x','y','vx','vy','r','g','b','life','ml','sz')
    def __init__(self, x, y, r, g, b, spread=5, life=0.6):
        self.x, self.y = x, y
        a = random.uniform(0, math.pi*2)
        s = random.uniform(1, spread)
        self.vx, self.vy = math.cos(a)*s, math.sin(a)*s
        self.r, self.g, self.b = r, g, b
        self.life = random.uniform(life*0.4, life)
        self.ml = self.life
        self.sz = random.uniform(2, 5)

class Bullet:
    __slots__ = ('x','y','vy','vx_extra','friendly','r','g','b','sz')
    def __init__(self, x, y, vy, friendly=True):
        self.x, self.y, self.vy = x, y, vy
        self.vx_extra = 0
        self.friendly = friendly
        if friendly:
            self.r, self.g, self.b = 0.3, 1.0, 0.9
        else:
            self.r, self.g, self.b = 1.0, 0.3, 0.2
        self.sz = 4 if friendly else 3

class Enemy:
    __slots__ = ('x','y','w','h','hp','max_hp','color','speed','shoot_cd','kind','phase')
    def __init__(self, x, y, kind, level):
        self.x, self.y = x, y
        self.kind = kind
        self.color = random.choice(ENEMY_COLORS)
        self.phase = random.uniform(0, math.pi*2)
        if kind == 'normal':
            self.w, self.h = 32, 28
            self.hp = 1 + level // 3
            self.speed = 1.2 + level * 0.1
            self.shoot_cd = random.randint(80, 150)
        elif kind == 'fast':
            self.w, self.h = 24, 22
            self.hp = 1
            self.speed = 2.5 + level * 0.15
            self.shoot_cd = random.randint(60, 100)
            self.color = (1.0, 0.9, 0.2)
        elif kind == 'tank':
            self.w, self.h = 44, 36
            self.hp = 4 + level // 2
            self.speed = 0.6
            self.shoot_cd = random.randint(50, 90)
            self.color = (0.8, 0.2, 0.2)
        elif kind == 'boss':
            self.w, self.h = 80, 50
            self.hp = 20 + level * 5
            self.speed = 0.4
            self.shoot_cd = 25
            self.color = (0.9, 0.1, 0.5)
        self.max_hp = self.hp

class SpaceShooter(scene.Scene):
    def setup(self):
        W, H = self.size.w, self.size.h
        self.player_x = W / 2
        self.player_y = H * 0.1
        self.player_w = 36
        self.player_h = 40
        self.bullets = []
        self.enemies = []
        self.particles = []
        self.stars = [{'x': random.uniform(0, W), 'y': random.uniform(0, H),
                       'sp': random.uniform(0.5, 3), 'br': random.uniform(0.2, 0.7),
                       'sz': random.uniform(1, 2.5)} for _ in range(100)]
        self.score = 0
        self.lives = 3
        self.level = 1
        self.frame = 0
        self.spawn_cd = 60
        self.game_over = False
        self.shoot_cd = 0
        self.kills = 0
        self.combo = 0
        self.combo_timer = 0
        self.floats = []
        self.boss_spawned = False
        self.invincible = 0
        self.touch_offset_y = 60

    def touch_began(self, touch):
        if self.game_over:
            self.setup()
            return
        self._move(touch)

    def touch_moved(self, touch):
        if not self.game_over:
            self._move(touch)

    def touch_ended(self, touch):
        pass

    def _move(self, touch):
        x, y = touch.location
        self.player_x = max(self.player_w/2, min(self.size.w - self.player_w/2, x))
        self.player_y = max(20, min(self.size.h * 0.5, y + self.touch_offset_y))

    def update(self):
        if self.game_over:
            self.frame += 1
            self._upd_particles()
            return
        self.frame += 1
        W, H = self.size.w, self.size.h

        if self.invincible > 0:
            self.invincible -= 1
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo = 0

        for s in self.stars:
            s['y'] -= s['sp']
            if s['y'] < 0:
                s['y'] = H; s['x'] = random.uniform(0, W)

        if self.shoot_cd > 0:
            self.shoot_cd -= 1
        else:
            self.bullets.append(Bullet(self.player_x - 8, self.player_y + self.player_h/2, 9))
            self.bullets.append(Bullet(self.player_x + 8, self.player_y + self.player_h/2, 9))
            self.shoot_cd = 8

        self.spawn_cd -= 1
        if self.spawn_cd <= 0:
            if self.kills > 0 and self.kills % 15 == 0 and not self.boss_spawned:
                self.enemies.append(Enemy(W/2, H + 30, 'boss', self.level))
                self.boss_spawned = True
                self.spawn_cd = 200
            else:
                kind = random.choices(['normal','fast','tank'], weights=[5,3,1])[0]
                ex = random.uniform(30, W - 30)
                self.enemies.append(Enemy(ex, H + 20, kind, self.level))
                self.spawn_cd = max(15, 50 - self.level * 3)

        for e in self.enemies:
            if e.kind == 'boss':
                e.x += math.sin(self.frame * 0.02 + e.phase) * 1.5
                e.y -= e.speed * 0.3
                if e.y < H * 0.7:
                    e.y = H * 0.7
            else:
                e.y -= e.speed
                if e.kind == 'fast':
                    e.x += math.sin(self.frame * 0.05 + e.phase) * 2
            e.shoot_cd -= 1
            if e.shoot_cd <= 0 and e.y < H - 20:
                if e.kind == 'boss':
                    for angle_off in [-0.3, 0, 0.3]:
                        b = Bullet(e.x, e.y - e.h/2, -5, False)
                        b.vx_extra = math.sin(angle_off) * 2
                        self.bullets.append(b)
                    e.shoot_cd = 30
                else:
                    self.bullets.append(Bullet(e.x, e.y - e.h/2, -4, False))
                    e.shoot_cd = random.randint(60, 120)

        for b in self.bullets:
            b.y += b.vy
            b.x += b.vx_extra

        self.bullets = [b for b in self.bullets if -10 < b.y < H + 10 and -10 < b.x < W + 10]

        for b in list(self.bullets):
            if not b.friendly:
                continue
            for e in self.enemies:
                if e.hp <= 0:
                    continue
                if abs(b.x - e.x) < e.w/2 and abs(b.y - e.y) < e.h/2:
                    e.hp -= 1
                    if b in self.bullets:
                        self.bullets.remove(b)
                    for _ in range(3):
                        self.particles.append(Particle(b.x, b.y, 1, 1, 1, 3, 0.3))
                    if e.hp <= 0:
                        self.combo += 1
                        self.combo_timer = 90
                        pts = {'normal': 10, 'fast': 15, 'tank': 30, 'boss': 200}[e.kind]
                        pts *= self.combo
                        self.score += pts
                        self.kills += 1
                        if e.kind == 'boss':
                            self.boss_spawned = False
                            self.level += 1
                        c = e.color
                        for _ in range(20 if e.kind == 'boss' else 12):
                            self.particles.append(Particle(e.x, e.y, c[0], c[1], c[2], 7, 0.8))
                        self.floats.append({'x': e.x, 'y': e.y, 'text': f'+{pts}', 'life': 1.0, 'color': c})
                    break

        if self.invincible <= 0:
            for b in list(self.bullets):
                if b.friendly:
                    continue
                if abs(b.x - self.player_x) < self.player_w/2 and abs(b.y - self.player_y) < self.player_h/2:
                    self.lives -= 1
                    self.invincible = 90
                    if b in self.bullets:
                        self.bullets.remove(b)
                    for _ in range(10):
                        self.particles.append(Particle(self.player_x, self.player_y, 0.3, 0.8, 1.0, 5, 0.6))
                    if self.lives <= 0:
                        self.game_over = True
                        for _ in range(30):
                            self.particles.append(Particle(self.player_x, self.player_y, 1, 0.5, 0.2, 8, 1.0))
                    break

        self.enemies = [e for e in self.enemies if e.hp > 0 and e.y > -60]

        for f in self.floats:
            f['y'] += 0.8; f['life'] -= 1/60
        self.floats = [f for f in self.floats if f['life'] > 0]

        self._upd_particles()

    def _upd_particles(self):
        dt = 1/60
        for p in self.particles:
            p.x += p.vx; p.y += p.vy; p.vy -= 3*dt; p.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        fc = self.frame

        scene.background(0.01, 0.01, 0.05)

        for s in self.stars:
            scene.fill(0.7, 0.8, 1.0, s['br'] * (0.5 + 0.5*math.sin(fc*0.01+s['br']*10)))
            scene.rect(s['x'], s['y'], s['sz'], s['sz'])

        for b in self.bullets:
            scene.fill(b.r, b.g, b.b, 0.15)
            scene.ellipse(b.x - b.sz*2, b.y - b.sz*2, b.sz*4, b.sz*4)
            scene.fill(b.r, b.g, b.b)
            scene.ellipse(b.x - b.sz/2, b.y - b.sz/2, b.sz, b.sz)

        for e in self.enemies:
            if e.hp <= 0:
                continue
            r, g, b = e.color
            scene.fill(r*0.3, g*0.3, b*0.3, 0.4)
            scene.rect(e.x - e.w/2 + 2, e.y - e.h/2 - 2, e.w, e.h, 4)
            scene.fill(r, g, b)
            scene.rect(e.x - e.w/2, e.y - e.h/2, e.w, e.h, 4)
            scene.fill(1, 1, 1, 0.15)
            scene.rect(e.x - e.w/2 + 3, e.y + e.h/2 - 6, e.w - 6, 4, 2)
            if e.max_hp > 1:
                bar_w = e.w
                hp_ratio = e.hp / e.max_hp
                scene.fill(0.2, 0.2, 0.2, 0.6)
                scene.rect(e.x - bar_w/2, e.y + e.h/2 + 4, bar_w, 4, 2)
                scene.fill(0.2, 1, 0.3)
                scene.rect(e.x - bar_w/2, e.y + e.h/2 + 4, bar_w * hp_ratio, 4, 2)

        if not self.game_over:
            if self.invincible > 0 and fc % 6 < 3:
                pass
            else:
                px, py = self.player_x, self.player_y
                pw, ph = self.player_w, self.player_h
                scene.fill(0.15, 0.5, 1.0, 0.1)
                scene.ellipse(px - pw, py - ph, pw*2, ph*2)
                scene.fill(0.2, 0.65, 1.0)
                scene.rect(px - pw*0.15, py - ph*0.45, pw*0.3, ph*0.9, 3)
                scene.fill(0.15, 0.55, 0.95)
                scene.rect(px - pw*0.45, py - ph*0.2, pw*0.9, ph*0.35, 4)
                scene.fill(0.5, 0.85, 1.0, 0.5)
                scene.rect(px - pw*0.1, py + ph*0.15, pw*0.2, ph*0.25, 2)
                scene.fill(1.0, 0.6, 0.15, 0.7)
                scene.ellipse(px - 4, py - ph*0.5, 8, 10)
                flicker = random.uniform(0.6, 1.0)
                scene.fill(1.0, 0.8, 0.2, flicker)
                scene.ellipse(px - 3, py - ph*0.55, 6, 8)

        for p in self.particles:
            a = p.life / p.ml
            scene.fill(p.r, p.g, p.b, a * 0.8)
            sz = p.sz * a
            scene.ellipse(p.x - sz/2, p.y - sz/2, sz, sz)

        for f in self.floats:
            c = f['color']
            scene.tint(c[0], c[1], c[2], f['life'])
            scene.text(f['text'], 'Arial-BoldMT', 15, f['x'], f['y'])
        scene.no_tint()

        hud_top = H - insets.top
        hud_h = 48
        scene.fill(0.01, 0.01, 0.05, 0.7)
        scene.rect(0, hud_top - hud_h, W, hud_h + insets.top)

        cy = hud_top - hud_h / 2
        scene.tint(0.5, 0.8, 1.0)
        scene.text(f'WAVE {self.level}', 'Arial-BoldMT', 13, 35, cy + 12)
        scene.tint(1, 1, 1)
        scene.text(f'{self.score}', 'Arial-BoldMT', 22, W/2, cy + 2)
        scene.tint(0.5, 0.5, 0.6)
        scene.text('分数', 'Arial', 10, W/2, cy + 17)
        if self.combo > 1:
            ca = 0.6 + 0.4 * math.sin(fc * 0.12)
            scene.tint(1, 0.8, 0.2, ca)
            scene.text(f'x{self.combo}', 'Arial-BoldMT', 16, W/2, cy - 13)
        for i in range(self.lives):
            scene.fill(1, 0.25, 0.4)
            scene.ellipse(W - 22 - i*18, cy - 4, 10, 10)
        scene.no_tint()

        if self.game_over:
            scene.fill(0, 0, 0, 0.8)
            scene.rect(0, 0, W, H)
            p = 1 + 0.04*math.sin(fc*0.06)
            scene.push_matrix()
            scene.translate(W/2, H/2+60)
            scene.scale(p, p)
            scene.tint(1, 0.3, 0.3)
            scene.text('任务失败', 'Arial-BoldMT', 40, 0, 0)
            scene.pop_matrix()
            scene.tint(1, 0.95, 0.7)
            scene.text(f'{self.score}', 'Arial-BoldMT', 48, W/2, H/2+10)
            scene.tint(0.6, 0.6, 0.7)
            scene.text('最终分数', 'Arial', 14, W/2, H/2+38)
            scene.tint(0.8, 0.8, 0.9)
            scene.text(f'波次 {self.level}  |  击杀 {self.kills}', 'Arial', 16, W/2, H/2-20)
            blink = 0.4 + 0.6*abs(math.sin(fc*0.04))
            scene.tint(0.6, 0.7, 0.9, blink)
            scene.text('轻触屏幕再来一局', 'Arial', 18, W/2, H/2-55)
            scene.no_tint()

if __name__ == '__main__':
    scene.run(SpaceShooter())
