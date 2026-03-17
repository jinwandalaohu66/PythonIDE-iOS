#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重力迷宫 — 倾斜手机控制小球穿越迷宫（使用重力感应器）"""
import scene
import random
import math

class Particle:
    __slots__ = ('x','y','vx','vy','r','g','b','life','ml','sz')
    def __init__(self, x, y, r, g, b):
        a = random.uniform(0, math.pi*2)
        s = random.uniform(0.5, 3)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a)*s, math.sin(a)*s
        self.r, self.g, self.b = r, g, b
        self.life = random.uniform(0.2, 0.5)
        self.ml = self.life
        self.sz = random.uniform(2, 4)

LEVEL_DATA = [
    {'walls': [(0.05,0.25,0.65,0.03),(0.35,0.45,0.03,0.25),(0.6,0.15,0.03,0.35),
               (0.2,0.65,0.55,0.03),(0.75,0.4,0.03,0.35),(0.1,0.85,0.6,0.03)],
     'goal': (0.85, 0.9), 'coins': [(0.15,0.4),(0.5,0.3),(0.7,0.6),(0.4,0.8),(0.9,0.2)]},
    {'walls': [(0.1,0.2,0.5,0.03),(0.5,0.2,0.03,0.25),(0.3,0.4,0.45,0.03),
               (0.1,0.55,0.35,0.03),(0.55,0.55,0.03,0.2),(0.4,0.75,0.45,0.03),
               (0.15,0.75,0.03,0.15),(0.7,0.3,0.03,0.25)],
     'goal': (0.9, 0.85), 'coins': [(0.3,0.3),(0.7,0.5),(0.2,0.7),(0.8,0.15),(0.5,0.65),(0.15,0.9)]},
    {'walls': [(0.05,0.15,0.4,0.03),(0.55,0.15,0.4,0.03),(0.45,0.15,0.03,0.2),
               (0.2,0.3,0.03,0.25),(0.35,0.45,0.35,0.03),(0.7,0.3,0.03,0.15),
               (0.1,0.55,0.25,0.03),(0.5,0.6,0.03,0.2),(0.65,0.55,0.3,0.03),
               (0.3,0.75,0.5,0.03),(0.1,0.85,0.03,0.1),(0.8,0.75,0.03,0.15)],
     'goal': (0.9, 0.92), 'coins': [(0.1,0.25),(0.7,0.25),(0.5,0.5),(0.2,0.65),(0.8,0.7),(0.5,0.85),(0.15,0.45)]},
]


