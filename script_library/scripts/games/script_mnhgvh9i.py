import os
import random

import scene
import sound
import ui


BOARD_ROWS = 10
BOARD_COLS = 9
HUMAN_SIDE = 'r'
AI_SIDE = 'b'
MATE_SCORE = 999999

ORTHOGONAL_DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))

PIECE_TEXT = {
    'rK': '帅',
    'rA': '仕',
    'rE': '相',
    'rH': '马',
    'rR': '车',
    'rC': '炮',
    'rP': '兵',
    'bK': '将',
    'bA': '士',
    'bE': '象',
    'bH': '马',
    'bR': '车',
    'bC': '炮',
    'bP': '卒',
}

PIECE_VALUES = {
    'K': 100000,
    'R': 920,
    'H': 430,
    'C': 470,
    'A': 210,
    'E': 210,
    'P': 120,
}

INITIAL_COUNTS = {
    'rK': 1, 'rA': 2, 'rE': 2, 'rH': 2, 'rR': 2, 'rC': 2, 'rP': 5,
    'bK': 1, 'bA': 2, 'bE': 2, 'bH': 2, 'bR': 2, 'bC': 2, 'bP': 5,
}


class XiangqiEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.turn = HUMAN_SIDE
        self.history = []
        self.king_pos = {'r': (9, 4), 'b': (0, 4)}
        self._setup_initial_board()

    def _setup_initial_board(self):
        top = ['R', 'H', 'E', 'A', 'K', 'A', 'E', 'H', 'R']
        bottom = ['R', 'H', 'E', 'A', 'K', 'A', 'E', 'H', 'R']

        for col, kind in enumerate(top):
            self.board[0][col] = 'b' + kind
            self.board[9][col] = 'r' + bottom[col]

        self.board[2][1] = 'bC'
        self.board[2][7] = 'bC'
        self.board[7][1] = 'rC'
        self.board[7][7] = 'rC'

        for col in (0, 2, 4, 6, 8):
            self.board[3][col] = 'bP'
            self.board[6][col] = 'rP'

    def other(self, color):
        return 'b' if color == 'r' else 'r'

    def inside(self, row, col):
        return 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS

    def in_palace(self, color, row, col):
        if not (3 <= col <= 5):
            return False
        if color == 'r':
            return 7 <= row <= 9
        return 0 <= row <= 2

    def crossed_river(self, color, row):
        return row <= 4 if color == 'r' else row >= 5

    def piece_count(self):
        count = 0
        for row in self.board:
            for piece in row:
                if piece:
                    count += 1
        return count

    def board_key(self):
        return tuple(tuple(row) for row in self.board)

    def pseudo_moves(self, color):
        moves = []
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if not piece or piece[0] != color:
                    continue
                kind = piece[1]
                if kind == 'K':
                    self._gen_king_moves(row, col, piece, moves)
                elif kind == 'A':
                    self._gen_advisor_moves(row, col, piece, moves)
                elif kind == 'E':
                    self._gen_elephant_moves(row, col, piece, moves)
                elif kind == 'H':
                    self._gen_horse_moves(row, col, piece, moves)
                elif kind == 'R':
                    self._gen_rook_moves(row, col, piece, moves)
                elif kind == 'C':
                    self._gen_cannon_moves(row, col, piece, moves)
                elif kind == 'P':
                    self._gen_pawn_moves(row, col, piece, moves)
        return moves

    def legal_moves(self, color=None):
        color = color or self.turn
        legal = []
        for move in self.pseudo_moves(color):
            self.make_move(move, store_history=False)
            if not self.is_in_check(color):
                legal.append(move)
            self.undo_move(move)
        return legal

    def legal_targets_from(self, row, col):
        piece = self.board[row][col]
        if not piece:
            return []
        return [move for move in self.legal_moves(piece[0]) if move[0] == row and move[1] == col]

    def make_move(self, move, store_history=True):
        from_row, from_col, to_row, to_col, piece, captured = move
        self.board[from_row][from_col] = None
        self.board[to_row][to_col] = piece
        if piece[1] == 'K':
            self.king_pos[piece[0]] = (to_row, to_col)
        if captured and captured[1] == 'K':
            self.king_pos[captured[0]] = None
        self.turn = self.other(piece[0])
        if store_history:
            self.history.append(move)
        return move

    def undo_move(self, move=None):
        if move is None:
            if not self.history:
                return False
            move = self.history.pop()
        from_row, from_col, to_row, to_col, piece, captured = move
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured
        self.turn = piece[0]
        if piece[1] == 'K':
            self.king_pos[piece[0]] = (from_row, from_col)
        if captured and captured[1] == 'K':
            self.king_pos[captured[0]] = (to_row, to_col)
        return True

    def current_winner(self):
        if self.king_pos['r'] is None:
            return 'b'
        if self.king_pos['b'] is None:
            return 'r'
        legal = self.legal_moves(self.turn)
        if legal:
            return None
        if self.is_in_check(self.turn):
            return self.other(self.turn)
        return 'draw'

    def move_heuristic(self, move, color):
        from_row, from_col, to_row, to_col, piece, captured = move
        score = 0
        if captured:
            score += PIECE_VALUES[captured[1]] * 12 - PIECE_VALUES[piece[1]]
            if captured[1] == 'K':
                score += MATE_SCORE
        score += self.position_bonus(piece, to_row, to_col)
        score -= self.position_bonus(piece, from_row, from_col)
        if piece[1] == 'P' and self.crossed_river(piece[0], to_row):
            score += 30
        score += (4 - abs(to_col - 4)) * 3
        return score if piece[0] == color else -score

    def evaluate(self):
        if self.king_pos['r'] is None:
            return MATE_SCORE
        if self.king_pos['b'] is None:
            return -MATE_SCORE

        score = 0
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if not piece:
                    continue
                sign = 1 if piece[0] == AI_SIDE else -1
                score += sign * (PIECE_VALUES[piece[1]] + self.position_bonus(piece, row, col))

        score += 3 * (len(self.pseudo_moves(AI_SIDE)) - len(self.pseudo_moves(HUMAN_SIDE)))
        if self.is_in_check(HUMAN_SIDE):
            score += 40
        if self.is_in_check(AI_SIDE):
            score -= 40
        return score

    def position_bonus(self, piece, row, col):
        color = piece[0]
        kind = piece[1]
        center = 4 - abs(col - 4)
        advance = row if color == 'b' else (9 - row)

        if kind == 'P':
            bonus = advance * 16
            if self.crossed_river(color, row):
                bonus += 36 + center * 8
            return bonus
        if kind == 'R':
            return center * 8 + advance * 4
        if kind == 'H':
            return center * 13 + advance * 5
        if kind == 'C':
            return center * 11 + advance * 3
        if kind == 'A':
            return 12 - abs(col - 4) * 4
        if kind == 'E':
            return 8 - abs(col - 4) * 2
        return 0

    def is_in_check(self, color):
        king = self.king_pos[color]
        if king is None:
            return True

        enemy = self.other(color)
        king_row, king_col = king

        for dr, dc in ORTHOGONAL_DIRS:
            blockers = 0
            row = king_row + dr
            col = king_col + dc
            while self.inside(row, col):
                piece = self.board[row][col]
                if piece:
                    if blockers == 0:
                        if piece[0] == enemy and piece[1] in ('R', 'K'):
                            return True
                        blockers = 1
                    else:
                        if piece[0] == enemy and piece[1] == 'C':
                            return True
                        break
                row += dr
                col += dc

        if enemy == 'r':
            if self.inside(king_row + 1, king_col) and self.board[king_row + 1][king_col] == 'rP':
                return True
            if king_row <= 4:
                for dc in (-1, 1):
                    col = king_col + dc
                    if self.inside(king_row, col) and self.board[king_row][col] == 'rP':
                        return True
        else:
            if self.inside(king_row - 1, king_col) and self.board[king_row - 1][king_col] == 'bP':
                return True
            if king_row >= 5:
                for dc in (-1, 1):
                    col = king_col + dc
                    if self.inside(king_row, col) and self.board[king_row][col] == 'bP':
                        return True

        horse_checks = (
            (-2, -1, -1, 0), (-2, 1, -1, 0),
            (2, -1, 1, 0), (2, 1, 1, 0),
            (-1, -2, 0, -1), (1, -2, 0, -1),
            (-1, 2, 0, 1), (1, 2, 0, 1),
        )
        for dr, dc, leg_row_off, leg_col_off in horse_checks:
            row = king_row + dr
            col = king_col + dc
            leg_row = king_row + leg_row_off
            leg_col = king_col + leg_col_off
            if not self.inside(row, col) or not self.inside(leg_row, leg_col):
                continue
            if self.board[leg_row][leg_col] is None and self.board[row][col] == enemy + 'H':
                return True

        return False

    def _push_move(self, moves, from_row, from_col, to_row, to_col, piece):
        if not self.inside(to_row, to_col):
            return
        target = self.board[to_row][to_col]
        if target and target[0] == piece[0]:
            return
        moves.append((from_row, from_col, to_row, to_col, piece, target))

    def _gen_king_moves(self, row, col, piece, moves):
        for dr, dc in ORTHOGONAL_DIRS:
            next_row = row + dr
            next_col = col + dc
            if self.in_palace(piece[0], next_row, next_col):
                self._push_move(moves, row, col, next_row, next_col, piece)

        for dr in (-1, 1):
            scan_row = row + dr
            while self.inside(scan_row, col):
                target = self.board[scan_row][col]
                if target:
                    if target[0] != piece[0] and target[1] == 'K':
                        moves.append((row, col, scan_row, col, piece, target))
                    break
                scan_row += dr

    def _gen_advisor_moves(self, row, col, piece, moves):
        for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            next_row = row + dr
            next_col = col + dc
            if self.in_palace(piece[0], next_row, next_col):
                self._push_move(moves, row, col, next_row, next_col, piece)

    def _gen_elephant_moves(self, row, col, piece, moves):
        home_side_min = 5 if piece[0] == 'r' else 0
        home_side_max = 9 if piece[0] == 'r' else 4
        candidates = (
            (2, 2, 1, 1), (2, -2, 1, -1),
            (-2, 2, -1, 1), (-2, -2, -1, -1),
        )
        for dr, dc, eye_dr, eye_dc in candidates:
            next_row = row + dr
            next_col = col + dc
            eye_row = row + eye_dr
            eye_col = col + eye_dc
            if not self.inside(next_row, next_col):
                continue
            if not (home_side_min <= next_row <= home_side_max):
                continue
            if self.board[eye_row][eye_col] is None:
                self._push_move(moves, row, col, next_row, next_col, piece)

    def _gen_horse_moves(self, row, col, piece, moves):
        candidates = (
            (-2, -1, -1, 0), (-2, 1, -1, 0),
            (2, -1, 1, 0), (2, 1, 1, 0),
            (-1, -2, 0, -1), (1, -2, 0, -1),
            (-1, 2, 0, 1), (1, 2, 0, 1),
        )
        for dr, dc, leg_dr, leg_dc in candidates:
            leg_row = row + leg_dr
            leg_col = col + leg_dc
            next_row = row + dr
            next_col = col + dc
            if not self.inside(next_row, next_col):
                continue
            if self.board[leg_row][leg_col] is None:
                self._push_move(moves, row, col, next_row, next_col, piece)

    def _gen_rook_moves(self, row, col, piece, moves):
        for dr, dc in ORTHOGONAL_DIRS:
            next_row = row + dr
            next_col = col + dc
            while self.inside(next_row, next_col):
                target = self.board[next_row][next_col]
                if target is None:
                    moves.append((row, col, next_row, next_col, piece, None))
                else:
                    if target[0] != piece[0]:
                        moves.append((row, col, next_row, next_col, piece, target))
                    break
                next_row += dr
                next_col += dc

    def _gen_cannon_moves(self, row, col, piece, moves):
        for dr, dc in ORTHOGONAL_DIRS:
            next_row = row + dr
            next_col = col + dc
            screen_found = False
            while self.inside(next_row, next_col):
                target = self.board[next_row][next_col]
                if not screen_found:
                    if target is None:
                        moves.append((row, col, next_row, next_col, piece, None))
                    else:
                        screen_found = True
                else:
                    if target:
                        if target[0] != piece[0]:
                            moves.append((row, col, next_row, next_col, piece, target))
                        break
                next_row += dr
                next_col += dc

    def _gen_pawn_moves(self, row, col, piece, moves):
        forward = -1 if piece[0] == 'r' else 1
        self._push_move(moves, row, col, row + forward, col, piece)
        if self.crossed_river(piece[0], row):
            self._push_move(moves, row, col, row, col - 1, piece)
            self._push_move(moves, row, col, row, col + 1, piece)


