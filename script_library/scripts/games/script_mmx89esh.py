#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""霓虹飞鸟 — 赛博朋克 Flappy Bird，粒子爆炸、无尽上头、最高引流神器"""

from scene import *
import random
import math

class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'r', 'g', 'b', 'life', 'ml', 'sz')
    def __init__(self, x, y, r, g, b, spread=4, life=0.6):
        a = random.uniform(0, math.pi * 2)
        s = random.uniform(0.5, spread)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a) * s, math.sin(a) * s
        self.r, self.g, self.b = r, g, b
        self.life = random.uniform(life * 0.4, life)
        self.ml = self.life
        self.sz = random.uniform(2, 5)

class NeonFlappy(Scene):
    def setup(self):
        self.W, self.H = self.size.w, self.size.h
        self.bird_x = self.W * 0.25
        self.bird_y = self.H * 0.6
        self.bird_vy = 0
        self.bird_angle = 0
        self.gravity = -0.38
        self.jump_force = 10.2
        self.speed = 2.8
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.frame = 0
        self.spawn_timer = 0
        self.pipes = []
        self.particles = []
        self.floats = []
        self.bg_stars = [{'x': random.uniform(0, self.W), 'y': random.uniform(0, self.H),
                          'sp': random.uniform(0.3, 1.2), 'br': random.uniform(0.2, 0.8),
                          'sz': random.uniform(1, 3)} for _ in range(90)]
        self._spawn_pipe()
        self._spawn_pipe()

    def touch_began(self, touch):
        if self.game_over:
            self.setup()
            return
        self.bird_vy = self.jump_force
        for _ in range(12):
            self.particles.append(Particle(self.bird_x - 10, self.bird_y - 5, 0.3, 1.0, 0.95, 3, 0.4))

    def _spawn_pipe(self):
        gap_y = random.randint(int(self.H * 0.3), int(self.H * 0.65))
        gap_size = 155
        self.pipes.append({'x': self.W + 60, 'gap_y': gap_y, 'gap_size': gap_size, 'passed': False})

    def _die(self):
        self.game_over = True
        if self.score > self.high_score:
            self.high_score = self.score
        for _ in range(35):
            self.particles.append(Particle(self.bird_x, self.bird_y, 1.0, 0.4, 0.2, 7, 1.1))

    def update(self):
        if self.game_over:
            for p in self.particles[:]:
                p.x += p.vx
                p.y += p.vy
                p.vy += 0.15
                p.life -= 0.025
                if p.life <= 0:
                    self.particles.remove(p)
            return

        self.frame += 1

        self.bird_vy += self.gravity
        self.bird_y += self.bird_vy
        self.bird_angle = max(-35, min(35, self.bird_vy * 2.8))

        if self.bird_y < 60 or self.bird_y > self.H - 60:
            self._die()

        for p in self.pipes[:]:
            p['x'] -= self.speed
            if p['x'] < -80:
                self.pipes.remove(p)
                continue
            if not p['passed'] and p['x'] + 40 < self.bird_x:
                p['passed'] = True
                self.score += 1
                self.floats.append({'x': p['x'] + 30, 'y': p['gap_y'], 'text': '+1', 'life': 1.2})
                for _ in range(6):
                    self.particles.append(Particle(p['x'] + 30, p['gap_y'], 0.9, 1.0, 0.3, 2.5, 0.5))
            if self.score > 0 and self.score % 10 == 0 and self.frame % 90 == 0:
                self.speed = min(5.5, self.speed + 0.15)

        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self._spawn_pipe()
            self.spawn_timer = 65

        # 碰撞检测（修复：鸟在缝隙外面才判定死亡）
        bird_r = 18
        for p in self.pipes:
            gap_bottom = p['gap_y'] - p['gap_size'] // 2
            gap_top = p['gap_y'] + p['gap_size'] // 2
            if (abs(self.bird_x - (p['x'] + 30)) < bird_r + 30 and
                (self.bird_y - bird_r < gap_bottom or self.bird_y + bird_r > gap_top)):
                self._die()
                break

        for p in self.particles[:]:
            p.x += p.vx
            p.y += p.vy
            p.life -= 0.028
            if p.life <= 0:
                self.particles.remove(p)

        for f in self.floats[:]:
            f['y'] += 1.2
            f['life'] -= 0.035
            if f['life'] <= 0:
                self.floats.remove(f)

        for s in self.bg_stars:
            s['x'] -= s['sp']
            if s['x'] < 0:
                s['x'] = self.W

    def draw(self):
        background(0.03, 0.0, 0.12)

        no_stroke()
        for s in self.bg_stars:
            fill(1, 1, 1, s['br'])
            rect(s['x'], s['y'], s['sz'], s['sz'])

        # 管子（霓虹发光）
        for p in self.pipes:
            gb = p['gap_y'] - p['gap_size'] // 2
            gt = p['gap_y'] + p['gap_size'] // 2
            # 下管（地面到缝隙下沿）
            no_stroke()
            fill(0.08, 0.5, 0.65)
            rect(p['x'], 0, 64, gb)
            stroke(0.4, 1.0, 1.0)
            stroke_weight(3)
            no_fill()
            rect(p['x'], 0, 64, gb)
            # 上管（缝隙上沿到屏幕顶）
            no_stroke()
            fill(0.08, 0.5, 0.65)
            rect(p['x'], gt, 64, self.H - gt)
            stroke(0.4, 1.0, 1.0)
            stroke_weight(3)
            no_fill()
            rect(p['x'], gt, 64, self.H - gt)

        no_stroke()

        # 鸟（霓虹粉紫 + 旋转）
        push_matrix()
        translate(self.bird_x, self.bird_y)
        rotate(self.bird_angle)
        fill(1.0, 0.35, 0.9)
        ellipse(-18, -14, 36, 28)
        fill(1.0, 1.0, 0.3)
        ellipse(8, 2, 12, 12)
        fill(0, 0, 0)
        ellipse(12, 8, 6, 8)
        fill(1, 1, 1)
        ellipse(13, 9, 3, 3)
        pop_matrix()

        # 粒子
        for p in self.particles:
            a = p.life / p.ml
            fill(p.r, p.g, p.b, a)
            ellipse(p.x, p.y, p.sz * a, p.sz * a)

        # 浮动分数
        for f in self.floats:
            a = f['life']
            fill(1, 1, 0.4, a)
            text(f['text'], 'Helvetica-Bold', 36, f['x'], f['y'])

        # 分数
        fill(1, 1, 1)
        text(str(self.score), 'Helvetica-Bold', 72, self.W / 2, self.H * 0.88)

        if self.game_over:
            fill(1.0, 0.3, 0.3)
            text("GAME OVER", 'Helvetica-Bold', 64, self.W / 2, self.H * 0.55)
            fill(1, 1, 1)
            text(f"最高分 {self.high_score}", 'Helvetica', 42, self.W / 2, self.H * 0.45)
            text("轻点屏幕重新开始", 'Helvetica', 28, self.W / 2, self.H * 0.3)

run(NeonFlappy())
