#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""无尽跳塔 — 纵向无尽跳跃，弹簧/碎裂/移动平台，金币与道具"""
import scene
import random
import math

PLAT_NORMAL = 0
PLAT_MOVING = 1
PLAT_FRAGILE = 2
PLAT_SPRING = 3

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

class Platform:
    __slots__ = ('x','y','w','kind','alive','move_dir','move_range','ox')
    def __init__(self, x, y, w, kind):
        self.x, self.y, self.w = x, y, w
        self.kind = kind
        self.alive = True
        self.move_dir = random.choice([-1, 1])
        self.move_range = random.uniform(30, 60)
        self.ox = x

class Coin:
    __slots__ = ('x','y','alive','pulse')
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.alive = True
        self.pulse = random.uniform(0, 6.28)

class JumpTower(scene.Scene):
    def setup(self):
        W, H = self.size.w, self.size.h
        self.player_x = W / 2
        self.player_y = H * 0.2
        self.player_w = 28
        self.player_h = 32
        self.vy = 0
        self.vx = 0
        self.camera_y = 0
        self.max_height = 0
        self.score = 0
        self.coins_collected = 0
        self.game_over = False
        self.frame = 0
        self.particles = []
        self.floats = []
        self.facing_right = True
        self.jump_stretch = 0
        self.on_ground = False

        self.platforms = []
        self.coins = []
        self._gen_initial_platforms()

        self.bg_stars = [{'x': random.uniform(0, W), 'y': random.uniform(0, H*3),
                          'sz': random.uniform(1, 2.5), 'br': random.uniform(0.1, 0.4)} for _ in range(80)]

    def _gen_initial_platforms(self):
        W, H = self.size.w, self.size.h
        y = 0
        base = Platform(W/2, 30, W, PLAT_NORMAL)
        self.platforms.append(base)
        y = 80
        while y < H * 2:
            self._add_platform_at(y)
            y += random.uniform(45, 75)

    def _add_platform_at(self, y):
        W = self.size.w
        pw = random.uniform(55, 90)
        px = random.uniform(pw/2 + 10, W - pw/2 - 10)
        height = max(0, y / 200)
        r = random.random()
        if height > 5 and r < 0.15:
            kind = PLAT_FRAGILE
        elif height > 3 and r < 0.3:
            kind = PLAT_MOVING
        elif r < 0.12:
            kind = PLAT_SPRING
        else:
            kind = PLAT_NORMAL
        p = Platform(px, y, pw, kind)
        self.platforms.append(p)
        if random.random() < 0.3:
            self.coins.append(Coin(px + random.uniform(-20, 20), y + 25))

    def touch_began(self, touch):
        if self.game_over:
            self.setup()
            return
        self._handle_touch(touch)

    def touch_moved(self, touch):
        if not self.game_over:
            self._handle_touch(touch)

    def touch_ended(self, touch):
        self.vx *= 0.5

    def _handle_touch(self, touch):
        W = self.size.w
        x = touch.location.x
        center = W / 2
        self.vx = (x - center) / center * 8
        if self.vx > 0:
            self.facing_right = True
        elif self.vx < 0:
            self.facing_right = False

    def update(self):
        self.frame += 1
        if self.game_over:
            self._upd_particles()
            return

        W, H = self.size.w, self.size.h
        gravity = -0.35

        self.vy += gravity
        self.player_y += self.vy
        self.player_x += self.vx
        self.vx *= 0.92

        if self.player_x < 0:
            self.player_x = W
        elif self.player_x > W:
            self.player_x = 0

        if self.jump_stretch > 0:
            self.jump_stretch -= 0.05

        self.on_ground = False
        if self.vy <= 0:
            for p in self.platforms:
                if not p.alive:
                    continue
                if (self.player_y > p.y and self.player_y < p.y + 15 and
                    abs(self.player_x - p.x) < (p.w/2 + self.player_w/2 - 5)):
                    if p.kind == PLAT_FRAGILE:
                        p.alive = False
                        for _ in range(8):
                            self.particles.append(Particle(p.x, p.y, 0.6, 0.5, 0.4, 3, 0.4))
                        self.vy = 10
                        self.jump_stretch = 1
                    elif p.kind == PLAT_SPRING:
                        self.vy = 18
                        self.jump_stretch = 1
                        for _ in range(5):
                            self.particles.append(Particle(self.player_x, self.player_y, 0.2, 1, 0.5, 4, 0.3))
                    else:
                        self.vy = 10
                        self.jump_stretch = 1
                    self.on_ground = True
                    break

        for p in self.platforms:
            if p.kind == PLAT_MOVING and p.alive:
                p.x += p.move_dir * 1.2
                if abs(p.x - p.ox) > p.move_range:
                    p.move_dir *= -1

        for c in self.coins:
            if not c.alive:
                continue
            if abs(self.player_x - c.x) < 20 and abs(self.player_y - c.y) < 20:
                c.alive = False
                self.coins_collected += 1
                self.score += 25
                self.floats.append({'x': c.x, 'y': c.y, 'text': '+25', 'life': 1.0})
                for _ in range(6):
                    self.particles.append(Particle(c.x, c.y, 1, 0.85, 0.15, 3, 0.4))

        if self.player_y > self.max_height:
            diff = int((self.player_y - self.max_height) / 10)
            self.score += diff
            self.max_height = self.player_y

        target_cam = self.player_y - H * 0.4
        self.camera_y += (target_cam - self.camera_y) * 0.1

        top_y = self.camera_y + H + 100
        if self.platforms:
            highest = max(p.y for p in self.platforms)
            while highest < top_y:
                highest += random.uniform(45, 75)
                self._add_platform_at(highest)

        self.platforms = [p for p in self.platforms if p.y > self.camera_y - 100 and p.alive]
        self.coins = [c for c in self.coins if c.y > self.camera_y - 100 and c.alive]

        if self.player_y < self.camera_y - 100:
            self.game_over = True
            for _ in range(20):
                self.particles.append(Particle(self.player_x, self.player_y, 1, 0.4, 0.2, 6, 0.8))

        self._upd_particles()
        for f in self.floats:
            f['y'] += 0.8; f['life'] -= 1/60
        self.floats = [f for f in self.floats if f['life'] > 0]

    def _upd_particles(self):
        dt = 1/60
        for p in self.particles:
            p.x += p.vx; p.y += p.vy; p.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]

    def _screen_y(self, world_y):
        return world_y - self.camera_y

    def draw(self):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        fc = self.frame
        cy = self.camera_y

        height_ratio = min(1, self.max_height / 5000)
        br = 0.05 + height_ratio*0.02
        bg = 0.04 + height_ratio*0.01
        bb = 0.12 - height_ratio*0.05
        scene.background(br, bg, max(0.02, bb))

        for s in self.bg_stars:
            sy = s['y'] - cy * 0.3
            sy = sy % (H * 3)
            if 0 < sy < H:
                a = s['br'] * (0.5 + 0.5*math.sin(fc*0.005 + s['br']*20))
                scene.fill(0.7, 0.8, 1, a)
                scene.rect(s['x'], sy, s['sz'], s['sz'])

        for p in self.platforms:
            if not p.alive:
                continue
            sy = self._screen_y(p.y)
            if sy < -20 or sy > H + 20:
                continue
            hw = p.w / 2
            if p.kind == PLAT_NORMAL:
                scene.fill(0.2, 0.55, 0.35)
                scene.rect(p.x - hw, sy, p.w, 10, 5)
                scene.fill(0.3, 0.75, 0.45, 0.4)
                scene.rect(p.x - hw + 3, sy + 7, p.w - 6, 2, 2)
            elif p.kind == PLAT_MOVING:
                scene.fill(0.2, 0.45, 0.8)
                scene.rect(p.x - hw, sy, p.w, 10, 5)
                scene.fill(0.4, 0.65, 1.0, 0.4)
                scene.rect(p.x - hw + 3, sy + 7, p.w - 6, 2, 2)
                scene.fill(0.4, 0.65, 1.0, 0.3)
                for i in range(3):
                    ax = p.x - hw + 10 + i*20
                    if ax < p.x + hw - 5:
                        scene.rect(ax, sy + 3, 8, 2, 1)
            elif p.kind == PLAT_FRAGILE:
                scene.fill(0.6, 0.45, 0.3)
                scene.rect(p.x - hw, sy, p.w, 10, 5)
                scene.stroke(0.4, 0.3, 0.2, 0.5)
                scene.stroke_weight(1)
                scene.line(p.x - hw + 10, sy + 2, p.x - hw + 20, sy + 8)
                scene.line(p.x + hw - 15, sy + 3, p.x + hw - 8, sy + 7)
                scene.no_stroke()
            elif p.kind == PLAT_SPRING:
                scene.fill(0.2, 0.55, 0.35)
                scene.rect(p.x - hw, sy, p.w, 10, 5)
                scene.fill(1.0, 0.3, 0.35)
                spring_w = 18
                scene.rect(p.x - spring_w/2, sy + 10, spring_w, 10, 4)
                scene.fill(1.0, 0.5, 0.5, 0.4)
                scene.rect(p.x - spring_w/2 + 3, sy + 17, spring_w - 6, 2, 1)

        for c in self.coins:
            if not c.alive:
                continue
            sy = self._screen_y(c.y)
            if sy < -20 or sy > H + 20:
                continue
            pulse = 0.7 + 0.3*math.sin(fc*0.06 + c.pulse)
            scene.fill(1, 0.85, 0.15, 0.12*pulse)
            scene.ellipse(c.x - 12, sy - 12, 24, 24)
            scene.fill(1, 0.85, 0.15)
            scene.ellipse(c.x - 7, sy - 7, 14, 14)
            scene.fill(1, 1, 0.6, 0.4)
            scene.ellipse(c.x - 3, sy + 1, 5, 5)

        py_screen = self._screen_y(self.player_y)
        px = self.player_x
        pw, ph = self.player_w, self.player_h
        stretch_y = 1 + self.jump_stretch * 0.15
        stretch_x = 1 - self.jump_stretch * 0.08
        scene.push_matrix()
        scene.translate(px, py_screen + ph/2)
        scene.scale(stretch_x if self.facing_right else -stretch_x, stretch_y)
        scene.fill(0.9, 0.65, 0.4)
        scene.ellipse(-pw*0.3, ph*0.05, pw*0.6, ph*0.55, )
        scene.fill(0.95, 0.75, 0.55)
        scene.ellipse(-pw*0.25, ph*0.35, pw*0.5, pw*0.5)
        scene.fill(0.2, 0.2, 0.25)
        scene.ellipse(pw*0.02, ph*0.5, 5, 5)
        scene.fill(1, 1, 1)
        scene.ellipse(pw*0.01, ph*0.52, 3, 3)
        if self.vy > 2:
            scene.fill(1, 0.6, 0.15, 0.5)
            scene.ellipse(-4, -ph*0.2, 8, 10)
            scene.fill(1, 0.8, 0.3, 0.3)
            scene.ellipse(-3, -ph*0.3, 6, 8)
        scene.pop_matrix()

        for p in self.particles:
            sy = self._screen_y(p.y)
            a = p.life / p.ml
            scene.fill(p.r, p.g, p.b, a*0.7)
            sz = p.sz * a
            scene.ellipse(p.x-sz/2, sy-sz/2, sz, sz)

        for f in self.floats:
            sy = self._screen_y(f['y'])
            scene.tint(1, 0.85, 0.15, f['life'])
            scene.text(f['text'], 'Arial-BoldMT', 14, f['x'], sy)
        scene.no_tint()

        hud_top = H - insets.top
        hud_h = 48
        scene.fill(br, bg, max(0.02, bb), 0.8)
        scene.rect(0, hud_top - hud_h, W, hud_h + insets.top)
        hcy = hud_top - hud_h / 2
        scene.tint(0.5, 0.8, 0.5)
        h_m = int(self.max_height / 10)
        scene.text(f'↑{h_m}m', 'Arial-BoldMT', 14, 40, hcy + 10)
        scene.tint(1, 1, 1)
        scene.text(f'{self.score}', 'Arial-BoldMT', 22, W/2, hcy + 2)
        scene.tint(0.5, 0.5, 0.6)
        scene.text('分数', 'Arial', 10, W/2, hcy + 17)
        scene.tint(1, 0.85, 0.15)
        scene.text(f'● {self.coins_collected}', 'Arial-BoldMT', 14, W - 45, hcy + 2)
        scene.no_tint()

        if self.game_over:
            scene.fill(0, 0, 0, 0.8)
            scene.rect(0, 0, W, H)
            p = 1 + 0.03*math.sin(fc*0.06)
            scene.push_matrix()
            scene.translate(W/2, H/2+70)
            scene.scale(p, p)
            scene.tint(1, 0.5, 0.3)
            scene.text('坠落了!', 'Arial-BoldMT', 40, 0, 0)
            scene.pop_matrix()
            scene.tint(1, 0.95, 0.7)
            scene.text(f'{self.score}', 'Arial-BoldMT', 48, W/2, H/2+15)
            scene.tint(0.6, 0.6, 0.7)
            scene.text('最终分数', 'Arial', 14, W/2, H/2+40)
            scene.tint(0.8, 0.8, 0.9)
            scene.text(f'高度 {int(self.max_height/10)}m  |  金币 {self.coins_collected}', 'Arial', 16, W/2, H/2-15)
            blink = 0.4+0.6*abs(math.sin(fc*0.04))
            scene.tint(0.6, 0.7, 0.9, blink)
            scene.text('轻触屏幕再来一局', 'Arial', 18, W/2, H/2-50)
            scene.no_tint()

if __name__ == '__main__':
    scene.run(JumpTower())