class XiangqiAI:
    def __init__(self, engine):
        self.engine = engine
        self.nodes = 0
        self.last_depth = 0
        self.last_nodes = 0
        self.transposition = {}

    def choose_move(self, color, difficulty):
        legal = self.engine.legal_moves(color)
        if not legal:
            self.last_depth = 0
            self.last_nodes = 0
            return None

        ordered = self._order_moves(legal, color)
        if difficulty == 'easy':
            self.last_depth = 1
            self.last_nodes = len(ordered)
            top = ordered[:min(6, len(ordered))]
            return random.choice(top[:min(4, len(top))])

        piece_count = self.engine.piece_count()
        if difficulty == 'medium':
            depths = [1, 2, 3] if piece_count <= 22 else [1, 2]
            root_limit = 24
            branch_limit = 12 if piece_count > 20 else 14
        else:
            depths = [1, 2, 3]
            if piece_count <= 12:
                depths.append(4)
            root_limit = 30
            branch_limit = 15 if piece_count > 16 else 12

        self.nodes = 0
        self.transposition = {}
        best_move = ordered[0]
        best_score = -10 ** 12
        ordered_root = ordered

        for depth in depths:
            self.last_depth = depth
            alpha = -10 ** 12
            beta = 10 ** 12
            iteration_best_score = -10 ** 12
            iteration_best_move = ordered_root[0]

            for move in ordered_root[:root_limit]:
                if move[5] and move[5][1] == 'K':
                    self.last_nodes = self.nodes + 1
                    self.last_depth = depth
                    return move
                self.engine.make_move(move, store_history=False)
                score = -self._search(depth - 1, -beta, -alpha, self.engine.other(color), branch_limit, 1)
                self.engine.undo_move(move)
                if score > iteration_best_score:
                    iteration_best_score = score
                    iteration_best_move = move
                if score > alpha:
                    alpha = score

            best_move = iteration_best_move
            best_score = iteration_best_score
            ordered_root = [best_move] + [move for move in ordered if move != best_move]

        self.last_nodes = self.nodes
        if difficulty == 'medium':
            medium_pool = ordered_root[:min(3, len(ordered_root))]
            return medium_pool[0] if random.random() < 0.8 else random.choice(medium_pool)
        return best_move if best_score > -MATE_SCORE + 20 else ordered_root[0]

    def _search(self, depth, alpha, beta, color, branch_limit, ply):
        self.nodes += 1
        if self.engine.king_pos[color] is None:
            return -MATE_SCORE + ply
        enemy = self.engine.other(color)
        if self.engine.king_pos[enemy] is None:
            return MATE_SCORE - ply

        legal = self.engine.legal_moves(color)
        if not legal:
            if self.engine.is_in_check(color):
                return -MATE_SCORE + ply
            return 0

        if depth <= 0:
            if self.engine.is_in_check(color) and ply < 7:
                depth = 1
            else:
                return self._evaluate_for(color)

        cache_key = (color, depth, self.engine.board_key())
        cached = self.transposition.get(cache_key)
        if cached is not None:
            return cached

        ordered = self._order_moves(legal, color)
        if len(ordered) > branch_limit:
            ordered = ordered[:branch_limit]

        best = -10 ** 12
        for move in ordered:
            self.engine.make_move(move, store_history=False)
            score = -self._search(depth - 1, -beta, -alpha, enemy, branch_limit, ply + 1)
            self.engine.undo_move(move)
            if score > best:
                best = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break
        self.transposition[cache_key] = best
        return best

    def _evaluate_for(self, color):
        base = self.engine.evaluate()
        return base if color == AI_SIDE else -base

    def _order_moves(self, moves, color):
        scored = []
        enemy = self.engine.other(color)
        for move in moves:
            score = self.engine.move_heuristic(move, color)
            self.engine.make_move(move, store_history=False)
            if self.engine.is_in_check(enemy):
                score += 180
            enemy_responses = len(self.engine.legal_moves(enemy))
            score -= enemy_responses * 2
            self.engine.undo_move(move)
            scored.append((score, move))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored]


