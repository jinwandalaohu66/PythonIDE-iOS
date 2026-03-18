"""霓虹俄罗斯方块 — 赛博朋克风格经典方块游戏"""
import scene
import random
import math

COLS = 10
ROWS = 20

SHAPES = {
    'I': [[(0,0),(1,0),(2,0),(3,0)], [(0,0),(0,1),(0,2),(0,3)]],
    'O': [[(0,0),(1,0),(0,1),(1,1)]],
    'T': [[(0,0),(1,0),(2,0),(1,1)], [(0,0),(0,1),(0,2),(1,1)],
           [(0,1),(1,1),(2,1),(1,0)], [(1,0),(1,1),(1,2),(0,1)]],
    'S': [[(1,0),(2,0),(0,1),(1,1)], [(0,0),(0,1),(1,1),(1,2)]],
    'Z': [[(0,0),(1,0),(1,1),(2,1)], [(1,0),(1,1),(0,1),(0,2)]],
    'J': [[(0,0),(0,1),(1,0),(2,0)], [(0,0),(1,0),(1,1),(1,2)],
           [(0,1),(1,1),(2,1),(2,0)], [(0,0),(0,1),(0,2),(1,2)]],
    'L': [[(0,0),(1,0),(2,0),(2,1)], [(1,0),(1,1),(1,2),(0,2)],
           [(0,0),(0,1),(1,1),(2,1)], [(0,0),(1,0),(0,1),(0,2)]],
}

COLORS = {
    'I': (0.0, 0.9, 1.0),
    'O': (1.0, 0.85, 0.1),
    'T': (0.7, 0.2, 1.0),
    'S': (0.2, 1.0, 0.4),
    'Z': (1.0, 0.2, 0.3),
    'J': (0.2, 0.4, 1.0),
    'L': (1.0, 0.55, 0.1),
}

PIECE_NAMES = list(SHAPES.keys())

SCORE_TABLE = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'r', 'g', 'b', 'life', 'max_life', 'sz')
    def __init__(self, x, y, r, g, b, spread=3.0):
        a = random.uniform(0, math.pi * 2)
        s = random.uniform(0.5, spread)
        self.x, self.y = x, y
        self.vx = math.cos(a) * s
        self.vy = math.sin(a) * s
        self.r, self.g, self.b = r, g, b
        self.life = random.uniform(0.3, 0.7)
        self.max_life = self.life
        self.sz = random.uniform(2, 5)