class GravityMaze(scene.Scene):
    def setup(self):
        W, H = self.size.w, self.size.h
        self.ball_r = 10
        self.ball_x = W * 0.1
        self.ball_y = H * 0.08
        self.ball_vx = 0
        self.ball_vy = 0
        self.level = 0
        self.score = 0
        self.total_coins = 0
        self.time_elapsed = 0
        self.game_over = False
        self.win = False
        self.particles = []
        self.frame = 0
        self.trail = []
        self._load_level()

    def _load_level(self):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        play_top = H - insets.top - 55
        play_bot = insets.bottom + 10
        play_h = play_top - play_bot
        data = LEVEL_DATA[self.level % len(LEVEL_DATA)]
        self.walls = []
        for wx, wy, ww, wh in data['walls']:
            self.walls.append((wx * W, play_bot + wy * play_h, ww * W, wh * play_h))
        gx, gy = data['goal']
        self.goal_x = gx * W
        self.goal_y = play_bot + gy * play_h
        self.goal_r = 16
        self.coins = []
        for cx, cy in data['coins']:
            self.coins.append({'x': cx * W, 'y': play_bot + cy * play_h, 'alive': True, 'pulse': random.uniform(0, 6.28)})
        self.ball_x = W * 0.1
        self.ball_y = play_bot + play_h * 0.05
        self.ball_vx = 0
        self.ball_vy = 0
        self.play_top = play_top
        self.play_bot = play_bot

    def touch_began(self, touch):
        if self.game_over or self.win:
            self.setup()

    def touch_moved(self, touch):
        pass

    def touch_ended(self, touch):
        pass

    def update(self):
        if self.game_over or self.win:
            self.frame += 1
            self._upd_particles()
            return
        self.frame += 1
        self.time_elapsed += 1.0 / 60.0
        W, H = self.size.w, self.size.h

        g = scene.gravity()
        ax = g.x * 18
        ay = g.y * 18

        self.ball_vx += ax
        self.ball_vy += ay
        friction = 0.96
        self.ball_vx *= friction
        self.ball_vy *= friction

        step = 4
        dx = self.ball_vx / step
        dy = self.ball_vy / step
        for _ in range(step):
            nx = self.ball_x + dx
            ny = self.ball_y + dy
            r = self.ball_r
            nx = max(r, min(W - r, nx))
            ny = max(self.play_bot + r, min(self.play_top - r, ny))
            for wx, wy, ww, wh in self.walls:
                cx = max(wx, min(nx, wx + ww))
                cy = max(wy, min(ny, wy + wh))
                ddx = nx - cx
                ddy = ny - cy
                dist = math.sqrt(ddx*ddx + ddy*ddy)
                if dist < r:
                    if dist > 0:
                        overlap = r - dist
                        nx += ddx / dist * overlap
                        ny += ddy / dist * overlap
                        dot = self.ball_vx * ddx/dist + self.ball_vy * ddy/dist
                        if dot < 0:
                            self.ball_vx -= 1.5 * dot * ddx/dist
                            self.ball_vy -= 1.5 * dot * ddy/dist
                            self.ball_vx *= 0.7
                            self.ball_vy *= 0.7
            self.ball_x, self.ball_y = nx, ny

        if self.frame % 2 == 0:
            self.trail.append((self.ball_x, self.ball_y, 0.4))
        new_trail = []
        for tx, ty, tl in self.trail:
            tl -= 1/60
            if tl > 0:
                new_trail.append((tx, ty, tl))
        self.trail = new_trail

        for c in self.coins:
            if not c['alive']:
                continue
            ddx = self.ball_x - c['x']
            ddy = self.ball_y - c['y']
            if ddx*ddx + ddy*ddy < (self.ball_r + 10)**2:
                c['alive'] = False
                self.score += 50
                self.total_coins += 1
                for _ in range(8):
                    self.particles.append(Particle(c['x'], c['y'], 1.0, 0.9, 0.2))

        ddx = self.ball_x - self.goal_x
        ddy = self.ball_y - self.goal_y
        if ddx*ddx + ddy*ddy < (self.ball_r + self.goal_r)**2:
            time_bonus = max(0, int(300 - self.time_elapsed * 10))
            self.score += 100 + time_bonus
            for _ in range(20):
                self.particles.append(Particle(self.goal_x, self.goal_y, 0.2, 1.0, 0.5))
            if self.level + 1 >= len(LEVEL_DATA):
                self.win = True
            else:
                self.level += 1
                self.time_elapsed = 0
                self._load_level()

        self._upd_particles()

    def _upd_particles(self):
        dt = 1/60
        for p in self.particles:
            p.x += p.vx; p.y += p.vy; p.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        fc = self.frame

        scene.background(0.06, 0.06, 0.12)

        scene.stroke(0.12, 0.12, 0.2, 0.15)
        scene.stroke_weight(1)
        sp = 40
        for gx in range(0, int(W), sp):
            scene.line(gx, self.play_bot, gx, self.play_top)
        for gy in range(int(self.play_bot), int(self.play_top), sp):
            scene.line(0, gy, W, gy)
        scene.no_stroke()

        scene.fill(0.15, 0.15, 0.25, 0.6)
        scene.rect(0, self.play_bot, W, 2)
        scene.rect(0, self.play_top - 2, W, 2)

        for wx, wy, ww, wh in self.walls:
            scene.fill(0.3, 0.35, 0.5)
            scene.rect(wx, wy, ww, wh, 3)
            scene.fill(0.5, 0.55, 0.7, 0.3)
            scene.rect(wx + 1, wy + wh - 3, ww - 2, 2, 1)

        pulse = 0.7 + 0.3 * math.sin(fc * 0.08)
        scene.fill(0.15, 0.9, 0.4, 0.15 * pulse)
        scene.ellipse(self.goal_x - self.goal_r * 2, self.goal_y - self.goal_r * 2,
                      self.goal_r * 4, self.goal_r * 4)
        scene.fill(0.2, 1.0, 0.5, 0.8)
        scene.ellipse(self.goal_x - self.goal_r, self.goal_y - self.goal_r,
                      self.goal_r * 2, self.goal_r * 2)
        scene.fill(0.5, 1, 0.7, 0.5)
        scene.ellipse(self.goal_x - 5, self.goal_y + 3, 7, 7)
        scene.tint(1, 1, 1)
        scene.text('★', 'Arial', 18, self.goal_x, self.goal_y)
        scene.no_tint()

        for c in self.coins:
            if not c['alive']:
                continue
            cp = 0.7 + 0.3 * math.sin(fc * 0.06 + c['pulse'])
            scene.fill(1.0, 0.85, 0.15, 0.15 * cp)
            scene.ellipse(c['x'] - 14, c['y'] - 14, 28, 28)
            scene.fill(1.0, 0.85, 0.15, 0.9)
            scene.ellipse(c['x'] - 8, c['y'] - 8, 16, 16)
            scene.fill(1, 1, 0.6, 0.4)
            scene.ellipse(c['x'] - 4, c['y'] + 2, 6, 6)

        for tx, ty, tl in self.trail:
            a = tl / 0.4 * 0.2
            scene.fill(0.3, 0.7, 1.0, a)
            sz = self.ball_r * (tl / 0.4)
            scene.ellipse(tx - sz/2, ty - sz/2, sz, sz)

        r = self.ball_r
        scene.fill(0.2, 0.6, 1.0, 0.12)
        scene.ellipse(self.ball_x - r*2, self.ball_y - r*2, r*4, r*4)
        scene.fill(0.25, 0.65, 1.0)
        scene.ellipse(self.ball_x - r, self.ball_y - r, r*2, r*2)
        scene.fill(0.6, 0.85, 1.0, 0.6)
        scene.ellipse(self.ball_x - r*0.4, self.ball_y + r*0.2, r*0.7, r*0.7)
        spd = math.sqrt(self.ball_vx**2 + self.ball_vy**2)
        if spd > 2:
            scene.fill(0.4, 0.8, 1.0, min(0.4, spd*0.05))
            scene.ellipse(self.ball_x - r*1.5, self.ball_y - r*1.5, r*3, r*3)

        for p in self.particles:
            a = p.life / p.ml
            scene.fill(p.r, p.g, p.b, a*0.8)
            sz = p.sz * a
            scene.ellipse(p.x - sz/2, p.y - sz/2, sz, sz)

        hud_top = H - insets.top
        hud_h = 48
        scene.fill(0.06, 0.06, 0.12, 0.8)
        scene.rect(0, hud_top - hud_h, W, hud_h + insets.top)
        cy = hud_top - hud_h / 2
        scene.tint(0.5, 0.8, 1.0)
        scene.text(f'关卡 {self.level + 1}/{len(LEVEL_DATA)}', 'Arial-BoldMT', 14, 50, cy + 10)
        scene.tint(1, 1, 1)
        scene.text(f'{self.score}', 'Arial-BoldMT', 22, W/2, cy + 2)
        scene.tint(0.5, 0.5, 0.6)
        scene.text('分数', 'Arial', 10, W/2, cy + 17)
        t = int(self.time_elapsed)
        scene.tint(0.9, 0.8, 0.5)
        scene.text(f'{t//60:01d}:{t%60:02d}', 'Arial-BoldMT', 16, W - 45, cy + 2)
        coins_left = sum(1 for c in self.coins if c['alive'])
        scene.tint(1, 0.85, 0.15)
        scene.text(f'●{self.total_coins}', 'Arial-BoldMT', 14, W - 45, cy - 14)
        scene.no_tint()

        g = scene.gravity()
        ind_x = W - 30
        ind_y = hud_top - hud_h - 30
        scene.fill(0.15, 0.15, 0.25, 0.5)
        scene.ellipse(ind_x - 15, ind_y - 15, 30, 30)
        dot_x = ind_x + g.x * 10
        dot_y = ind_y + g.y * 10
        scene.fill(0.3, 0.8, 1.0, 0.8)
        scene.ellipse(dot_x - 3, dot_y - 3, 6, 6)

        if self.win:
            scene.fill(0, 0, 0, 0.8)
            scene.rect(0, 0, W, H)
            scene.tint(0.2, 1, 0.5)
            scene.text('通关!', 'Arial-BoldMT', 44, W/2, H/2+60)
            scene.tint(1, 0.95, 0.7)
            scene.text(f'{self.score}', 'Arial-BoldMT', 48, W/2, H/2+10)
            scene.tint(0.6, 0.6, 0.7)
            scene.text('最终分数', 'Arial', 14, W/2, H/2+35)
            blink = 0.4 + 0.6*abs(math.sin(fc*0.04))
            scene.tint(0.6, 0.8, 0.7, blink)
            scene.text('轻触屏幕再来一次', 'Arial', 18, W/2, H/2-40)
            scene.no_tint()

if __name__ == '__main__':
    scene.run(GravityMaze())
