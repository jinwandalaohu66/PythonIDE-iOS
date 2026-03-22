from scene import *
import random
import math


class StickBridgeCN(Scene):
    def setup(self):
        self._init_game()
        self._start_new_run()

    def _init_game(self):
        self.sky_color = (0.55, 0.82, 0.98)
        self.ocean_color_top = (0.20, 0.62, 0.86)
        self.ocean_color_mid = (0.12, 0.45, 0.74)
        self.ocean_color_deep = (0.07, 0.28, 0.50)
        self.pillar_color = (0.08, 0.08, 0.12)
        self.stick_color = (0.03, 0.03, 0.03)

        self.hero_skins = [
            (0.02, 0.02, 0.02),
            (0.12, 0.18, 0.40),
            (0.08, 0.34, 0.20),
            (0.36, 0.14, 0.12),
        ]
        self.skin_index = 0
        self.hero_color = self.hero_skins[self.skin_index]

        self.base_y = self.size.h * 0.2
        self.pillar_h = self.size.h * 0.3
        self.top_y = self.base_y + self.pillar_h

        self.start_left_x = self.size.w * 0.12
        self.start_left_w = self.size.w * 0.14

        self.left_x = self.start_left_x
        self.left_w = self.start_left_w
        self.right_x = 0.0
        self.right_w = 0.0

        self.state = 'ready'
        self.score = 0
        self.best_score = 0
        self.last_gain = 0

        self.success = False
        self.perfect = False

        self.grow_speed = self.size.h * 0.95
        self.rotate_speed = math.pi * 1.8
        self.walk_speed = self.size.w * 0.52
        self.fall_g = self.size.h * 2.4

        self.stick_len = self.size.h * 0.002
        self.stick_angle = math.pi / 2

        self.hero_h = self.size.h * 0.085
        self.hero_foot_offset = self.hero_h * 0.18

        self.hero_x = 0.0
        self.hero_y = 0.0
        self.hero_tilt = 0.0
        self.hero_vy = 0.0

        self.bridge_end_x = 0.0
        self.walk_target_x = 0.0

        self.camera_x = 0.0
        self.camera_target_x = 0.0

        self.dead_timer = 0.0
        self.gain_show_timer = 0.0
        self.hint_text = '按住蓄力，松手放桥'

        self.ui_top_inset = max(26, self.size.h * 0.035)

    def _generate_right_pillar(self):
        min_gap = self.size.w * 0.18
        max_gap = self.size.w * 0.45
        min_w = self.size.w * 0.08
        max_w = self.size.w * 0.18

        gap = random.uniform(min_gap, max_gap)
        w = random.uniform(min_w, max_w)
        x = self.left_x + self.left_w + gap
        return x, w

    def _prepare_round(self, first_round=False):
        if not first_round:
            self.left_x = self.right_x
            self.left_w = self.right_w

        self.right_x, self.right_w = self._generate_right_pillar()

        self.stick_len = self.size.h * 0.002
        self.stick_angle = math.pi / 2

        self.hero_x = self.left_x + self.left_w
        self.hero_y = self.top_y + self.hero_foot_offset
        self.hero_tilt = 0.0
        self.hero_vy = 0.0

        self.success = False
        self.perfect = False
        self.state = 'ready'
        self.hint_text = '按住蓄力，松手放桥'

    def _start_new_run(self):
        self.left_x = self.start_left_x
        self.left_w = self.start_left_w
        self.camera_x = 0.0
        self.camera_target_x = 0.0
        self.score = 0
        self.last_gain = 0
        self.gain_show_timer = 0.0
        self._prepare_round(first_round=True)

    def _on_dead_reset(self):
        if self.score > self.best_score:
            self.best_score = self.score

        self.skin_index = (self.skin_index + 1) % len(self.hero_skins)
        self.hero_color = self.hero_skins[self.skin_index]

        self._start_new_run()

    def touch_began(self, touch):
        if self.state == 'ready':
            self.state = 'growing'
            self.stick_len = self.size.h * 0.002
            self.hint_text = '正在蓄力...'

    def touch_ended(self, touch):
        if self.state == 'growing':
            self.state = 'rotating'
            self.hint_text = '放桥中...'

    def update(self):
        dt = min(self.dt, 1 / 30)

        self.camera_x += (self.camera_target_x - self.camera_x) * min(1.0, dt * 6.0)

        if self.gain_show_timer > 0:
            self.gain_show_timer -= dt
            if self.gain_show_timer < 0:
                self.gain_show_timer = 0

        if self.state == 'growing':
            self.stick_len += self.grow_speed * dt

        elif self.state == 'rotating':
            self.stick_angle -= self.rotate_speed * dt
            if self.stick_angle <= 0:
                self.stick_angle = 0
                self.bridge_end_x = self.left_x + self.left_w + self.stick_len

                self.success = self.right_x <= self.bridge_end_x <= (self.right_x + self.right_w)

                if self.success:
                    center = self.right_x + self.right_w * 0.5
                    perfect_range = max(self.size.w * 0.015, self.right_w * 0.1)
                    self.perfect = abs(self.bridge_end_x - center) <= perfect_range
                else:
                    self.perfect = False

                self.walk_target_x = self.bridge_end_x
                self.state = 'walking'
                self.hint_text = '前进中...'

        elif self.state == 'walking':
            self.hero_x += self.walk_speed * dt
            self.camera_target_x = max(0.0, self.hero_x - self.size.w * 0.35)

            if self.hero_x >= self.walk_target_x:
                self.hero_x = self.walk_target_x
                if self.success:
                    self.walk_target_x = self.right_x + self.right_w * 0.5
                    self.state = 'to_center'
                else:
                    self.state = 'falling'
                    self.hero_vy = 0.0
                    self.hint_text = '桥长不合适，掉落中...'

        elif self.state == 'to_center':
            self.hero_x += self.walk_speed * dt
            self.camera_target_x = max(0.0, self.hero_x - self.size.w * 0.35)

            if self.hero_x >= self.walk_target_x:
                self.hero_x = self.walk_target_x

                gain = 1
                if self.perfect:
                    gain += 2

                self.last_gain = gain
                self.score += gain
                self.gain_show_timer = 0.8

                if self.perfect:
                    self.hint_text = '完美落点！+3'
                else:
                    self.hint_text = '过桥成功！+1'

                self._prepare_round(first_round=False)

        elif self.state == 'falling':
            self.hero_vy -= self.fall_g * dt
            self.hero_y += self.hero_vy * dt
            self.hero_tilt -= 2.8 * dt
            self.camera_target_x = max(0.0, self.hero_x - self.size.w * 0.35)

            if self.hero_y < -self.size.h * 0.2:
                self.state = 'dead_pause'
                self.dead_timer = 0.55
                self.hint_text = '坠落失败，正在重置...'

        elif self.state == 'dead_pause':
            self.dead_timer -= dt
            if self.dead_timer <= 0:
                self._on_dead_reset()

    def _draw_hero(self):
        h = self.hero_h
        head_r = h * 0.12

        push_matrix()
        translate(self.hero_x, self.hero_y)
        rotate(self.hero_tilt)

        stroke(self.hero_color[0], self.hero_color[1], self.hero_color[2], 1)
        stroke_weight(self.size.w * 0.007)

        line(0, 0, 0, h * 0.45)
        line(0, h * 0.35, -h * 0.16, h * 0.22)
        line(0, h * 0.35, h * 0.16, h * 0.22)
        line(0, 0, -h * 0.14, -h * 0.18)
        line(0, 0, h * 0.14, -h * 0.18)

        no_stroke()
        fill(self.hero_color[0], self.hero_color[1], self.hero_color[2], 1)
        ellipse(-head_r, h * 0.45, head_r * 2, head_r * 2)

        pop_matrix()

    def _draw_world(self):
        background(self.sky_color[0], self.sky_color[1], self.sky_color[2])

        push_matrix()
        translate(-self.camera_x, 0)

        no_stroke()
        fill(self.ocean_color_deep[0], self.ocean_color_deep[1], self.ocean_color_deep[2], 1)
        rect(self.camera_x - self.size.w, 0, self.size.w * 4, self.base_y)

        fill(self.ocean_color_mid[0], self.ocean_color_mid[1], self.ocean_color_mid[2], 0.95)
        rect(self.camera_x - self.size.w, self.base_y * 0.35, self.size.w * 4, self.base_y * 0.65)

        fill(self.ocean_color_top[0], self.ocean_color_top[1], self.ocean_color_top[2], 0.9)
        rect(self.camera_x - self.size.w, self.base_y * 0.72, self.size.w * 4, self.base_y * 0.28)

        stroke(1, 1, 1, 0.32)
        stroke_weight(self.size.h * 0.0035)
        wave_step = self.size.w * 0.09
        start_x = self.camera_x - self.size.w
        end_x = self.camera_x + self.size.w * 3
        phase = self.t * 1.8
        x = start_x
        while x < end_x:
            y1 = self.base_y - self.size.h * 0.008 + math.sin(x * 0.03 + phase) * self.size.h * 0.003
            y2 = y1 + math.sin(x * 0.045 + phase * 1.2) * self.size.h * 0.0015
            line(x, y1, x + wave_step * 0.55, y2)
            x += wave_step

        no_stroke()
        fill(self.pillar_color[0], self.pillar_color[1], self.pillar_color[2], 1)
        rect(self.left_x, self.base_y, self.left_w, self.pillar_h)
        rect(self.right_x, self.base_y, self.right_w, self.pillar_h)

        base_x = self.left_x + self.left_w
        end_x = base_x + self.stick_len * math.cos(self.stick_angle)
        end_y = self.top_y + self.stick_len * math.sin(self.stick_angle)

        stroke(self.stick_color[0], self.stick_color[1], self.stick_color[2], 1)
        stroke_weight(self.size.w * 0.01)
        line(base_x, self.top_y, end_x, end_y)

        if self.state in ('ready', 'growing', 'rotating', 'walking', 'to_center'):
            center = self.right_x + self.right_w * 0.5
            mark_w = max(self.size.w * 0.01, self.right_w * 0.08)
            no_stroke()
            fill(1, 0.25, 0.25, 0.8)
            rect(center - mark_w * 0.5, self.top_y - self.size.h * 0.01, mark_w, self.size.h * 0.01)

        self._draw_hero()
        pop_matrix()

    def _draw_panel(self):
        panel_h = self.size.h * 0.12
        panel_y = self.size.h - self.ui_top_inset - panel_h - self.size.h * 0.09

        no_stroke()
        fill(0, 0, 0, 0.28)
        rect(0, panel_y, self.size.w, panel_h)

        fill(1, 1, 1, 1)
        text('当前分', x=self.size.w * 0.17, y=panel_y + panel_h * 0.65, font_size=self.size.h * 0.028, alignment=5)
        text(str(self.score), x=self.size.w * 0.17, y=panel_y + panel_h * 0.28, font_size=self.size.h * 0.048, alignment=5)

        text('最高分', x=self.size.w * 0.83, y=panel_y + panel_h * 0.65, font_size=self.size.h * 0.028, alignment=5)
        text(str(self.best_score), x=self.size.w * 0.83, y=panel_y + panel_h * 0.28, font_size=self.size.h * 0.048, alignment=5)

        fill(1, 1, 1, 0.95)
        hint_y = panel_y - self.size.h * 0.035
        text(self.hint_text, x=self.size.w * 0.5, y=hint_y, font_size=self.size.h * 0.03, alignment=5)

        if self.gain_show_timer > 0:
            alpha = min(1.0, self.gain_show_timer / 0.8)
            fill(1, 0.93, 0.2, alpha)
            text(f'+{self.last_gain}', x=self.size.w * 0.5, y=hint_y - self.size.h * 0.028, font_size=self.size.h * 0.024, alignment=5)

    def draw(self):
        self._draw_world()
        self._draw_panel()


run(StickBridgeCN(), PORTRAIT)