class NeonTetris(scene.Scene):

    def setup(self):
        self.high_score = getattr(self, 'high_score', 0)
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets

        safe_top = H - insets.top
        safe_bot = insets.bottom
        hud_h = 55
        ctrl_h = 80

        play_top = safe_top - hud_h
        play_bot = safe_bot + ctrl_h
        avail_h = play_top - play_bot
        avail_w = W - insets.left - insets.right

        self.cell = min(avail_h / ROWS, (avail_w * 0.72) / COLS)
        self.cell = int(self.cell)
        if self.cell < 12:
            self.cell = 12

        self.grid_w = COLS * self.cell
        self.grid_h = ROWS * self.cell
        self.grid_x = (W - self.grid_w) / 2
        self.grid_y = play_bot + (avail_h - self.grid_h) / 2

        self.board = [[None] * COLS for _ in range(ROWS)]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.paused = False
        self.particles = []
        self.floats = []

        self.flash_rows = []
        self.flash_timer = 0

        self.fall_timer = 0.0
        self.lock_timer = 0.0
        self.lock_delay = 0.5

        self.bag = []
        self.current = None
        self.cur_rot = 0
        self.cur_x = 0
        self.cur_y = 0
        self.next_piece = self._pick()
        self._spawn()

        self.touch_start = None
        self.touch_start_time = 0
        self.touch_moved_dist = 0
        self.move_repeat_timer = 0
        self.last_move_dir = 0

    def _pick(self):
        if not self.bag:
            self.bag = PIECE_NAMES[:]
            random.shuffle(self.bag)
        return self.bag.pop()

    def _get_cells(self, name=None, rot=None, ox=None, oy=None):
        name = name or self.current
        rot = rot if rot is not None else self.cur_rot
        ox = ox if ox is not None else self.cur_x
        oy = oy if oy is not None else self.cur_y
        pattern = SHAPES[name][rot % len(SHAPES[name])]
        return [(ox + c, oy + r) for c, r in pattern]

    def _valid(self, cells):
        for cx, cy in cells:
            if cx < 0 or cx >= COLS or cy < 0:
                return False
            if cy < ROWS and self.board[cy][cx] is not None:
                return False
        return True

    def _spawn(self):
        self.current = self.next_piece
        self.next_piece = self._pick()
        self.cur_rot = 0
        shape = SHAPES[self.current][0]
        min_c = min(c for c, r in shape)
        max_c = max(c for c, r in shape)
        self.cur_x = (COLS - (max_c - min_c + 1)) // 2 - min_c
        max_r = max(r for c, r in shape)
        self.cur_y = ROWS - 1 - max_r
        self.lock_timer = 0
        self.fall_timer = 0
        if not self._valid(self._get_cells()):
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score

    def _lock(self):
        cells = self._get_cells()
        color = COLORS[self.current]
        for cx, cy in cells:
            if 0 <= cy < ROWS:
                self.board[cy][cx] = color
        self._check_lines()
        self._spawn()

    def _check_lines(self):
        cleared = []
        for r in range(ROWS):
            if all(self.board[r][c] is not None for c in range(COLS)):
                cleared.append(r)

        if not cleared:
            return

        self.flash_rows = cleared[:]
        self.flash_timer = 0.25

        for r in cleared:
            cx = self.grid_x + self.grid_w / 2
            cy = self.grid_y + r * self.cell + self.cell / 2
            for i in range(COLS * 2):
                px = self.grid_x + random.uniform(0, self.grid_w)
                c = self.board[r][i % COLS] or (0.5, 0.8, 1.0)
                self.particles.append(Particle(px, cy, c[0], c[1], c[2], 4.0))

        for r in sorted(cleared, reverse=True):
            del self.board[r]
            self.board.append([None] * COLS)

        n = len(cleared)
        pts = SCORE_TABLE.get(n, 800) * self.level
        self.score += pts
        self.lines += n

        new_level = self.lines // 10 + 1
        if new_level != self.level:
            self.level = new_level

        self.floats.append({
            'x': self.grid_x + self.grid_w / 2,
            'y': self.grid_y + cleared[0] * self.cell,
            'text': f'+{pts}' + ('  TETRIS!' if n == 4 else ''),
            'life': 1.2,
        })

    def _fall_interval(self):
        return max(0.05, 0.8 - (self.level - 1) * 0.065)

    def _ghost_y(self):
        gy = self.cur_y
        while True:
            cells = self._get_cells(oy=gy - 1)
            if self._valid(cells):
                gy -= 1
            else:
                break
        return gy

    def _try_rotate(self):
        new_rot = (self.cur_rot + 1) % len(SHAPES[self.current])
        offsets = [(0, 0), (-1, 0), (1, 0), (0, 1), (-2, 0), (2, 0)]
        for dx, dy in offsets:
            cells = self._get_cells(rot=new_rot, ox=self.cur_x + dx, oy=self.cur_y + dy)
            if self._valid(cells):
                self.cur_rot = new_rot
                self.cur_x += dx
                self.cur_y += dy
                self.lock_timer = 0
                return True
        return False

    def _try_move(self, dx):
        cells = self._get_cells(ox=self.cur_x + dx)
        if self._valid(cells):
            self.cur_x += dx
            self.lock_timer = 0
            return True
        return False

    def _hard_drop(self):
        gy = self._ghost_y()
        drop_dist = self.cur_y - gy
        self.score += drop_dist * 2
        self.cur_y = gy

        cells = self._get_cells()
        color = COLORS[self.current]
        for cx, cy in cells:
            px = self.grid_x + cx * self.cell + self.cell / 2
            py = self.grid_y + cy * self.cell + self.cell / 2
            for _ in range(3):
                self.particles.append(Particle(px, py, color[0], color[1], color[2], 2.0))
        self._lock()

    # ── touch handling ──

    def touch_began(self, touch):
        tx, ty = touch.location.x, touch.location.y
        if self.game_over:
            self.setup()
            return
        self.touch_start = (tx, ty)
        self.touch_start_time = self.t
        self.touch_moved_dist = 0
        self.last_move_dir = 0
        self.move_repeat_timer = 0

    def touch_moved(self, touch):
        if self.game_over or self.touch_start is None:
            return
        tx, ty = touch.location.x, touch.location.y
        sx, sy = self.touch_start
        dx = tx - sx
        dy = ty - sy
        self.touch_moved_dist = max(self.touch_moved_dist, abs(dx), abs(dy))

        if dy < -self.cell * 2 and abs(dy) > abs(dx) * 1.5:
            self._hard_drop()
            self.touch_start = None
            return

        cell_moves = int(dx / self.cell)
        if cell_moves != self.last_move_dir:
            diff = cell_moves - self.last_move_dir
            direction = 1 if diff > 0 else -1
            for _ in range(abs(diff)):
                self._try_move(direction)
            self.last_move_dir = cell_moves

    def touch_ended(self, touch):
        if self.game_over or self.touch_start is None:
            self.touch_start = None
            return
        tx, ty = touch.location.x, touch.location.y
        sx, sy = self.touch_start
        elapsed = self.t - self.touch_start_time

        if self.touch_moved_dist < self.cell * 0.7 and elapsed < 0.3:
            W = self.size.w
            third = W / 3
            if tx < third:
                self._try_move(-1)
            elif tx > third * 2:
                self._try_move(1)
            else:
                self._try_rotate()

        self.touch_start = None

    # ── update ──

    def update(self):
        dt = self.dt
        if dt > 0.1:
            dt = 0.1

        self._upd_particles(dt)

        if self.flash_timer > 0:
            self.flash_timer -= dt
            return

        if self.game_over or self.paused:
            return

        self.fall_timer += dt
        interval = self._fall_interval()

        if self.fall_timer >= interval:
            self.fall_timer = 0
            cells_below = self._get_cells(oy=self.cur_y - 1)
            if self._valid(cells_below):
                self.cur_y -= 1
                self.lock_timer = 0
            else:
                self.lock_timer += interval
                if self.lock_timer >= self.lock_delay:
                    self._lock()
        else:
            cells_below = self._get_cells(oy=self.cur_y - 1)
            if not self._valid(cells_below):
                self.lock_timer += dt
                if self.lock_timer >= self.lock_delay:
                    self._lock()

    def _upd_particles(self, dt):
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vy -= 3.0 * dt
            p.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]
        for f in self.floats:
            f['y'] += 40 * dt
            f['life'] -= dt
        self.floats = [f for f in self.floats if f['life'] > 0]

    # ── draw ──

    def draw(self):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        t = self.t

        scene.background(0.03, 0.02, 0.07)

        self._draw_grid_bg()
        self._draw_board(t)
        self._draw_ghost()
        self._draw_current(t)
        self._draw_flash(t)
        self._draw_particles()
        self._draw_next(t)
        self._draw_hud(t)
        self._draw_controls()

        if self.game_over:
            self._draw_game_over(t)

    def _draw_grid_bg(self):
        gx, gy = self.grid_x, self.grid_y
        cs = self.cell

        scene.fill(0.05, 0.04, 0.10, 0.6)
        scene.rect(gx - 2, gy - 2, self.grid_w + 4, self.grid_h + 4, 4)

        scene.stroke(0.10, 0.08, 0.16, 0.5)
        scene.stroke_weight(0.5)
        for c in range(COLS + 1):
            scene.line(gx + c * cs, gy, gx + c * cs, gy + self.grid_h)
        for r in range(ROWS + 1):
            scene.line(gx, gy + r * cs, gx + self.grid_w, gy + r * cs)
        scene.no_stroke()

        scene.stroke(0.15, 0.10, 0.25, 0.6)
        scene.stroke_weight(1.5)
        scene.no_fill()
        scene.rect(gx - 2, gy - 2, self.grid_w + 4, self.grid_h + 4, 4)
        scene.no_stroke()

    def _draw_block(self, px, py, cs, color, glow=False, alpha=1.0):
        r, g, b = color
        if glow:
            scene.fill(r, g, b, 0.08 * alpha)
            scene.ellipse(px - cs * 0.3, py - cs * 0.3, cs * 1.6, cs * 1.6)
        scene.fill(r * 0.15, g * 0.15, b * 0.15, 0.4 * alpha)
        scene.rect(px + 1, py - 1, cs - 2, cs - 2, 3)
        scene.fill(r, g, b, alpha)
        scene.rect(px + 1, py + 1, cs - 2, cs - 2, 3)
        scene.fill(r + (1 - r) * 0.3, g + (1 - g) * 0.3, b + (1 - b) * 0.3, 0.35 * alpha)
        scene.rect(px + 3, py + cs - 5, cs - 6, 2, 1)

    def _draw_board(self, t):
        gx, gy = self.grid_x, self.grid_y
        cs = self.cell
        for r in range(ROWS):
            for c in range(COLS):
                color = self.board[r][c]
                if color is None:
                    continue
                px = gx + c * cs
                py = gy + r * cs
                self._draw_block(px, py, cs, color)

    def _draw_ghost(self):
        if self.current is None or self.game_over:
            return
        gy_pos = self._ghost_y()
        if gy_pos == self.cur_y:
            return
        cells = self._get_cells(oy=gy_pos)
        color = COLORS[self.current]
        gx, gy = self.grid_x, self.grid_y
        cs = self.cell
        for cx, cy in cells:
            if cy >= ROWS:
                continue
            px = gx + cx * cs
            py = gy + cy * cs
            scene.stroke(color[0], color[1], color[2], 0.25)
            scene.stroke_weight(1)
            scene.no_fill()
            scene.rect(px + 2, py + 2, cs - 4, cs - 4, 3)
            scene.no_stroke()

    def _draw_current(self, t):
        if self.current is None or self.game_over:
            return
        cells = self._get_cells()
        color = COLORS[self.current]
        gx, gy = self.grid_x, self.grid_y
        cs = self.cell
        pulse = 0.85 + 0.15 * math.sin(t * 6)
        for cx, cy in cells:
            if cy >= ROWS:
                continue
            px = gx + cx * cs
            py = gy + cy * cs
            self._draw_block(px, py, cs, color, glow=True, alpha=pulse)

    def _draw_flash(self, t):
        if not self.flash_rows or self.flash_timer <= 0:
            return
        gx, gy = self.grid_x, self.grid_y
        cs = self.cell
        flash_alpha = 0.5 + 0.5 * math.sin(t * 30)
        for r in self.flash_rows:
            scene.fill(1, 1, 1, flash_alpha * 0.6)
            scene.rect(gx, gy + r * cs, self.grid_w, cs)

    def _draw_particles(self):
        for p in self.particles:
            a = max(0, p.life / p.max_life)
            sz = p.sz * a
            scene.fill(p.r, p.g, p.b, a * 0.8)
            scene.ellipse(p.x - sz / 2, p.y - sz / 2, sz, sz)
        for f in self.floats:
            a = min(1.0, f['life'])
            scene.tint(1, 0.95, 0.6, a)
            scene.text(f['text'], 'Arial-BoldMT', 16, f['x'], f['y'])
        scene.no_tint()

    def _draw_next(self, t):
        W = self.size.w
        gx = self.grid_x
        cs = self.cell
        box_x = gx + self.grid_w + 10
        avail = W - box_x - self.safe_area_insets.right - 5
        if avail < cs * 3:
            box_x = gx - cs * 4.5 - 10
            if box_x < self.safe_area_insets.left + 5:
                box_x = self.safe_area_insets.left + 5

        box_y = self.grid_y + self.grid_h - cs * 6

        scene.fill(0.06, 0.04, 0.12, 0.7)
        scene.rect(box_x - 5, box_y - 5, cs * 4.5 + 10, cs * 5.5 + 10, 6)

        scene.tint(0.5, 0.45, 0.6, 0.7)
        scene.text('NEXT', 'Arial-BoldMT', 12, box_x + cs * 2.25, box_y + cs * 5.2)
        scene.no_tint()

        shape = SHAPES[self.next_piece][0]
        color = COLORS[self.next_piece]
        min_c = min(c for c, r in shape)
        max_c = max(c for c, r in shape)
        min_r = min(r for c, r in shape)
        max_r = max(r for c, r in shape)
        pw = (max_c - min_c + 1) * cs
        ph = (max_r - min_r + 1) * cs
        ox = box_x + (cs * 4.5 - pw) / 2
        oy = box_y + (cs * 4.5 - ph) / 2

        pulse = 0.8 + 0.2 * math.sin(t * 3)
        for c, r in shape:
            px = ox + (c - min_c) * cs
            py = oy + (r - min_r) * cs
            self._draw_block(px, py, cs, color, alpha=pulse)

    def _draw_hud(self, t):
        W, H = self.size.w, self.size.h
        insets = self.safe_area_insets
        hud_h = 55
        hud_top = H - insets.top
        hud_y = hud_top - hud_h

        scene.fill(0.04, 0.03, 0.09, 0.9)
        scene.rect(0, hud_y, W, hud_h + insets.top)

        cy = hud_y + hud_h / 2

        scene.tint(0.0, 0.85, 1.0, 0.8)
        scene.text(f'Lv.{self.level}', 'Arial-BoldMT', 14, insets.left + 30, cy + 12)
        scene.no_tint()
        scene.tint(0.5, 0.5, 0.6)
        scene.text(f'Lines: {self.lines}', 'Arial', 12, insets.left + 30, cy - 6)
        scene.no_tint()

        scene.tint(1, 1, 1)
        scene.text(f'{self.score}', 'Arial-BoldMT', 24, W / 2, cy + 2)
        scene.no_tint()
        scene.tint(0.5, 0.5, 0.6)
        scene.text('SCORE', 'Arial', 10, W / 2, cy + 20)
        scene.no_tint()

        if self.high_score > 0:
            scene.tint(0.8, 0.7, 0.3, 0.7)
            scene.text(f'Best: {self.high_score}', 'Arial', 12, W - insets.right - 50, cy + 2)
            scene.no_tint()

    def _draw_controls(self):
        W = self.size.w
        insets = self.safe_area_insets
        cy = insets.bottom + 35

        scene.fill(0.04, 0.03, 0.09, 0.5)
        scene.rect(0, 0, W, insets.bottom + 70)

        scene.tint(0.4, 0.35, 0.5, 0.45)
        third = W / 3
        scene.text('◀ Move', 'Arial', 12, third / 2, cy)
        scene.text('Rotate', 'Arial', 12, W / 2, cy)
        scene.text('Move ▶', 'Arial', 12, W - third / 2, cy)

        scene.tint(0.3, 0.3, 0.4, 0.3)
        scene.text('↓ Swipe down to drop', 'Arial', 10, W / 2, cy - 18)
        scene.no_tint()

        scene.stroke(0.15, 0.12, 0.22, 0.3)
        scene.stroke_weight(1)
        scene.line(third, insets.bottom + 8, third, insets.bottom + 62)
        scene.line(third * 2, insets.bottom + 8, third * 2, insets.bottom + 62)
        scene.no_stroke()

    def _draw_game_over(self, t):
        W, H = self.size.w, self.size.h
        scene.fill(0, 0, 0, 0.85)
        scene.rect(0, 0, W, H)

        pulse = 1.0 + 0.03 * math.sin(t * 4)
        scene.push_matrix()
        scene.translate(W / 2, H / 2 + 80)
        scene.rotate(math.sin(t * 2) * 1.5)
        scene.tint(1.0, 0.2, 0.3)
        scene.text('GAME OVER', 'Arial-BoldMT', 36, 0, 0)
        scene.pop_matrix()
        scene.no_tint()

        scene.tint(1, 0.95, 0.7)
        scene.text(f'{self.score}', 'Arial-BoldMT', 52, W / 2, H / 2 + 20)
        scene.no_tint()
        scene.tint(0.5, 0.5, 0.6)
        scene.text('FINAL SCORE', 'Arial', 13, W / 2, H / 2 + 50)
        scene.no_tint()

        scene.tint(0.7, 0.7, 0.8)
        scene.text(f'Level {self.level}  |  Lines {self.lines}', 'Arial', 15, W / 2, H / 2 - 15)
        scene.no_tint()

        if self.high_score > 0:
            scene.tint(0.85, 0.75, 0.3)
            scene.text(f'Best: {self.high_score}', 'Arial-BoldMT', 18, W / 2, H / 2 - 40)
            scene.no_tint()

        blink = 0.35 + 0.65 * abs(math.sin(t * 2.5))
        scene.tint(0.5, 0.7, 1.0, blink)
        scene.text('Tap to play again', 'Arial', 18, W / 2, H / 2 - 75)
        scene.no_tint()


if __name__ == '__main__':
    scene.run(NeonTetris())
