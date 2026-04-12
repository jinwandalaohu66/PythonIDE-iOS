import ui
import pygame
import random

# 只保留pygame核心逻辑，不初始化图形
pygame.init()

# 数字颜色（和原版一致）
COLORS = {
    1: '#0000FF',
    2: '#008000',
    3: '#FF0000',
    4: '#000080',
    5: '#800000',
    6: '#008080',
    7: '#000000',
    8: '#808080'
}

class MineLogic:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.reset()

    def reset(self):
        self.mine = [[0]*self.cols for _ in range(self.rows)]
        self.revealed = [[False]*self.cols for _ in range(self.rows)]
        self.flagged = [[False]*self.cols for _ in range(self.rows)]
        self.game_over = False
        self.win = False
        self.first = True
        self.mine_pos = set()

    def put_mines(self, ar, ac):
        while len(self.mine_pos) < self.mines:
            r = random.randint(0, self.rows-1)
            c = random.randint(0, self.cols-1)
            if (r,c) != (ar,ac):
                self.mine_pos.add((r,c))
        for r,c in self.mine_pos:
            self.mine[r][c] = -1
        self.calc_numbers()

    def calc_numbers(self):
        dirs = [(-1,-1),(-1,0),(-1,1),
                (0,-1),         (0,1),
                (1,-1), (1,0),(1,1)]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.mine[r][c] == -1: continue
                cnt = 0
                for dr,dc in dirs:
                    nr, nc = r+dr, c+dc
                    if 0<=nr<self.rows and 0<=nc<self.cols:
                        if self.mine[nr][nc] == -1:
                            cnt +=1
                self.mine[r][c] = cnt

    def reveal_cell(self, r, c):
        if self.game_over or self.flagged[r][c] or self.revealed[r][c]:
            return
        if self.first:
            self.put_mines(r,c)
            self.first = False
        if self.mine[r][c] == -1:
            self.game_over = True
            return
        self.revealed[r][c] = True
        # 递归展开0的格子（修复自动扩散逻辑）
        if self.mine[r][c] == 0:
            dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
            for dr,dc in dirs:
                nr, nc = r+dr, c+dc
                if 0<=nr<self.rows and 0<=nc<self.cols:
                    if not self.revealed[nr][nc]:
                        self.reveal_cell(nr, nc)
        self.check_win()

    def flag_cell(self, r, c):
        if self.game_over or self.revealed[r][c]:
            return
        self.flagged[r][c] = not self.flagged[r][c]

    def check_win(self):
        total = self.rows*self.cols - self.mines
        cnt = sum(row.count(True) for row in self.revealed)
        if cnt >= total:
            self.win = True
            self.game_over = True

    def mines_left(self):
        return self.mines - sum(row.count(True) for row in self.flagged)

class MineUI(ui.View):
    def __init__(self, r=9, c=9, m=10):
        self.g = MineLogic(r,c,m)
        self.cell = 26
        self.flag_mode = False  # 插旗开关
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.background_color = '#c0c0c0'
        self.name = '扫雷'
        w = self.g.cols * self.cell

        # 顶部栏
        top = ui.View(frame=(10,10,w,50))
        top.background_color = '#c0c0c0'
        top.border_width = 2
        top.border_color = '#808080'
        self.add_subview(top)

        # 雷数显示
        self.mine_lbl = ui.Label(frame=(10,10,60,30))
        self.mine_lbl.background_color = 'black'
        self.mine_lbl.text_color = 'red'
        self.mine_lbl.font = ('Courier',22)
        self.mine_lbl.alignment = ui.ALIGN_CENTER
        top.add_subview(self.mine_lbl)

        # 笑脸
        self.face = ui.Button(frame=(w//2-20,10,30,30))
        self.face.title = '😊'
        self.face.font = ('System',20)
        self.face.action = self.reset
        top.add_subview(self.face)

        # 插旗模式开关（解决长按不支持的问题）
        self.flag_btn = ui.Button(frame=(w-70,10,60,30))
        self.flag_btn.title = '🚩'
        self.flag_btn.font = ('System',20)
        self.flag_btn.action = self.toggle_flag_mode
        self.flag_btn.background_color = '#c0c0c0'
        self.flag_btn.border_width = 1
        self.flag_btn.border_color = '#808080'
        top.add_subview(self.flag_btn)

        # 棋盘
        board = ui.View(frame=(10,70, self.g.cols*self.cell, self.g.rows*self.cell))
        board.background_color = '#c0c0c0'
        board.border_width = 2
        board.border_color = '#808080'
        self.add_subview(board)

        self.btns = []
        for r in range(self.g.rows):
            row_btns = []
            for c in range(self.g.cols):
                btn = ui.Button(frame=(c*self.cell, r*self.cell, self.cell, self.cell))
                btn.tag = (r,c)
                btn.background_color = '#c0c0c0'
                btn.border_width = 1
                btn.border_color = '#808080'
                btn.font = ('System',14)
                btn.action = self.on_cell_click
                board.add_subview(btn)
                row_btns.append(btn)
            self.btns.append(row_btns)
        self.refresh()

    def toggle_flag_mode(self, sender):
        # 切换插旗模式
        self.flag_mode = not self.flag_mode
        sender.background_color = '#ff9999' if self.flag_mode else '#c0c0c0'

    def refresh(self):
        self.mine_lbl.text = f'{max(0, self.g.mines_left()):03d}'
        if self.g.win:
            self.face.title = '😎'
        elif self.g.game_over:
            self.face.title = '😵'
        else:
            self.face.title = '😊'

        for r in range(self.g.rows):
            for c in range(self.g.cols):
                b = self.btns[r][c]
                if self.g.flagged[r][c]:
                    b.title = '🚩'
                    b.background_color = '#c0c0c0'
                    continue
                if not self.g.revealed[r][c]:
                    b.title = ''
                    b.background_color = '#c0c0c0'
                    continue
                b.background_color = '#e0e0e0'
                v = self.g.mine[r][c]
                if v == -1:
                    b.title = '💣'
                elif v == 0:
                    b.title = ''
                else:
                    b.title = str(v)
                    b.text_color = COLORS[v]

    def on_cell_click(self, btn):
        r,c = btn.tag
        if self.flag_mode:
            # 插旗模式：点一下插旗/拔旗
            self.g.flag_cell(r,c)
        else:
            # 普通模式：点一下翻开，自动扩散
            self.g.reveal_cell(r,c)
        self.refresh()

    def reset(self, btn=None):
        self.g.reset()
        self.flag_mode = False
        self.flag_btn.background_color = '#c0c0c0'
        self.refresh()

class MenuUI(ui.View):
    def __init__(self):
        super().__init__()
        self.background_color = '#c0c0c0'
        self.frame = (0,0,280,300)
        self.name = '扫雷菜单'
        self.setup()

    def setup(self):
        def b(y, t, r, c, m):
            btn = ui.Button(frame=(40,y,200,40))
            btn.title = t
            btn.background_color = '#c0c0c0'
            btn.border_width = 2
            btn.border_color = '#808080'
            btn.action = lambda s: MineUI(r,c,m).present()
            self.add_subview(btn)
        b(40, '初级 9×9 10雷',9,9,10)
        b(90, '中级 16×16 40雷',16,16,40)
        b(140, '高级 16×30 99雷',16,30,99)

MenuUI().present()