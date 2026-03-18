# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
# 2048 - 数字拼图
# A classic number puzzle game for Pythonista Scene module

import scene
import random
import copy
import math

# ── Color Palette ───────────────────────────────────────────────

TILE_CLR = {
    0:    (0.804, 0.757, 0.706),
    2:    (0.933, 0.894, 0.855),
    4:    (0.929, 0.878, 0.784),
    8:    (0.949, 0.694, 0.475),
    16:   (0.961, 0.584, 0.388),
    32:   (0.965, 0.486, 0.373),
    64:   (0.965, 0.369, 0.231),
    128:  (0.929, 0.812, 0.447),
    256:  (0.929, 0.800, 0.380),
    512:  (0.929, 0.784, 0.314),
    1024: (0.929, 0.773, 0.247),
    2048: (0.929, 0.761, 0.180),
    4096: (0.384, 0.298, 0.624),
    8192: (0.298, 0.451, 0.651),
}

DARK_TEXT  = (0.467, 0.431, 0.396)
LIGHT_TEXT = (0.976, 0.965, 0.949)
BOARD_BG   = (0.725, 0.675, 0.627)
PAGE_BG    = (0.980, 0.973, 0.937)
BUTTON_BG  = (0.557, 0.475, 0.396)

IDLE, SLIDING, SETTLING = 0, 1, 2


def tile_color(v):
    return TILE_CLR.get(v, (0.235, 0.224, 0.200))


def text_color(v):
    return DARK_TEXT if v <= 4 else LIGHT_TEXT


def font_size(v, ts):
    if v < 10:    return ts * 0.50
    if v < 100:   return ts * 0.43
    if v < 1000:  return ts * 0.35
    if v < 10000: return ts * 0.28
    return ts * 0.23


# ── Game Scene ──────────────────────────────────────────────────

