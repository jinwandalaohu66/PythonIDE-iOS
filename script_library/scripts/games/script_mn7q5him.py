# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～


from scene import *
import ui
import math
import random
import sound

BLOCK_H = 28
INIT_W_RATIO = 0.52
PERFECT_TOL = 4
MIN_W = 10
BASE_SPEED = 220
SPEED_INC = 10


def _hsv_hex(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:     r, g, b = c, x, 0
    elif h < 120:  r, g, b = x, c, 0
    elif h < 180:  r, g, b = 0, c, x
    elif h < 240:  r, g, b = 0, x, c
    elif h < 300:  r, g, b = x, 0, c
    else:          r, g, b = c, 0, x
    return '#{:02x}{:02x}{:02x}'.format(
        int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


class StackTower(Scene):

    # ━━ 初始化 ━━━━━━━━━━━━━━━━━━━━━━
    def setup(self):
        w, h = self.size.w, self.size.h
        self.background_color = '#0d0d1a'

        self.game_over = False
        self.score = 0
        self.combo = 0
        self.best_combo = 0
        self._paused_flag = False
        self._slow = False
        self._gl_y = 0.0
        
        # 音效初始化
        self._sound_effects = {
            'place': 'game:Click_1',          # 放置方块
            'perfect': 'game:Powerup',        # 完美放置
            'combo': 'arcade:Coin_1',         # 连击
            'fall': 'game:Error',             # 掉落
            'game_over': 'music:GameOver_NES_1',  # 游戏结束
            'restart': 'ui:click1',           # 重新开始
            'pause': 'ui:click2',             # 暂停
            'resume': 'ui:click3',            # 继续
            'slow_start': 'game:Powerup_2',   # 慢放开始
            'slow_end': 'game:Powerdown'      # 慢放结束
        }

        insets = self.safe_area_insets

        # ★ 游戏层 — 统一控制 Node.speed / Node.paused
        self.game_layer = Node(parent=self)

        # 基座
        bw = w * INIT_W_RATIO
        by = 80
        base = ShapeNode(
            path=ui.Path.rounded_rect(0, 0, bw, BLOCK_H, 5),
            fill_color=self._clr(0),
            stroke_color='clear',
            shadow=('#00000055', 0, -2, 5),
            position=(w / 2, by),
            parent=self.game_layer,
        )
        self.stack = [{'x': w / 2, 'w': bw, 'y': by}]

        # ── HUD（不受 game_layer.speed 影响）──
        self.score_lbl = LabelNode(
            '0', font=('Menlo-Bold', 44),
            position=(w / 2, h - insets.top - 48),
            z_position=20, parent=self, color='white',
        )
        self.combo_lbl = LabelNode(
            '', font=('Menlo-Bold', 16),
            position=(w / 2, h - insets.top - 78),
            z_position=20, parent=self, color='#FFD700',
        )
        self.combo_lbl.alpha = 0

        # ★ Node.paused — 暂停按钮
        self.pause_btn = LabelNode(
            '⏸', font=('Menlo', 26),
            position=(w - 36, h - insets.top - 48),
            z_position=25, parent=self,
        )

        # 慢放进度条
        sbar_w = 100
        sy = h - insets.top - 96
        self.sbar_bg = ShapeNode(
            path=ui.Path.rounded_rect(0, 0, sbar_w, 5, 2.5),
            fill_color='#333', stroke_color='clear',
            position=(w / 2, sy), z_position=20, parent=self,
        )
        self.sbar_bg.alpha = 0
        self.sbar = ShapeNode(
            path=ui.Path.rounded_rect(0, 0, sbar_w, 5, 2.5),
            fill_color='#00e5ff', stroke_color='clear',
            position=(w / 2, sy), z_position=21, parent=self,
        )
        self.sbar.alpha = 0
        self._sbar_w = sbar_w

        # 提示
        self.hint = LabelNode(
            '点击放置方块', font=('Helvetica-Bold', 22),
            position=(w / 2, h * 0.48),
            z_position=30, parent=self, color='#ffffff55',
        )
        self.hint.run_action(Action.repeat_forever(Action.sequence([
            Action.fade_to(0.15, 0.8, TIMING_EASE_IN_OUT),
            Action.fade_to(0.45, 0.8, TIMING_EASE_IN_OUT),
        ])), key='pulse')

        self.cur = None
        self._spawn()

    def _clr(self, i):
        return _hsv_hex((i * 20) % 360, 0.72, 0.92)
    
    def _play_sound(self, effect_name, volume=1.0, pitch=1.0):
        """播放音效"""
        if effect_name in self._sound_effects:
            try:
                sound.play_effect(self._sound_effects[effect_name], 
                                 volume=volume, pitch=pitch)
            except:
                pass  # 如果音效播放失败，静默处理

    # ━━ 生成下一个滑块 ━━━━━━━━━━━━━━
    def _spawn(self):
        last = self.stack[-1]
        y = last['y'] + BLOCK_H
        bw = last['w']
        w = self.size.w

        self._dir = 1 if len(self.stack) % 2 == 0 else -1
        start_x = -bw if self._dir == 1 else w + bw
        self._mspd = BASE_SPEED + len(self.stack) * SPEED_INC
        self._cy = y
        self._cw = bw

        # ★ ShapeNode shadow
        self.cur = ShapeNode(
            path=ui.Path.rounded_rect(0, 0, bw, BLOCK_H, 4),
            fill_color=self._clr(len(self.stack)),
            stroke_color='clear',
            shadow=('#00000055', 0, -2, 5),
            position=(start_x, y),
            parent=self.game_layer,
        )

    # ━━ 主循环 ━━━━━━━━━━━━━━━━━━━━━━
    def update(self, dt):
        if self.game_over or self._paused_flag:
            return
        if self.cur is None:
            return

        spd = self._mspd * (0.35 if self._slow else 1.0)

        # ★ Vector2 += 原地运算
        pos = Vector2(self.cur.position.x, self.cur.position.y)
        pos += Vector2(self._dir * spd * dt, 0)

        hw = self._cw / 2
        if pos.x - hw > self.size.w + 15:
            self._dir = -1
        elif pos.x + hw < -15:
            self._dir = 1

        self.cur.position = (pos.x, self._cy)

    # ★ did_evaluate_actions — 每帧动作后回调
    def did_evaluate_actions(self):
        pass

    # ━━ 触摸 ━━━━━━━━━━━━━━━━━━━━━━━━
    def touch_began(self, touch):
        if self.game_over:
            self._restart()
            return

        tx, ty = touch.location.x, touch.location.y
        bx, by = self.pause_btn.position.x, self.pause_btn.position.y
        if abs(tx - bx) < 30 and abs(ty - by) < 30:
            self._toggle_pause()
            return
        if self._paused_flag:
            return

        if self.hint and self.hint.parent:
            self.hint.run_action(Action.sequence(
                Action.fade_to(0, 0.15), Action.remove()))

        if self.cur is not None:
            self._place()

    def _toggle_pause(self):
        # ★ Node.paused
        self._paused_flag = not self._paused_flag
        self.game_layer.paused = self._paused_flag
        self.pause_btn.text = '▶️' if self._paused_flag else '⏸'

    # ━━ 放置方块 ━━━━━━━━━━━━━━━━━━━━
    def _place(self):
        cx = self.cur.position.x
        last = self.stack[-1]
        lx, lw = last['x'], last['w']
        bw = self._cw

        ol = max(cx - bw / 2, lx - lw / 2)
        or_ = min(cx + bw / 2, lx + lw / 2)
        ow = or_ - ol

        if ow <= MIN_W:
            self._end()
            return

        diff = abs(cx - lx)
        perfect = diff < PERFECT_TOL

        if perfect:
            ow = bw
            nx = lx
            self.combo += 1
            if self.combo > self.best_combo:
                self.best_combo = self.combo
            
            # 播放完美放置音效
            if self.combo >= 3:
                self._play_sound('combo', volume=1.0, pitch=0.9 + self.combo * 0.05)
            else:
                self._play_sound('perfect', volume=1.0, pitch=1.0)
                
            self._fx_perfect(nx, self._cy)
            if self.combo >= 3 and not self._slow:
                self._start_slow()
        else:
            self.combo = 0
            nx = (ol + or_) / 2
            cut_w = bw - ow
            if cx > lx:
                fx = or_ + cut_w / 2
            else:
                fx = ol - cut_w / 2
            
            # 播放掉落音效
            self._play_sound('fall', volume=0.8, pitch=0.9)
            self._fx_fall(fx, self._cy, cut_w)

        self.cur.remove_from_parent()
        self.cur = None

        # 播放放置方块音效
        self._play_sound('place', volume=0.7, pitch=1.0)

        placed = ShapeNode(
            path=ui.Path.rounded_rect(0, 0, ow, BLOCK_H, 4),
            fill_color=self._clr(len(self.stack)),
            stroke_color='clear',
            shadow=('#00000055', 0, -2, 5),
            position=(nx, self._cy),
            parent=self.game_layer,
        )

        # ★ Action.scale_x_to / scale_y_to — 弹性落地
        placed.run_action(Action.sequence([
            Action.group(
                Action.scale_x_to(1.08, 0.05),
                Action.scale_y_to(0.6, 0.05),
            ),
            Action.group(
                Action.scale_x_to(1.0, 0.2, TIMING_ELASTIC_OUT),
                Action.scale_y_to(1.0, 0.2, TIMING_ELASTIC_OUT),
            ),
        ]))

        self.stack.append({'x': nx, 'w': ow, 'y': self._cy})
        self.score += 1
        self.score_lbl.text = str(self.score)
        self.score_lbl.run_action(Action.sequence([
            Action.scale_to(1.3, 0.07),
            Action.scale_to(1.0, 0.15, TIMING_EASE_OUT),
        ]), key='bounce')

        if self.combo >= 2:
            self.combo_lbl.text = f'× {self.combo} COMBO'
            self.combo_lbl.run_action(Action.fade_to(1, 0.1))
        else:
            self.combo_lbl.run_action(Action.fade_to(0, 0.25))

        # 镜头跟随
        screen_y = self._cy + self._gl_y
        target = self.size.h * 0.35
        if screen_y > target:
            delta = screen_y - target
            self._gl_y -= delta
            self.game_layer.run_action(
                Action.move_to(0, self._gl_y, 0.25, TIMING_EASE_OUT),
                key='scroll')

        # ★ Node.speed — 随层数提速
        self.game_layer.speed = 1.0 + len(self.stack) * 0.012

        self._spawn()

    # ━━ 特效 ━━━━━━━━━━━━━━━━━━━━━━━━
    def _fx_fall(self, x, y, w):
        if w < 2:
            return
        p = ShapeNode(
            path=ui.Path.rounded_rect(0, 0, w, BLOCK_H, 3),
            fill_color=self._clr(len(self.stack)),
            stroke_color='clear',
            position=(x, y),
            parent=self.game_layer,
        )
        p.run_action(Action.sequence([
            Action.group(
                Action.move_by(0, -320, 0.85),
                Action.rotate_by(random.uniform(-2.5, 2.5), 0.85),
                Action.fade_to(0, 0.85),
            ),
            Action.remove(),
        ]))

    def _fx_perfect(self, x, y):
        txt = 'PERFECT!' if self.combo < 5 else f'PERFECT ×{self.combo}!'
        fs = 16 + min(self.combo, 6)
        lbl = LabelNode(
            txt, font=('Menlo-Bold', fs),
            position=(x, y + BLOCK_H + 5),
            z_position=30, parent=self.game_layer, color='#FFD700',
        )
        # ★ scale_x_to 文字弹出
        lbl.run_action(Action.sequence([
            Action.group(
                Action.scale_x_to(1.3, 0.12),
                Action.move_by(0, 28, 0.55),
                Action.fade_to(0, 0.55),
            ),
            Action.remove(),
        ]))
        ring = ShapeNode(
            path=ui.Path.rounded_rect(0, 0, self._cw + 10, BLOCK_H + 8, 6),
            fill_color='clear', stroke_color='#FFD700',
            line_width=2,
            position=(x, y),
            parent=self.game_layer,
        )
        ring.run_action(Action.sequence([
            Action.group(
                Action.scale_to(1.35, 0.3),
                Action.fade_to(0, 0.3),
            ),
            Action.remove(),
        ]))

    # ━━ 慢放 ━━━━━━━━━━━━━━━━━━━━━━━━
    def _start_slow(self):
        self._slow = True
        self.game_layer.speed = max(0.35, self.game_layer.speed * 0.35)

        # 播放慢放开始音效
        self._play_sound('slow_start', volume=1.0, pitch=0.8)

        self.sbar_bg.run_action(Action.fade_to(1, 0.12))
        self.sbar.run_action(Action.fade_to(1, 0.12))

        # ★ Action.call(fn, duration) — progress 回调驱动倒计时条
        def on_progress(node, progress):
            remaining = 1.0 - progress
            fw = max(1, self._sbar_w * remaining)
            self.sbar.set_path(ui.Path.rounded_rect(0, 0, fw, 5, 2.5))

        def end_slow():
            self._slow = False
            self.game_layer.speed = 1.0 + len(self.stack) * 0.012
            # 播放慢放结束音效
            self._play_sound('slow_end', volume=0.8, pitch=1.2)
            self.sbar_bg.run_action(Action.fade_to(0, 0.3))
            self.sbar.run_action(Action.fade_to(0, 0.3))

        self.run_action(Action.sequence([
            Action.call(on_progress, duration=3.0),
            Action.call(end_slow),
        ]), key='slow')

    # ━━ 结束 ━━━━━━━━━━━━━━━━━━━━━━━━
    def _end(self):
        self.game_over = True
        
        # 播放游戏结束音效
        self._play_sound('game_over', volume=1.0, pitch=0.9)
        
        if self.cur:
            self.cur.run_action(Action.sequence([
                Action.group(
                    Action.move_by(0, -400, 0.7),
                    Action.rotate_by(random.uniform(-3, 3), 0.7),
                    Action.fade_to(0, 0.7),
                ),
                Action.remove(),
            ]))
            self.cur = None

        w, h = self.size.w, self.size.h

        overlay = SpriteNode(
            color=(0, 0, 0, 0.55),
            size=(w, h),
            position=(w / 2, h / 2),
            z_position=50, parent=self,
        )
        overlay.alpha = 0
        overlay.run_action(Action.fade_to(1, 0.5))

        LabelNode(
            'GAME OVER', font=('Menlo-Bold', 38),
            position=(w / 2, h / 2 + 55),
            z_position=51, parent=self, color='#FF6B6B',
        )
        LabelNode(
            f'层数: {self.score}', font=('Menlo', 22),
            position=(w / 2, h / 2 + 8),
            z_position=51, parent=self, color='white',
        )
        if self.best_combo > 0:
            LabelNode(
                f'最佳连击: {self.best_combo}',
                font=('Menlo', 16),
                position=(w / 2, h / 2 - 22),
                z_position=51, parent=self, color='#FFD700',
            )
        LabelNode(
            '点击重来', font=('Helvetica', 18),
            position=(w / 2, h / 2 - 60),
            z_position=51, parent=self, color='#b2bec3',
        )

    # ━━ 重启 ━━━━━━━━━━━━━━━━━━━━━━━━
    def _restart(self):
        for n in list(self.children):
            n.remove_from_parent()
        self.stack = []
        self.game_over = False
        self._paused_flag = False
        self._slow = False
        self._gl_y = 0.0
        self.score = 0
        self.combo = 0
        self.setup()


# ★ show_fps + anti_alias
if __name__ == '__main__':
    run(StackTower(), show_fps=True, anti_alias=True)
