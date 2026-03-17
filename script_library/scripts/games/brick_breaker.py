#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scene 模块全面测试游戏 — 霓虹弹球
涵盖: background, fill, rect, ellipse, line, text, tint,
      stroke, stroke_weight, no_fill, no_stroke, no_tint,
      push_matrix, pop_matrix, translate, rotate, scale,
      corner_radius, touch, safe_area_insets, 透明度
"""
import scene
import random
import math

# ─── 关卡配色方案 ───
LEVEL_PALETTES = [
    # Level 1: 霓虹赛博
    [(1.0, 0.15, 0.4), (1.0, 0.4, 0.1), (1.0, 0.85, 0.1),
     (0.1, 0.95, 0.5), (0.1, 0.7, 1.0), (0.6, 0.3, 1.0), (1.0, 0.3, 0.85)],
    # Level 2: 冰霜
    [(0.5, 0.85, 1.0), (0.3, 0.7, 0.95), (0.6, 0.9, 1.0),
     (0.8, 0.95, 1.0), (0.4, 0.6, 0.9), (0.2, 0.5, 0.85), (0.7, 0.85, 0.95)],
    # Level 3: 岩浆
    [(1.0, 0.2, 0.05), (1.0, 0.4, 0.0), (1.0, 0.6, 0.1),
     (0.9, 0.15, 0.0), (1.0, 0.8, 0.2), (0.8, 0.1, 0.05), (1.0, 0.5, 0.15)],
    # Level 4: 森林
    [(0.2, 0.8, 0.3), (0.1, 0.65, 0.2), (0.4, 0.9, 0.3),
     (0.6, 0.95, 0.4), (0.15, 0.55, 0.25), (0.3, 0.75, 0.15), (0.5, 0.85, 0.5)],
]

POWERUP_TYPES = ['wide', 'multi', 'slow', 'life']
POWERUP_COLORS = {
    'wide':  (0.2, 1.0, 0.5),
    'multi': (1.0, 0.5, 0.2),
    'slow':  (0.4, 0.7, 1.0),
    'life':  (1.0, 0.3, 0.5),
}
POWERUP_ICONS = {'wide': 'W', 'multi': 'M', 'slow': 'S', 'life': '♥'}


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'r', 'g', 'b', 'life', 'max_life', 'size', 'kind')
    def __init__(self, x, y, r, g, b, kind='spark'):
        self.x, self.y = x, y
        self.kind = kind
        if kind == 'spark':
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 7)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.life = random.uniform(0.3, 0.8)
            self.size = random.uniform(2, 5)
        elif kind == 'trail':
            self.vx = random.uniform(-0.3, 0.3)
            self.vy = random.uniform(-0.5, 0.5)
            self.life = random.uniform(0.15, 0.35)
            self.size = random.uniform(3, 6)
        elif kind == 'shockwave':
            self.vx = 0
            self.vy = 0
            self.life = 0.4
            self.size = 5
        self.r, self.g, self.b = r, g, b
        self.max_life = self.life


class Ball:
    __slots__ = ('x', 'y', 'vx', 'vy', 'r', 'active')
    def __init__(self, x, y, vx, vy, r=8):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.r = r
        self.active = True


class BrickBreaker(scene.Scene):

    def setup(self):
        W, H = self.size.w, self.size.h
        self.level = 1
        self.score = 0
        self.lives = 3
        self.combo = 0
        self.max_combo = 0
        self.game_over = False
        self.frame_count = 0

        self.paddle_base_w = W * 0.22
        self.paddle_w = self.paddle_base_w
        self.paddle_h = 14
        self.paddle_x = W / 2
        self.paddle_y = H * 0.06
        self.wide_timer = 0
        self.slow_timer = 0
        self.screen_shake = 0
        self.shake_x = 0
        self.shake_y = 0

        self.balls = [Ball(W / 2, H * 0.15, *self._rand_launch_vel())]
        self.bricks = []
        self.particles = []
        self.powerups = []
        self.floats = []
        self.stars = self._make_stars(80)

        self._build_level()

    def _rand_launch_vel(self):
        ang = random.uniform(math.pi * 0.3, math.pi * 0.7)
        spd = 4.5
        if self.slow_timer > 0:
            spd *= 0.6
        return math.cos(ang) * spd, math.sin(ang) * spd

    def _make_stars(self, n):
        W, H = self.size.w, self.size.h
        return [{'x': random.uniform(0, W), 'y': random.uniform(0, H),
                 'br': random.uniform(0.15, 0.7), 'sp': random.uniform(0.08, 0.4),
                 'sz': random.uniform(1, 2.5), 'phase': random.uniform(0, 6.28)} for _ in range(n)]

    def _build_level(self):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        cols, rows = 7, 5 + min(self.level, 3)
        margin = 6
        top_start = H - insets.top - 80
        area_w = W - margin * 2
        bw = (area_w - margin * (cols - 1)) / cols
        bh = 20
        palette = LEVEL_PALETTES[(self.level - 1) % len(LEVEL_PALETTES)]
        self.bricks = []
        self.brick_w = bw
        self.brick_h = bh
        for row in range(rows):
            color = palette[row % len(palette)]
            for col in range(cols):
                bx = margin + col * (bw + margin)
                by = top_start - row * (bh + margin)
                hp = 3 if row == 0 else (2 if row < 3 else 1)
                self.bricks.append({'x': bx, 'y': by, 'color': color, 'hp': hp,
                                    'max_hp': hp, 'alive': True, 'shake': 0})

    # ─── Touch ───
    def touch_began(self, touch):
        if self.game_over:
            self.setup()
            return
        self._move_paddle(touch)

    def touch_moved(self, touch):
        if not self.game_over:
            self._move_paddle(touch)

    def touch_ended(self, touch):
        pass

    def _move_paddle(self, touch):
        x, _ = touch.location
        half = self.paddle_w / 2
        self.paddle_x = max(half, min(self.size.w - half, x))

    # ─── Update ───
    def update(self):
        if self.game_over:
            self.frame_count += 1
            self._update_particles()
            return
        self.frame_count += 1
        W, H = self.size.w, self.size.h

        if self.wide_timer > 0:
            self.wide_timer -= 1
            if self.wide_timer == 0:
                self.paddle_w = self.paddle_base_w
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer == 0:
                for b in self.balls:
                    spd = math.hypot(b.vx, b.vy)
                    if spd > 0:
                        factor = 4.5 / (spd if spd > 0 else 1)
                        b.vx *= factor
                        b.vy *= factor

        if self.screen_shake > 0:
            self.screen_shake -= 1
            self.shake_x = random.uniform(-3, 3) * (self.screen_shake / 8)
            self.shake_y = random.uniform(-3, 3) * (self.screen_shake / 8)
        else:
            self.shake_x = self.shake_y = 0

        for s in self.stars:
            s['y'] -= s['sp']
            if s['y'] < 0:
                s['y'] = H
                s['x'] = random.uniform(0, W)

        pl = self.paddle_x - self.paddle_w / 2
        pr = self.paddle_x + self.paddle_w / 2
        pt = self.paddle_y + self.paddle_h

        for ball in self.balls:
            if not ball.active:
                continue

            if self.frame_count % 2 == 0:
                self.particles.append(Particle(ball.x, ball.y, 1.0, 0.85, 0.3, 'trail'))

            ball.x += ball.vx
            ball.y += ball.vy
            bx, by, br = ball.x, ball.y, ball.r

            if bx - br <= 0:
                bx = br; ball.vx = abs(ball.vx)
            elif bx + br >= W:
                bx = W - br; ball.vx = -abs(ball.vx)
            if by + br >= H:
                by = H - br; ball.vy = -abs(ball.vy)

            if by - br < 0:
                ball.active = False
                for _ in range(12):
                    self.particles.append(Particle(bx, 10, 1, 0.4, 0.2, 'spark'))
                continue

            if (pl - br <= bx <= pr + br
                    and self.paddle_y <= by - br <= pt
                    and ball.vy < 0):
                ball.vy = abs(ball.vy)
                offset = (bx - self.paddle_x) / (self.paddle_w / 2 + 0.01)
                ball.vx += offset * 2.0
                spd = math.hypot(ball.vx, ball.vy)
                target = 3.0 if self.slow_timer > 0 else 4.5 + min(self.level * 0.3, 2.0)
                if spd > 0:
                    ball.vx = ball.vx / spd * target
                    ball.vy = ball.vy / spd * target
                self.combo = 0
                for _ in range(4):
                    self.particles.append(Particle(bx, pt + 2, 0.4, 0.8, 1.0, 'spark'))

            for brick in self.bricks:
                if not brick['alive']:
                    continue
                bk_l, bk_b = brick['x'], brick['y']
                bk_r = bk_l + self.brick_w
                bk_t = bk_b + self.brick_h

                cx = max(bk_l, min(bx, bk_r))
                cy = max(bk_b, min(by, bk_t))
                dx, dy = bx - cx, by - cy
                if dx * dx + dy * dy < br * br:
                    brick['hp'] -= 1
                    brick['shake'] = 4
                    if brick['hp'] <= 0:
                        brick['alive'] = False
                        self.combo += 1
                        if self.combo > self.max_combo:
                            self.max_combo = self.combo
                        pts = 10 * self.combo * self.level
                        self.score += pts
                        c = brick['color']
                        for _ in range(10):
                            self.particles.append(Particle(
                                bk_l + self.brick_w / 2, bk_b + self.brick_h / 2,
                                c[0], c[1], c[2], 'spark'))
                        self.particles.append(Particle(
                            bk_l + self.brick_w / 2, bk_b + self.brick_h / 2,
                            c[0], c[1], c[2], 'shockwave'))
                        self.screen_shake = 6

                        self.floats.append({
                            'x': bk_l + self.brick_w / 2, 'y': bk_t + 5,
                            'text': f'+{pts}', 'life': 1.0,
                            'color': c
                        })

                        if random.random() < 0.12:
                            ptype = random.choice(POWERUP_TYPES)
                            self.powerups.append({
                                'x': bk_l + self.brick_w / 2, 'y': bk_b,
                                'vy': -1.8, 'type': ptype, 'angle': 0
                            })
                    else:
                        for _ in range(3):
                            self.particles.append(Particle(cx, cy, 1, 1, 1, 'spark'))

                    if abs(dx) > abs(dy):
                        ball.vx = -ball.vx
                    else:
                        ball.vy = -ball.vy
                    break

            ball.x, ball.y = bx, by

        active_balls = [b for b in self.balls if b.active]
        if not active_balls:
            self.lives -= 1
            self.combo = 0
            if self.lives <= 0:
                self.game_over = True
                self.screen_shake = 15
            else:
                self.balls = [Ball(W / 2, H * 0.15, *self._rand_launch_vel())]

        for pw in self.powerups:
            pw['y'] += pw['vy']
            pw['angle'] = (pw.get('angle', 0) + 4) % 360
            if pl <= pw['x'] <= pr and self.paddle_y <= pw['y'] <= pt:
                self._activate_powerup(pw['type'])
                pw['y'] = -200
        self.powerups = [p for p in self.powerups if p['y'] > -100]

        for f in self.floats:
            f['y'] += 0.8
            f['life'] -= 1.0 / 60.0
        self.floats = [f for f in self.floats if f['life'] > 0]

        self._update_particles()

        for b in self.bricks:
            if b['shake'] > 0:
                b['shake'] -= 1

        if all(not b['alive'] for b in self.bricks):
            self.score += 200 * self.level
            self.level += 1
            self._build_level()
            self.balls = [Ball(W / 2, H * 0.15, *self._rand_launch_vel())]

    def _activate_powerup(self, ptype):
        W = self.size.w
        if ptype == 'wide':
            self.paddle_w = min(W * 0.42, self.paddle_base_w * 1.6)
            self.wide_timer = 360
        elif ptype == 'multi':
            new_balls = []
            for b in self.balls:
                if b.active:
                    for _ in range(2):
                        ang = random.uniform(-0.5, 0.5)
                        cos_a, sin_a = math.cos(ang), math.sin(ang)
                        nvx = b.vx * cos_a - b.vy * sin_a
                        nvy = b.vx * sin_a + b.vy * cos_a
                        new_balls.append(Ball(b.x, b.y, nvx, nvy, b.r))
            self.balls.extend(new_balls)
        elif ptype == 'slow':
            self.slow_timer = 300
            for b in self.balls:
                b.vx *= 0.6
                b.vy *= 0.6
        elif ptype == 'life':
            self.lives = min(self.lives + 1, 5)

    def _update_particles(self):
        dt = 1.0 / 60.0
        for p in self.particles:
            if p.kind == 'shockwave':
                p.size += 12
            else:
                p.x += p.vx
                p.y += p.vy
                if p.kind == 'spark':
                    p.vy -= 6 * dt
            p.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]

    # ─── Draw ───
    def draw(self):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        fc = self.frame_count

        scene.background(0.01, 0.01, 0.04)

        scene.push_matrix()
        scene.translate(self.shake_x, self.shake_y)

        # 星空
        for s in self.stars:
            pulse = 0.5 + 0.5 * math.sin(fc * 0.015 + s['phase'])
            scene.fill(1, 1, 1, s['br'] * pulse)
            scene.rect(s['x'], s['y'], s['sz'], s['sz'])

        # 网格线
        scene.stroke(0.08, 0.08, 0.18, 0.2)
        scene.stroke_weight(1)
        sp = 50
        offset = (fc * 0.3) % sp
        for gx_i in range(int(W / sp) + 2):
            x = gx_i * sp - offset
            scene.line(x, 0, x, H)
        for gy_i in range(int(H / sp) + 2):
            y = gy_i * sp - offset
            scene.line(0, y, W, y)
        scene.no_stroke()

        # 砖块
        for brick in self.bricks:
            if not brick['alive']:
                continue
            r, g, b = brick['color']
            bx, by = brick['x'], brick['y']
            bw, bh = self.brick_w, self.brick_h

            shk = 0
            if brick['shake'] > 0:
                shk = random.uniform(-1.5, 1.5)

            hp_ratio = brick['hp'] / brick['max_hp']
            alpha = 0.5 + 0.5 * hp_ratio

            scene.fill(r * 0.3, g * 0.3, b * 0.3, alpha * 0.4)
            scene.rect(bx + 2, by - 2, bw, bh, 5)

            scene.fill(r, g, b, alpha)
            scene.rect(bx + shk, by, bw, bh, 5)

            scene.fill(1, 1, 1, 0.15 + 0.1 * hp_ratio)
            scene.rect(bx + shk + 3, by + bh - 5, bw - 6, 3, 2)

            if brick['hp'] >= 3:
                scene.stroke(1, 1, 1, 0.4)
                scene.stroke_weight(1.5)
                scene.no_fill()
                scene.rect(bx + shk, by, bw, bh, 5)
                scene.no_stroke()
            elif brick['hp'] >= 2:
                scene.stroke(r, g, b, 0.5)
                scene.stroke_weight(1)
                scene.no_fill()
                scene.rect(bx + shk, by, bw, bh, 5)
                scene.no_stroke()

        # 道具
        for pw in self.powerups:
            pc = POWERUP_COLORS.get(pw['type'], (1, 1, 1))
            icon = POWERUP_ICONS.get(pw['type'], '?')
            scene.push_matrix()
            scene.translate(pw['x'], pw['y'])

            glow_pulse = 0.6 + 0.4 * math.sin(fc * 0.1)
            scene.fill(pc[0], pc[1], pc[2], 0.2 * glow_pulse)
            scene.ellipse(-14, -14, 28, 28)

            scene.fill(pc[0], pc[1], pc[2], 0.9)
            scene.ellipse(-10, -10, 20, 20)
            scene.fill(1, 1, 1, 0.3)
            scene.ellipse(-6, 2, 8, 8)
            scene.tint(1, 1, 1)
            scene.text(icon, 'Arial-BoldMT', 13, 0, -1)
            scene.pop_matrix()

        # 挡板
        pl = self.paddle_x - self.paddle_w / 2
        # 地面光晕
        scene.fill(0.2, 0.5, 1.0, 0.06)
        scene.ellipse(pl - 20, self.paddle_y - 15, self.paddle_w + 40, self.paddle_h + 30)
        # 挡板主体
        if self.wide_timer > 0:
            pr_c = (0.1, 0.95, 0.5)
        elif self.slow_timer > 0:
            pr_c = (0.4, 0.7, 1.0)
        else:
            pr_c = (0.15, 0.55, 1.0)
        scene.fill(*pr_c)
        scene.rect(pl, self.paddle_y, self.paddle_w, self.paddle_h, 7)
        # 顶部高光
        scene.fill(pr_c[0] + 0.3, pr_c[1] + 0.2, min(1, pr_c[2] + 0.2), 0.5)
        scene.rect(pl + 4, self.paddle_y + self.paddle_h - 4, self.paddle_w - 8, 3, 2)
        # 底部反光
        scene.fill(1, 1, 1, 0.08)
        scene.rect(pl + 2, self.paddle_y, self.paddle_w - 4, 3, 2)

        # 球
        for ball in self.balls:
            if not ball.active:
                continue
            bx, by, br = ball.x, ball.y, ball.r
            # 拖尾
            for i in range(6):
                t = (6 - i) / 6.0
                tx = bx - ball.vx * i * 0.6
                ty = by - ball.vy * i * 0.6
                scene.fill(1.0, 0.75, 0.2, t * 0.25)
                sz = br * 2 * t
                scene.ellipse(tx - sz / 2, ty - sz / 2, sz, sz)
            # 光晕
            scene.fill(1.0, 0.9, 0.3, 0.12)
            scene.ellipse(bx - br * 2, by - br * 2, br * 4, br * 4)
            # 主体
            scene.fill(1.0, 0.9, 0.3)
            scene.ellipse(bx - br, by - br, br * 2, br * 2)
            # 高光
            scene.fill(1, 1, 0.85, 0.85)
            scene.ellipse(bx - br * 0.35, by + br * 0.2, br * 0.7, br * 0.7)

        # 冲击波粒子（在球之后画，层级高）
        for p in self.particles:
            if p.kind == 'shockwave':
                alpha = (p.life / p.max_life) * 0.3
                scene.stroke(p.r, p.g, p.b, alpha)
                scene.stroke_weight(2)
                scene.no_fill()
                scene.ellipse(p.x - p.size / 2, p.y - p.size / 2, p.size, p.size)
                scene.no_stroke()

        # 普通粒子
        for p in self.particles:
            if p.kind == 'shockwave':
                continue
            alpha = p.life / p.max_life
            scene.fill(p.r, p.g, p.b, alpha * (0.8 if p.kind == 'spark' else 0.4))
            sz = p.size * (alpha if p.kind == 'spark' else 1.0)
            scene.ellipse(p.x - sz / 2, p.y - sz / 2, sz, sz)

        # 飘字
        for f in self.floats:
            a = max(0, f['life'])
            c = f['color']
            scene.tint(c[0], c[1], c[2], a)
            scene.text(f['text'], 'Arial-BoldMT', 16, f['x'], f['y'])
        scene.no_tint()

        # 底部能量线
        scene.stroke(pr_c[0], pr_c[1], pr_c[2], 0.35)
        scene.stroke_weight(1.5)
        scene.line(0, self.paddle_y - 8, W, self.paddle_y - 8)
        scene.no_stroke()
        # 能量线上的脉冲光点
        pulse_x = (fc * 3) % int(W)
        scene.fill(pr_c[0], pr_c[1], pr_c[2], 0.5)
        scene.ellipse(pulse_x - 8, self.paddle_y - 12, 16, 8)

        scene.pop_matrix()

        # ─── HUD（safe area 适配）───
        hud_top = H - insets.top
        hud_h = 48
        scene.fill(0.02, 0.02, 0.06, 0.75)
        scene.rect(0, hud_top - hud_h, W, hud_h + insets.top, 0)
        # 底部分割线
        scene.stroke(0.3, 0.5, 1.0, 0.3)
        scene.stroke_weight(1)
        scene.line(0, hud_top - hud_h, W, hud_top - hud_h)
        scene.no_stroke()

        cy = hud_top - hud_h / 2

        # 关卡
        scene.tint(0.6, 0.8, 1.0)
        scene.text(f'LV.{self.level}', 'Arial-BoldMT', 15, 30, cy + 10)

        # 分数
        scene.tint(1, 1, 1)
        scene.text(f'{self.score}', 'Arial-BoldMT', 22, W * 0.5, cy + 2)
        scene.tint(0.6, 0.6, 0.7)
        scene.text('分数', 'Arial', 10, W * 0.5, cy + 17)

        # 连击
        if self.combo > 1:
            combo_alpha = 0.7 + 0.3 * math.sin(fc * 0.15)
            scene.tint(1.0, 0.8, 0.2, combo_alpha)
            scene.text(f'x{self.combo}', 'Arial-BoldMT', 18, W * 0.5, cy - 14)

        # 生命
        for i in range(self.lives):
            hx = W - 25 - i * 18
            hy = cy - 2
            scene.fill(1, 0.25, 0.4, 0.9)
            scene.ellipse(hx - 5, hy - 5, 10, 10)
            scene.fill(1, 0.6, 0.7, 0.5)
            scene.ellipse(hx - 3, hy, 4, 4)

        # 道具计时条
        bar_y = hud_top - hud_h - 6
        if self.wide_timer > 0:
            ratio = self.wide_timer / 360.0
            scene.fill(0.2, 1.0, 0.5, 0.6)
            scene.rect(0, bar_y, W * ratio, 4, 2)
        if self.slow_timer > 0:
            ratio = self.slow_timer / 300.0
            scene.fill(0.4, 0.7, 1.0, 0.6)
            scene.rect(0, bar_y - 5, W * ratio, 4, 2)

        scene.no_tint()

        # ─── 游戏结束 ───
        if self.game_over:
            overlay_alpha = min(1.0, (fc - self.frame_count + 60) / 60.0) * 0.8
            scene.fill(0, 0, 0, 0.8)
            scene.rect(0, 0, W, H)

            mid = H / 2

            # 装饰线条
            scene.stroke(1, 0.3, 0.4, 0.3)
            scene.stroke_weight(1)
            scene.line(W * 0.1, mid + 95, W * 0.9, mid + 95)
            scene.line(W * 0.1, mid - 80, W * 0.9, mid - 80)
            scene.no_stroke()

            pulse = 1.0 + 0.04 * math.sin(fc * 0.06)
            scene.push_matrix()
            scene.translate(W / 2, mid + 65)
            scene.scale(pulse, pulse)
            scene.tint(1, 0.3, 0.35)
            scene.text('游戏结束', 'Arial-BoldMT', 40, 0, 0)
            scene.pop_matrix()

            scene.tint(1.0, 0.95, 0.7)
            scene.text(f'{self.score}', 'Arial-BoldMT', 48, W / 2, mid + 10)
            scene.tint(0.6, 0.6, 0.7)
            scene.text('最终分数', 'Arial', 14, W / 2, mid + 38)

            scene.tint(0.85, 0.85, 0.9)
            scene.text(f'关卡 {self.level}  |  最高连击 x{self.max_combo}', 'Arial', 16,
                       W / 2, mid - 20)

            blink = 0.4 + 0.6 * abs(math.sin(fc * 0.04))
            scene.tint(0.6, 0.7, 0.9, blink)
            scene.text('轻触屏幕再来一局', 'Arial', 18, W / 2, mid - 55)

            scene.no_tint()


if __name__ == '__main__':
    scene.run(BrickBreaker())