class XiangqiArena(scene.Scene):
    def setup(self):
        self.background_color = '#2d1815'
        self.engine = XiangqiEngine()
        self.ai = XiangqiAI(self.engine)
        self.vs_bot = True
        self.game_over = False
        self.winner = None
        self.music_on = True
        self.music_handle = None
        self.music_player = None
        self.difficulty = 'medium'
        self.difficulties = [('easy', '简单'), ('medium', '中等'), ('hard', '困难')]
        self.ai_wait = 0.45
        self.ai_timer = 0.0
        self.ai_thinking = False
        self.animating = False
        self.selected_square = None
        self.selected_moves = []
        self.last_ai_summary = ''
        self.board_nodes = []
        self.piece_nodes = []
        self.last_move_nodes = []
        self.selection_nodes = []
        self.target_nodes = []
        self.check_nodes = []
        self.animation_nodes = []
        self.buttons = {}

        self.board_root = scene.Node(parent=self, z_position=1)
        self.fx_root = scene.Node(parent=self, z_position=6)
        self.piece_root = scene.Node(parent=self, z_position=10)
        self.ui_root = scene.Node(parent=self, z_position=20)

        self._compute_layout()
        self._build_board()
        self._build_ui()
        self.refresh_dynamic_nodes()
        self.refresh_labels()
        self.start_music()
        self.play_effect('music:Start_NES_1', volume=0.3)

    def stop(self):
        self.stop_music()

    def _compute_layout(self):
        insets = self.safe_area_insets
        top = getattr(insets, 'top', 0) or 0
        bottom = getattr(insets, 'bottom', 0) or 0
        left = getattr(insets, 'left', 0) or 0
        right = getattr(insets, 'right', 0) or 0

        safe_w = self.size.w - left - right
        safe_h = self.size.h - top - bottom
        top_bar = 78
        bottom_panel = 128
        side_margin = 18

        self.cell = min((safe_w - side_margin * 2) / 8.0, (safe_h - top_bar - bottom_panel) / 9.0)
        self.cell = max(self.cell, 28)
        self.board_w = self.cell * 8
        self.board_h = self.cell * 9
        self.board_x = self.size.w / 2.0 - self.board_w / 2.0
        available_h = safe_h - top_bar - bottom_panel - self.board_h
        self.board_y = bottom + bottom_panel + max(12, available_h / 2.0)
        self.board_mid_y = self.board_y + self.board_h / 2.0
        self.bottom_y = bottom + 16
        self.top_y = self.size.h - top - 36

    def board_point(self, row, col):
        x = self.board_x + col * self.cell
        y = self.board_y + (9 - row) * self.cell
        return x, y

    def point_to_cell(self, point):
        col = round((point.x - self.board_x) / self.cell)
        rank = round((point.y - self.board_y) / self.cell)
        if not (0 <= col < BOARD_COLS and 0 <= rank < BOARD_ROWS):
            return None, None
        x, y = self.board_x + col * self.cell, self.board_y + rank * self.cell
        if abs(point.x - x) > self.cell * 0.46 or abs(point.y - y) > self.cell * 0.46:
            return None, None
        return 9 - rank, col

    def _build_board(self):
        panel_w = self.board_w + self.cell * 1.1
        panel_h = self.board_h + self.cell * 1.2
        board_image = self._make_board_image(panel_w, panel_h)
        board_panel = scene.SpriteNode(
            scene.Texture(board_image),
            size=(panel_w, panel_h),
            position=(self.size.w / 2, self.board_mid_y),
            parent=self.board_root,
            z_position=0,
        )
        self.board_nodes.append(board_panel)

        river_left = scene.LabelNode(
            '楚   河',
            font=('Helvetica-Bold', max(18, self.cell * 0.42)),
            color='#7f3d29',
            position=(self.board_x + self.board_w * 0.25, self.board_y + self.board_h / 2.0),
            parent=self.board_root,
            z_position=2,
        )
        river_right = scene.LabelNode(
            '汉   界',
            font=('Helvetica-Bold', max(18, self.cell * 0.42)),
            color='#7f3d29',
            position=(self.board_x + self.board_w * 0.75, self.board_y + self.board_h / 2.0),
            parent=self.board_root,
            z_position=2,
        )
        self.board_nodes.extend([river_left, river_right])

    def _make_board_image(self, panel_w, panel_h):
        margin_x = (panel_w - self.board_w) / 2.0
        margin_y = (panel_h - self.board_h) / 2.0
        line_color = '#6b3e1f'
        frame_color = '#f6ddb1'

        def texture_point(row, col):
            x = margin_x + col * self.cell
            y = margin_y + row * self.cell
            return x, y

        def stroke_line(x1, y1, x2, y2, width):
            lib = ui._init_lib()
            if lib:
                lib.ui_draw_path_begin()
            path = ui.Path()
            path.line_width = width
            path.move_to(x1, y1)
            path.line_to(x2, y2)
            path.stroke()

        with ui.ImageContext(int(panel_w), int(panel_h)) as ctx:
            ui.set_color('#d8b272')
            outer = ui.Path.rounded_rect(0, 0, panel_w, panel_h, 26)
            outer.fill()
            ui.set_color('#f7ddb2')
            outer.line_width = 3.0
            outer.stroke()

            ui.set_color('#e1bc79')
            inner = ui.Path.rounded_rect(8, 8, panel_w - 16, panel_h - 16, 22)
            inner.fill()

            ui.set_color('#e8c989')
            ui.fill_rect(margin_x, margin_y + self.board_h * 0.43, self.board_w, self.cell * 1.15)

            ui.set_color(line_color)
            for rank in range(BOARD_ROWS):
                y = margin_y + rank * self.cell
                stroke_line(margin_x, y, margin_x + self.board_w, y, 2.6)

            full_top = margin_y + self.board_h
            river_top = margin_y + self.cell * 5
            river_bottom = margin_y + self.cell * 4
            for col in range(BOARD_COLS):
                x = margin_x + col * self.cell
                if col in (0, BOARD_COLS - 1):
                    stroke_line(x, margin_y, x, full_top, 2.6)
                else:
                    stroke_line(x, margin_y, x, river_bottom, 2.6)
                    stroke_line(x, river_top, x, full_top, 2.6)

            palace_lines = (
                ((0, 3), (2, 5)),
                ((0, 5), (2, 3)),
                ((7, 3), (9, 5)),
                ((7, 5), (9, 3)),
            )
            for start, end in palace_lines:
                x1, y1 = texture_point(*start)
                x2, y2 = texture_point(*end)
                stroke_line(x1, y1, x2, y2, 2.6)

            for row, col in self._marker_positions():
                self._draw_texture_markers(row, col, margin_x, margin_y)

            return ctx.get_image()

    def _marker_positions(self):
        positions = [(2, 1), (2, 7), (7, 1), (7, 7)]
        for row in (3, 6):
            for col in (0, 2, 4, 6, 8):
                positions.append((row, col))
        return positions

    def _draw_texture_markers(self, row, col, margin_x, margin_y):
        x = margin_x + col * self.cell
        y = margin_y + row * self.cell
        gap = self.cell * 0.18
        short = self.cell * 0.14
        long = self.cell * 0.1
        color = '#6b3e1f'
        for side in (-1, 1):
            if col == 0 and side == -1:
                continue
            if col == 8 and side == 1:
                continue
            base_x = x + side * gap
            lib = ui._init_lib()
            if lib:
                lib.ui_draw_path_begin()
            path = ui.Path()
            path.line_width = 2.2
            path.move_to(base_x, y + gap)
            path.line_to(base_x + side * short, y + gap)
            path.move_to(base_x, y + gap)
            path.line_to(base_x, y + gap + long)
            path.move_to(base_x, y - gap)
            path.line_to(base_x + side * short, y - gap)
            path.move_to(base_x, y - gap)
            path.line_to(base_x, y - gap - long)
            ui.set_color(color)
            path.stroke()

    def _build_ui(self):
        title = scene.LabelNode(
            '象棋擂台',
            font=('Helvetica-Bold', 24),
            color='#f5e6c5',
            position=(self.size.w / 2, self.top_y + 34),
            parent=self.ui_root,
        )
        subtitle = scene.LabelNode(
            '带音乐、悔棋和 AI 的楚河汉界',
            font=('Helvetica', 12),
            color='#d6c5a2',
            position=(self.size.w / 2, self.top_y + 14),
            parent=self.ui_root,
        )

        self.status_label = scene.LabelNode(
            '',
            font=('Helvetica-Bold', 20),
            color='#fff4d2',
            position=(self.size.w / 2, self.bottom_y + 86),
            parent=self.ui_root,
        )
        self.info_label = scene.LabelNode(
            '',
            font=('Helvetica', 13),
            color='#e6d6b4',
            position=(self.size.w / 2, self.bottom_y + 60),
            parent=self.ui_root,
        )
        self.red_capture_label = scene.LabelNode(
            '',
            font=('Helvetica-Bold', 13),
            color='#ff8c7a',
            position=(self.size.w * 0.28, self.bottom_y + 26),
            parent=self.ui_root,
        )
        self.black_capture_label = scene.LabelNode(
            '',
            font=('Helvetica-Bold', 13),
            color='#c8d6e5',
            position=(self.size.w * 0.72, self.bottom_y + 26),
            parent=self.ui_root,
        )

        self.ai_dots = []
        for index in range(3):
            dot = scene.ShapeNode(
                path=('oval', -5, -5, 10, 10),
                fill_color='#56d6ff',
                stroke_color='#00000000',
                position=(self.size.w / 2 - 24 + index * 24, self.bottom_y + 42),
                parent=self.ui_root,
                alpha=0.0,
            )
            self.ai_dots.append(dot)

        safe_w = self.size.w - 36
        gap = 7
        button_w = (safe_w - gap * 4) / 5.0
        start_x = self.size.w / 2.0 - (button_w * 5 + gap * 4) / 2.0 + button_w / 2.0
        button_y = self.top_y - 18
        specs = [
            ('mode', '模式:AI', '#3d6f8f'),
            ('difficulty', '难度:中', '#527a49'),
            ('music', '音乐:开', '#8b6b3d'),
            ('undo', '悔棋', '#b66b2d'),
            ('restart', '重开', '#8e3f39'),
        ]
        for index, (key, text, color) in enumerate(specs):
            center = (start_x + index * (button_w + gap), button_y)
            self.buttons[key] = self._create_button(key, text, center, (button_w, 34), color)

        self.ui_nodes = [title, subtitle, self.status_label, self.info_label, self.red_capture_label, self.black_capture_label]

    def _create_button(self, key, text, center, size, fill_color):
        width, height = size
        root = scene.Node(position=center, parent=self.ui_root, z_position=21)
        bg = scene.ShapeNode(
            path=ui.Path.rounded_rect(0, 0, width, height, 12),
            fill_color=fill_color,
            stroke_color='#f7ddb2',
            line_width=1.5,
            position=(0, 0),
            parent=root,
            shadow=('#00000033', 0, -2, 4),
        )
        label = scene.LabelNode(
            text,
            font=('Helvetica-Bold', 12),
            color='white',
            position=(0, 0),
            parent=root,
            z_position=2,
        )
        return {'root': root, 'bg': bg, 'label': label, 'size': size, 'key': key}

    def play_effect(self, name, volume=0.6, pitch=1.0, looping=False):
        try:
            return sound.play_effect(name, volume=volume, pitch=pitch, looping=looping)
        except TypeError:
            try:
                return sound.play_effect(name, volume=volume, pitch=pitch)
            except Exception:
                return None
        except Exception:
            return None

    def start_music(self):
        if not self.music_on:
            return
        if self.music_handle or self.music_player:
            return
        self.music_handle = self.play_effect('music:Bonus_NES_1', volume=0.12, pitch=0.82, looping=True)
        if self.music_handle:
            return
        try:
            file_dir = os.path.dirname(__file__) if '__file__' in globals() else os.getcwd()
            music_path = os.path.abspath(os.path.join(file_dir, '..', 'Sounds', 'music', 'Bonus_NES_1.wav'))
            if os.path.exists(music_path):
                self.music_player = sound.Player(music_path)
                self.music_player.number_of_loops = -1
                self.music_player.volume = 0.12
                self.music_player.play()
        except Exception:
            self.music_player = None

    def stop_music(self):
        if self.music_handle:
            try:
                sound.stop_effect(self.music_handle)
            except Exception:
                pass
            self.music_handle = None
        if self.music_player:
            try:
                self.music_player.stop()
            except Exception:
                pass
            self.music_player = None

    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            self.start_music()
            self.play_effect('ui:switch1', volume=0.5)
        else:
            self.play_effect('ui:switch2', volume=0.45)
            self.stop_music()
        self.refresh_labels()

    def get_difficulty_label(self):
        for code, label in self.difficulties:
            if code == self.difficulty:
                return label
        return '中等'

    def cycle_difficulty(self):
        codes = [item[0] for item in self.difficulties]
        index = (codes.index(self.difficulty) + 1) % len(codes)
        self.difficulty = codes[index]
        if self.difficulty == 'easy':
            self.ai_wait = 0.75
        elif self.difficulty == 'medium':
            self.ai_wait = 0.45
        else:
            self.ai_wait = 0.28
        self.play_effect('ui:click1', volume=0.45)
        if self.ai_thinking:
            self.stop_ai_thinking()
            if self.vs_bot and not self.game_over and self.engine.turn == AI_SIDE:
                self.start_ai_thinking()
        self.refresh_labels()

    def update(self):
        if self.ai_thinking and not self.game_over:
            self.ai_timer += self.dt
            active = int((self.ai_timer * 6) % 3)
            for index, dot in enumerate(self.ai_dots):
                dot.alpha = 1.0 if index == active else 0.28
                dot.scale = 1.15 if index == active else 1.0
            if self.ai_timer >= self.ai_wait:
                self.run_ai_turn()

    def touch_began(self, touch):
        button = self.button_at_point(touch.location)
        if button:
            self.handle_button(button)
            return

        if self.game_over or self.ai_thinking or self.animating:
            return

        row, col = self.point_to_cell(touch.location)
        if row is None:
            if self.selected_square:
                self.clear_selection()
                self.play_effect('ui:click3', volume=0.3)
            return

        if self.selected_square:
            for move in self.selected_moves:
                if (move[2], move[3]) == (row, col):
                    self.apply_move(move, by_ai=False)
                    return

        piece = self.engine.board[row][col]
        if not piece:
            if self.selected_square:
                self.play_effect('game:Error_3', volume=0.28)
            return

        if self.vs_bot and self.engine.turn == AI_SIDE:
            return
        if piece[0] != self.engine.turn:
            self.play_effect('game:Error_3', volume=0.28)
            return

        if self.selected_square == (row, col):
            self.clear_selection()
            self.play_effect('ui:click3', volume=0.3)
            return

        self.select_square(row, col)
        self.play_effect('ui:click2', volume=0.45)

    def button_at_point(self, point):
        for key, button in self.buttons.items():
            center_x = button['root'].position.x
            center_y = button['root'].position.y
            width, height = button['size']
            if abs(point.x - center_x) <= width / 2 and abs(point.y - center_y) <= height / 2:
                return key
        return None

    def handle_button(self, key):
        if self.animating:
            return
        if key == 'mode':
            self.vs_bot = not self.vs_bot
            self.play_effect('ui:switch1', volume=0.5)
            self.reset_match()
            return
        if key == 'difficulty':
            self.cycle_difficulty()
            return
        if key == 'music':
            self.toggle_music()
            return
        if key == 'undo':
            self.undo_turn()
            return
        if key == 'restart':
            self.play_effect('ui:click1', volume=0.5)
            self.reset_match()

    def reset_match(self):
        if self.animating:
            return
        self.stop_ai_thinking()
        self._clear_nodes(self.animation_nodes)
        self.engine.reset()
        self.game_over = False
        self.winner = None
        self.selected_square = None
        self.selected_moves = []
        self.last_ai_summary = ''
        self.refresh_dynamic_nodes()
        self.refresh_labels()

    def undo_turn(self):
        if self.animating:
            return
        if not self.engine.history:
            self.play_effect('game:Error_3', volume=0.3)
            return

        self.stop_ai_thinking()
        steps = 1
        if self.vs_bot and self.engine.turn == HUMAN_SIDE and len(self.engine.history) >= 2:
            steps = 2
        undone = 0
        for _ in range(steps):
            if self.engine.undo_move():
                undone += 1
        if undone == 0:
            self.play_effect('game:Error_3', volume=0.3)
            return

        self.game_over = False
        self.winner = None
        self.selected_square = None
        self.selected_moves = []
        self.last_ai_summary = ''
        self.refresh_dynamic_nodes()
        self.refresh_labels()
        self.play_effect('ui:click3', volume=0.45)

    def select_square(self, row, col):
        self.selected_square = (row, col)
        self.selected_moves = self.engine.legal_targets_from(row, col)
        if not self.selected_moves:
            self.selected_square = None
            self.play_effect('game:Error_3', volume=0.3)
        self.refresh_dynamic_nodes()
        self.refresh_labels()

    def clear_selection(self):
        self.selected_square = None
        self.selected_moves = []
        self.refresh_dynamic_nodes()
        self.refresh_labels()

    def start_ai_thinking(self):
        if self.game_over or self.engine.turn != AI_SIDE:
            return
        self.ai_thinking = True
        self.ai_timer = 0.0
        self.refresh_labels()

    def stop_ai_thinking(self):
        self.ai_thinking = False
        self.ai_timer = 0.0
        for dot in self.ai_dots:
            dot.alpha = 0.0
            dot.scale = 1.0
        self.refresh_labels()

    def run_ai_turn(self):
        if not self.vs_bot or self.game_over or self.engine.turn != AI_SIDE:
            self.stop_ai_thinking()
            return
        move = self.ai.choose_move(AI_SIDE, self.difficulty)
        self.stop_ai_thinking()
        if move is None:
            self.finish_game(self.engine.current_winner() or HUMAN_SIDE)
            return
        self.last_ai_summary = 'AI 深度 {} · 搜索 {} 节点'.format(self.ai.last_depth, self.ai.last_nodes)
        self.apply_move(move, by_ai=True)

    def apply_move(self, move, by_ai=False):
        if self.animating:
            return
        self.animating = True
        self.selected_square = None
        self.selected_moves = []
        self.refresh_labels()
        self._clear_nodes(self.selection_nodes)
        self._clear_nodes(self.target_nodes)
        self._clear_nodes(self.check_nodes)
        self._clear_nodes(self.last_move_nodes)
        self._clear_nodes(self.piece_nodes)

        hidden = {(move[0], move[1]), (move[2], move[3])}
        self._draw_pieces(exclude_positions=hidden)
        self._animate_move(move, by_ai)

    def finish_game(self, winner):
        self.game_over = True
        self.winner = winner
        self.stop_ai_thinking()
        self.refresh_dynamic_nodes()
        self.refresh_labels()
        if winner == HUMAN_SIDE:
            self.play_effect('music:Victory_NES_1', volume=0.8)
        elif winner == AI_SIDE:
            self.play_effect('music:GameOver_NES_1', volume=0.8)
        else:
            self.play_effect('music:LevelUp_NES_1', volume=0.6)

    def refresh_dynamic_nodes(self):
        self._clear_nodes(self.animation_nodes)
        self._clear_nodes(self.piece_nodes)
        self._clear_nodes(self.last_move_nodes)
        self._clear_nodes(self.selection_nodes)
        self._clear_nodes(self.target_nodes)
        self._clear_nodes(self.check_nodes)

        self._draw_last_move_fx()
        self._draw_pieces()
        self._draw_selection_fx()
        self._draw_check_fx()

    def _draw_pieces(self, exclude_positions=None):
        exclude_positions = exclude_positions or set()
        last_move = self.engine.history[-1] if self.engine.history else None
        last_target = (last_move[2], last_move[3]) if last_move else None
        checked_king = self.engine.king_pos[self.engine.turn] if not self.game_over and self.engine.is_in_check(self.engine.turn) else None

        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if (row, col) in exclude_positions:
                    continue
                piece = self.engine.board[row][col]
                if not piece:
                    continue
                x, y = self.board_point(row, col)
                root = self._create_piece_node(
                    piece,
                    x,
                    y,
                    parent=self.piece_root,
                    last_target=last_target == (row, col),
                    checked=checked_king == (row, col),
                )
                self.piece_nodes.append(root)

    def _create_piece_node(self, piece, x, y, parent=None, last_target=False, checked=False):
        parent = parent or self.piece_root
        root = scene.Node(position=(x, y), parent=parent)
        radius = self.cell * 0.86
        shadow = scene.ShapeNode(
            path=('oval', -radius / 2, -radius / 2, radius, radius),
            fill_color='#00000033',
            stroke_color='#00000000',
            position=(1.6, -2.0),
            parent=root,
        )
        outer = scene.ShapeNode(
            path=('oval', -radius / 2, -radius / 2, radius, radius),
            fill_color='#f2d9a7',
            stroke_color='#8c5b2a',
            line_width=2.5,
            position=(0, 0),
            parent=root,
        )
        inner_radius = radius * 0.78
        inner = scene.ShapeNode(
            path=('oval', -inner_radius / 2, -inner_radius / 2, inner_radius, inner_radius),
            fill_color='#fff7e4',
            stroke_color='#c44739' if piece[0] == 'r' else '#2a2d34',
            line_width=1.7,
            position=(0, 0),
            parent=root,
        )
        label = scene.LabelNode(
            PIECE_TEXT[piece],
            font=('Helvetica-Bold', max(16, self.cell * 0.46)),
            color='#cc4134' if piece[0] == 'r' else '#1e2630',
            position=(0, 0),
            parent=root,
            z_position=3,
        )
        if last_target:
            outer.stroke_color = '#ffd86b'
            outer.line_width = 3.0
            root.scale = 1.03
        if checked:
            inner.stroke_color = '#ff5f57'
            inner.line_width = 2.3
        return root

    def _animate_move(self, move, by_ai):
        from_x, from_y = self.board_point(move[0], move[1])
        to_x, to_y = self.board_point(move[2], move[3])
        move_duration = 0.18 if move[5] else 0.16

        moving = self._create_piece_node(move[4], from_x, from_y, parent=self.fx_root)
        moving.z_position = 40
        moving.scale = 1.05
        self.animation_nodes.append(moving)

        if move[5]:
            captured = self._create_piece_node(move[5], to_x, to_y, parent=self.fx_root)
            captured.z_position = 35
            captured.run_action(scene.Action.sequence(
                scene.Action.group(
                    scene.Action.scale_to(0.72, move_duration * 0.8),
                    scene.Action.fade_to(0.0, move_duration * 0.8),
                ),
                scene.Action.remove(),
            ))
            self.animation_nodes.append(captured)

        def finish():
            self._complete_move(move, by_ai)

        moving.run_action(scene.Action.sequence(
            scene.Action.group(
                scene.Action.move_to(to_x, to_y, move_duration),
                scene.Action.scale_to(1.1, move_duration * 0.75),
            ),
            scene.Action.scale_to(1.0, 0.05),
            scene.Action.call(finish, scene=self),
        ))

    def _complete_move(self, move, by_ai):
        captured = move[5]
        self._clear_nodes(self.animation_nodes)
        self.engine.make_move(move, store_history=True)
        self.animating = False
        self.refresh_dynamic_nodes()

        winner = self.engine.current_winner()
        if winner:
            self.finish_game(winner)
            return

        if captured:
            self.play_effect('game:Hit_2', volume=0.58, pitch=0.98 if by_ai else 1.05)
        else:
            self.play_effect('casino:CardPlace1', volume=0.5, pitch=0.98 if by_ai else 1.03)

        if self.engine.is_in_check(self.engine.turn):
            self.play_effect('game:Question_1', volume=0.6, pitch=1.08)

        self.refresh_labels()
        if self.vs_bot and self.engine.turn == AI_SIDE:
            self.start_ai_thinking()

    def _draw_last_move_fx(self):
        if not self.engine.history:
            return
        move = self.engine.history[-1]
        from_x, from_y = self.board_point(move[0], move[1])
        to_x, to_y = self.board_point(move[2], move[3])
        line = scene.ShapeNode(
            path=('line', from_x, from_y, to_x, to_y),
            fill_color='#00000000',
            stroke_color='#ffd86b66',
            line_width=4,
            parent=self.fx_root,
        )
        start_dot = scene.ShapeNode(
            path=('oval', -6, -6, 12, 12),
            fill_color='#ffd86b66',
            stroke_color='#00000000',
            position=(from_x, from_y),
            parent=self.fx_root,
        )
        end_ring = scene.ShapeNode(
            path=('oval', -self.cell * 0.28, -self.cell * 0.28, self.cell * 0.56, self.cell * 0.56),
            fill_color='#00000000',
            stroke_color='#ffd86bcc',
            line_width=2.5,
            position=(to_x, to_y),
            parent=self.fx_root,
        )
        self.last_move_nodes.extend([line, start_dot, end_ring])

    def _draw_selection_fx(self):
        if not self.selected_square:
            return

        row, col = self.selected_square
        x, y = self.board_point(row, col)
        ring = scene.ShapeNode(
            path=('oval', -self.cell * 0.47, -self.cell * 0.47, self.cell * 0.94, self.cell * 0.94),
            fill_color='#00000000',
            stroke_color='#47d7ff',
            line_width=3,
            position=(x, y),
            parent=self.fx_root,
        )
        ring.run_action(scene.Action.repeat_forever(scene.Action.sequence(
            scene.Action.scale_to(1.06, 0.55),
            scene.Action.scale_to(1.0, 0.55),
        )))
        self.selection_nodes.append(ring)

        for move in self.selected_moves:
            target_x, target_y = self.board_point(move[2], move[3])
            if move[5]:
                marker = scene.ShapeNode(
                    path=('oval', -self.cell * 0.33, -self.cell * 0.33, self.cell * 0.66, self.cell * 0.66),
                    fill_color='#00000000',
                    stroke_color='#ff8f6b',
                    line_width=2.6,
                    position=(target_x, target_y),
                    parent=self.fx_root,
                )
            else:
                size = self.cell * 0.22
                marker = scene.ShapeNode(
                    path=('oval', -size / 2, -size / 2, size, size),
                    fill_color='#4be17d',
                    stroke_color='#00000000',
                    position=(target_x, target_y),
                    parent=self.fx_root,
                )
                marker.alpha = 0.82
            self.target_nodes.append(marker)

    def _draw_check_fx(self):
        if self.game_over or not self.engine.is_in_check(self.engine.turn):
            return
        king = self.engine.king_pos[self.engine.turn]
        if king is None:
            return
        x, y = self.board_point(*king)
        ring = scene.ShapeNode(
            path=('oval', -self.cell * 0.52, -self.cell * 0.52, self.cell * 1.04, self.cell * 1.04),
            fill_color='#00000000',
            stroke_color='#ff5f57',
            line_width=3,
            position=(x, y),
            parent=self.fx_root,
        )
        ring.alpha = 0.9
        ring.run_action(scene.Action.repeat_forever(scene.Action.sequence(
            scene.Action.fade_to(0.35, 0.45),
            scene.Action.fade_to(0.9, 0.45),
        )))
        self.check_nodes.append(ring)

    def _captured_text(self, captor_color):
        target_color = self.engine.other(captor_color)
        counts = {}
        for row in self.engine.board:
            for piece in row:
                if piece:
                    counts[piece] = counts.get(piece, 0) + 1

        missing = []
        for kind in ('R', 'H', 'C', 'A', 'E', 'P'):
            piece_code = target_color + kind
            remaining = counts.get(piece_code, 0)
            total = INITIAL_COUNTS[piece_code]
            missing.extend([PIECE_TEXT[piece_code]] * max(0, total - remaining))
        return ''.join(missing) if missing else '无'

    def refresh_labels(self):
        mode_text = '模式:AI' if self.vs_bot else '模式:双人'
        diff_map = {'easy': '难度:简', 'medium': '难度:中', 'hard': '难度:难'}
        music_text = '音乐:开' if self.music_on else '音乐:关'
        self.buttons['mode']['label'].text = mode_text
        self.buttons['difficulty']['label'].text = diff_map[self.difficulty]
        self.buttons['music']['label'].text = music_text
        self.buttons['undo']['label'].text = '悔棋'
        self.buttons['restart']['label'].text = '重开'

        self.red_capture_label.text = '红方战果: {}'.format(self._captured_text('r'))
        self.black_capture_label.text = '黑方战果: {}'.format(self._captured_text('b'))

        if self.animating:
            self.status_label.text = '落子中'
            self.info_label.text = '棋子正在走位，不再是瞬移了'
            return

        if self.game_over:
            if self.winner == 'r':
                self.status_label.text = '红方胜利'
                self.info_label.text = '这局你下得很稳，点“重开”再来一盘'
            elif self.winner == 'b':
                self.status_label.text = '黑方胜利'
                self.info_label.text = 'AI 拿下了这局，悔棋或者重开都可以'
            else:
                self.status_label.text = '双方和棋'
                self.info_label.text = '局面锁死了，来一局新的更刺激'
            return

        if self.ai_thinking:
            self.status_label.text = 'AI 思考中'
            self.info_label.text = '难度 {} · 黑方正在推演下一步'.format(self.get_difficulty_label())
            return

        in_check = self.engine.is_in_check(self.engine.turn)
        if self.vs_bot:
            if self.engine.turn == HUMAN_SIDE:
                self.status_label.text = '将军！你的回合' if in_check else '你的回合'
                if self.selected_square:
                    piece = self.engine.board[self.selected_square[0]][self.selected_square[1]]
                    self.info_label.text = '已选 {} · 可走 {} 步'.format(PIECE_TEXT[piece], len(self.selected_moves))
                elif self.last_ai_summary:
                    self.info_label.text = self.last_ai_summary
                else:
                    self.info_label.text = '你执红先行，点棋子再点落点'
            else:
                self.status_label.text = '将军！AI 回合' if in_check else 'AI 回合'
                self.info_label.text = '黑方已接管棋局'
        else:
            side_text = '红方回合' if self.engine.turn == HUMAN_SIDE else '黑方回合'
            self.status_label.text = '将军！' + side_text if in_check else side_text
            if self.selected_square:
                piece = self.engine.board[self.selected_square[0]][self.selected_square[1]]
                self.info_label.text = '已选 {} · 可走 {} 步'.format(PIECE_TEXT[piece], len(self.selected_moves))
            else:
                self.info_label.text = '双人同屏对弈，轮流落子'

    def _clear_nodes(self, nodes):
        while nodes:
            node = nodes.pop()
            try:
                node.remove_from_parent()
            except Exception:
                pass


if __name__ == '__main__':
    scene.run(XiangqiArena(), show_fps=False, frame_interval=1)