class Game2048(scene.Scene):

    def setup(self):
        self.grid = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.best_score = 0
        self.prev_grid = None
        self.prev_score = None

        self.game_over = False
        self.won = False
        self.keep_playing = False
        self.phase = IDLE

        self.slides = []
        self.spawns = []
        self.merges = []
        self.pops = []

        self.slide_dur = 0.12
        self.spawn_dur = 0.15
        self.merge_dur = 0.15
        self.pop_dur = 0.70

        self.touch_start = None
        self.swipe_min = 30

        self._btn_new = (0, 0, 0, 0)
        self._btn_undo = (0, 0, 0, 0)
        self._cached_size = None

        self._spawn_tiles(2)

    # ── Layout ──────────────────────────────────────────────────

    def _calc_layout(self):
        w, h = self.size.w, self.size.h
        si = self.safe_area_insets
        st = getattr(si, 'top', 0) or 0
        sb = getattr(si, 'bottom', 0) or 0
        sl = getattr(si, 'left', 0) or 0
        sr = getattr(si, 'right', 0) or 0

        safe_w = w - sl - sr
        safe_h = h - st - sb
        header_h = 108
        margin = 14

        board = min(safe_w - margin * 2,
                    safe_h - header_h - margin * 2, 450)
        self.board_sz = board
        self.gap = max(round(board * 0.028), 4)
        self.tile_sz = (board - self.gap * 5) / 4.0
        self.corner_r = max(self.tile_sz * 0.065, 3)

        self.board_x = (w - board) / 2.0
        self.board_y = sb + (safe_h - board - header_h) / 2.0
        self.board_y = max(self.board_y, sb + margin)
        self.header_y = self.board_y + board + 10

        self._cached_size = (w, h)

    def _tile_pos(self, row, col):
        x = self.board_x + self.gap + col * (self.tile_sz + self.gap)
        y = (self.board_y + self.board_sz
             - self.gap - self.tile_sz
             - row * (self.tile_sz + self.gap))
        return x, y

    # ── Grid Logic ──────────────────────────────────────────────

    def _spawn_tiles(self, count=1):
        for _ in range(count):
            empty = [(r, c)
                     for r in range(4) for c in range(4)
                     if self.grid[r][c] == 0]
            if not empty:
                return
            r, c = random.choice(empty)
            v = 2 if random.random() < 0.9 else 4
            self.grid[r][c] = v
            self.spawns.append([r, c, v, 0.0])

    def _merge_line(self, tiles, to_rc):
        non_zero = [(v, r, c) for v, r, c in tiles if v]
        result = [0] * 4
        slide_list = []
        merge_list = []
        points = 0
        write_pos = 0
        i = 0

        while i < len(non_zero):
            v1, r1, c1 = non_zero[i]

            if i + 1 < len(non_zero) and v1 == non_zero[i + 1][0]:
                v2, r2, c2 = non_zero[i + 1]
                merged_val = v1 * 2
                result[write_pos] = merged_val
                tr, tc = to_rc(write_pos)
                slide_list.append([r1, c1, tr, tc, v1, 0.0])
                slide_list.append([r2, c2, tr, tc, v2, 0.0])
                merge_list.append([tr, tc, merged_val, 0.0])
                points += merged_val
                write_pos += 1
                i += 2
            else:
                result[write_pos] = v1
                tr, tc = to_rc(write_pos)
                slide_list.append([r1, c1, tr, tc, v1, 0.0])
                write_pos += 1
                i += 1

        return result, slide_list, merge_list, points

    def _do_move(self, direction):
        if self.phase != IDLE:
            return False

        old_grid = copy.deepcopy(self.grid)
        old_score = self.score
        all_slides = []
        all_merges = []
        changed = False

        for i in range(4):
            if direction == 'left':
                line = [(self.grid[i][j], i, j) for j in range(4)]
                to_rc = lambda idx, _i=i: (_i, idx)
                write_back = lambda j, _i=i: (_i, j)

            elif direction == 'right':
                line = [(self.grid[i][3 - j], i, 3 - j)
                        for j in range(4)]
                to_rc = lambda idx, _i=i: (_i, 3 - idx)
                write_back = lambda j, _i=i: (_i, 3 - j)

            elif direction == 'up':
                line = [(self.grid[j][i], j, i) for j in range(4)]
                to_rc = lambda idx, _i=i: (idx, _i)
                write_back = lambda j, _i=i: (j, _i)

            else:
                line = [(self.grid[3 - j][i], 3 - j, i)
                        for j in range(4)]
                to_rc = lambda idx, _i=i: (3 - idx, _i)
                write_back = lambda j, _i=i: (3 - j, _i)

            result, slides, merges, pts = self._merge_line(line, to_rc)

            for j in range(4):
                r, c = write_back(j)
                if self.grid[r][c] != result[j]:
                    changed = True
                self.grid[r][c] = result[j]

            self.score += pts
            all_slides.extend(slides)
            all_merges.extend(merges)

        if changed:
            self.prev_grid = old_grid
            self.prev_score = old_score
            self.best_score = max(self.best_score, self.score)
            self.slides = all_slides
            self.merges = all_merges
            self.spawns = []
            self.phase = SLIDING
            return True

        return False

    def _can_move(self):
        for r in range(4):
            for c in range(4):
                if self.grid[r][c] == 0:
                    return True
                if c < 3 and self.grid[r][c] == self.grid[r][c + 1]:
                    return True
                if r < 3 and self.grid[r][c] == self.grid[r + 1][c]:
                    return True
        return False

    def _has_won(self):
        if self.keep_playing:
            return False
        return any(self.grid[r][c] >= 2048
                   for r in range(4) for c in range(4))

    def _undo(self):
        if self.prev_grid is None:
            return
        self.grid = self.prev_grid
        self.score = self.prev_score
        self.prev_grid = None
        self.prev_score = None
        self.game_over = False
        self.won = False
        self.slides = []
        self.spawns = []
        self.merges = []
        self.phase = IDLE

    def _new_game(self):
        self.grid = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.prev_grid = None
        self.prev_score = None
        self.game_over = False
        self.won = False
        self.keep_playing = False
        self.slides = []
        self.spawns = []
        self.merges = []
        self.pops = []
        self.phase = IDLE
        self._spawn_tiles(2)

    # ── Update ──────────────────────────────────────────────────

    def update(self):
        dt = self.dt

        if self.phase == SLIDING:
            all_done = True
            for s in self.slides:
                s[5] += dt
                if s[5] < self.slide_dur:
                    all_done = False

            if all_done:
                self.slides = []
                self._spawn_tiles()
                for m in self.merges:
                    m[3] = 0.0
                    self.pops.append([m[2], m[0], m[1], 0.0])
                self.phase = SETTLING

                if self._has_won():
                    self.won = True
                elif not self._can_move():
                    self.game_over = True

        elif self.phase == SETTLING:
            all_done = True
            for a in self.spawns:
                a[3] += dt
                if a[3] < self.spawn_dur:
                    all_done = False
            for a in self.merges:
                a[3] += dt
                if a[3] < self.merge_dur:
                    all_done = False

            if all_done:
                self.spawns = []
                self.merges = []
                self.phase = IDLE

        alive = []
        for p in self.pops:
            p[3] += dt
            if p[3] < self.pop_dur:
                alive.append(p)
        self.pops = alive

    # ── Draw ────────────────────────────────────────────────────

    def draw(self):
        if self._cached_size != (self.size.w, self.size.h):
            self._calc_layout()

        scene.background(*PAGE_BG)
        self._draw_header()
        self._draw_board()
        self._draw_pops()

        if self.won:
            self._draw_overlay('🎉 You Win!', 'Tap to continue')
        elif self.game_over:
            self._draw_overlay('Game Over', 'Tap to restart')

    def _draw_header(self):
        bx = self.board_x
        bsz = self.board_sz
        hy = self.header_y

        scene.tint(*DARK_TEXT, 1)
        scene.text('2048', 'Helvetica-Bold', 44, bx, hy + 52, 1)

        scene.tint(0.60, 0.55, 0.50, 1)
        scene.text('数字拼图', 'Helvetica', 14, bx, hy + 14, 1)

        # ── Score / Best boxes ──
        box_w = bsz * 0.26
        box_h = 48
        score_x = bx + bsz - box_w * 2 - 6
        best_x = bx + bsz - box_w
        box_y = hy + 42

        for label, value, xx in [('SCORE', self.score, score_x),
                                  ('BEST', self.best_score, best_x)]:
            scene.fill(*BOARD_BG, 1)
            scene.no_stroke()
            scene.rect(xx, box_y, box_w, box_h, 5)

            scene.tint(0.93, 0.89, 0.85, 1)
            scene.text(label, 'Helvetica-Bold', 11,
                       xx + box_w / 2, box_y + box_h - 15, 5)

            scene.tint(1, 1, 1, 1)
            fs = 20 if value < 100000 else 15
            scene.text(str(value), 'Helvetica-Bold', fs,
                       xx + box_w / 2, box_y + box_h / 2 - 4, 5)

        # ── Buttons ──
        btn_h = 30
        new_w = bsz * 0.24
        undo_w = bsz * 0.18
        new_x = bx + bsz - new_w
        undo_x = new_x - undo_w - 6

        scene.fill(*BUTTON_BG, 1)
        scene.no_stroke()
        scene.rect(new_x, hy, new_w, btn_h, 4)
        scene.tint(1, 1, 1, 1)
        scene.text('New', 'Helvetica-Bold', 13,
                   new_x + new_w / 2, hy + btn_h / 2, 5)
        self._btn_new = (new_x, hy, new_w, btn_h)

        undo_alpha = 1.0 if self.prev_grid else 0.35
        scene.fill(*BUTTON_BG, undo_alpha)
        scene.rect(undo_x, hy, undo_w, btn_h, 4)
        scene.tint(1, 1, 1, undo_alpha)
        scene.text('↩', 'Helvetica', 18,
                   undo_x + undo_w / 2, hy + btn_h / 2, 5)
        self._btn_undo = (undo_x, hy, undo_w, btn_h)

    def _draw_board(self):
        scene.fill(*BOARD_BG, 1)
        scene.no_stroke()
        scene.rect(self.board_x, self.board_y,
                   self.board_sz, self.board_sz, 8)

        er, eg, eb = TILE_CLR[0]
        for r in range(4):
            for c in range(4):
                x, y = self._tile_pos(r, c)
                scene.fill(er, eg, eb, 1)
                scene.rect(x, y, self.tile_sz, self.tile_sz,
                           self.corner_r)

        if self.phase == SLIDING:
            self._draw_sliding()
        else:
            self._draw_settled()

    def _draw_sliding(self):
        for fr, fc, tr, tc, v, t in self.slides:
            p = min(t / self.slide_dur, 1.0)
            p = 1.0 - (1.0 - p) ** 3
            fx, fy = self._tile_pos(fr, fc)
            tx, ty = self._tile_pos(tr, tc)
            self._render_tile(fx + (tx - fx) * p,
                              fy + (ty - fy) * p, v)

    def _draw_settled(self):
        spawn_cells = {(a[0], a[1]) for a in self.spawns}
        merge_map = {(a[0], a[1]): a for a in self.merges}

        for r in range(4):
            for c in range(4):
                v = self.grid[r][c]
                if not v:
                    continue

                x, y = self._tile_pos(r, c)

                if (r, c) in spawn_cells:
                    sa = next(a for a in self.spawns
                              if a[0] == r and a[1] == c)
                    t = min(sa[3] / self.spawn_dur, 1.0)
                    if t < 0.7:
                        scale = (t / 0.7) * 1.12
                    else:
                        scale = 1.12 - 0.12 * ((t - 0.7) / 0.3)
                    self._render_tile(x, y, v, scale)

                elif (r, c) in merge_map:
                    ma = merge_map[(r, c)]
                    t = min(ma[3] / self.merge_dur, 1.0)
                    scale = 1.0 + 0.2 * math.sin(t * math.pi)
                    self._render_tile(x, y, v, scale)

                else:
                    self._render_tile(x, y, v)

    def _render_tile(self, x, y, val, scale=1.0):
        ts = self.tile_sz

        if scale != 1.0:
            new_sz = ts * scale
            x += (ts - new_sz) / 2
            y += (ts - new_sz) / 2
            ts = new_sz

        if val >= 128:
            pulse = 0.10 + 0.04 * math.sin(self.t * 3.0)
            gr, gg, gb = tile_color(val)
            scene.fill(gr, gg, gb, pulse)
            scene.no_stroke()
            scene.rect(x - 3, y - 3, ts + 6, ts + 6,
                       self.corner_r + 2)

        tr, tg, tb = tile_color(val)
        scene.fill(tr, tg, tb, 1)
        scene.no_stroke()
        scene.rect(x, y, ts, ts, self.corner_r)

        if val:
            nr, ng, nb = text_color(val)
            scene.tint(nr, ng, nb, 1)
            fs = font_size(val, self.tile_sz) * min(scale, 1.0)
            scene.text(str(val), 'Helvetica-Bold', fs,
                       x + ts / 2, y + ts / 2, 5)

    def _draw_pops(self):
        for val, r, c, t in self.pops:
            px, py = self._tile_pos(r, c)
            progress = t / self.pop_dur
            alpha = max(1.0 - progress * 1.3, 0)
            float_y = progress * 45
            scene.tint(*DARK_TEXT, alpha)
            scene.text('+%d' % val, 'Helvetica-Bold', 16,
                       px + self.tile_sz / 2,
                       py + self.tile_sz + float_y + 5, 5)

    def _draw_overlay(self, title, subtitle):
        scene.fill(1, 1, 1, 0.6)
        scene.no_stroke()
        scene.rect(self.board_x, self.board_y,
                   self.board_sz, self.board_sz, 8)

        cx = self.board_x + self.board_sz / 2
        cy = self.board_y + self.board_sz / 2

        scene.tint(*DARK_TEXT, 1)
        scene.text(title, 'Helvetica-Bold', 38, cx, cy + 20, 5)

        scene.tint(0.55, 0.47, 0.40, 1)
        scene.text(subtitle, 'Helvetica', 17, cx, cy - 22, 5)

    # ── Touch Input ─────────────────────────────────────────────

    def touch_began(self, touch):
        self.touch_start = (touch.location.x, touch.location.y)

    def touch_moved(self, touch):
        pass

    def touch_ended(self, touch):
        if self.touch_start is None:
            return

        end_x = touch.location.x
        end_y = touch.location.y
        start_x, start_y = self.touch_start
        dx = end_x - start_x
        dy = end_y - start_y
        dist = math.hypot(dx, dy)
        self.touch_start = None

        if dist < self.swipe_min:
            self._handle_tap(end_x, end_y)
            return

        if self.phase != IDLE or self.game_over or self.won:
            return

        if abs(dx) >= abs(dy):
            direction = 'right' if dx > 0 else 'left'
        else:
            direction = 'up' if dy > 0 else 'down'

        self._do_move(direction)

    def _handle_tap(self, x, y):
        if self._point_in_rect(x, y, self._btn_new):
            self._new_game()
        elif self._point_in_rect(x, y, self._btn_undo):
            self._undo()
        elif self.won:
            self.won = False
            self.keep_playing = True
        elif self.game_over:
            self._new_game()

    @staticmethod
    def _point_in_rect(x, y, rect):
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh


scene.run(Game2048())
