import scene
import ui
import random

class GomokuGame(scene.Scene):
    def setup(self):
        # 游戏配置
        self.board_size = 15
        self.cell_size = min(self.size.w, self.size.h) / (self.board_size + 2)
        self.board_offset_x = (self.size.w - self.cell_size * (self.board_size - 1)) / 2
        self.board_offset_y = (self.size.h - self.cell_size * (self.board_size - 1)) / 2
        
        # 游戏状态
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.vs_bot = False
        
        # AI 思考状态
        self.ai_thinking = False
        self.ai_think_timer = 0
        self.ai_think_duration = 0.8
        
        # 难度设置：easy/medium/hard
        self.difficulty = "medium"
        self.difficulties = [("easy", "简单"), ("medium", "中等"), ("hard", "困难")]
        
        # 背景
        self.background_color = '#8B4513'
        
        # 创建棋盘背景
        board_w = self.cell_size * (self.board_size - 1) + 40
        board_h = self.cell_size * (self.board_size - 1) + 40
        with ui.ImageContext(int(board_w), int(board_h)) as ctx:
            ui.set_color('#d2b48c')
            ui.fill_rect(0, 0, board_w, board_h)
            board_texture = ctx.get_image()
        self.board_bg = scene.SpriteNode(
            scene.Texture(board_texture),
            size=(board_w, board_h),
            position=self.size/2,
            parent=self,
            z_position=0
        )
        
        self.draw_board_lines()
        self.draw_star_points()
        
        self.stones = []
        
        insets = self.safe_area_insets
        
        # 状态标签
        self.status_label = scene.LabelNode(
            '黑棋回合',
            font=('Helvetica', 20),
            color='white',
            position=(self.size.w/2, insets.bottom + 30),
            parent=self
        )
        
        # AI 思考指示器
        self.ai_dots = []
        dot_spacing = 25
        for i in range(3):
            dot = scene.ShapeNode(
                path=('oval', -5, -5, 10, 10),
                fill_color='#00FFFF',
                position=(self.size.w/2 - dot_spacing + i * dot_spacing, insets.bottom + 70),
                parent=self,
                z_position=20,
                alpha=0.0  # 初始隐藏
            )
            self.ai_dots.append(dot)
        
        # 顶部按钮区域
        top_y = self.size.h - insets.top - 30
        
        # 难度按钮（左侧）
        self.difficulty_btn = scene.LabelNode(
            '难度:中等',
            font=('Helvetica', 16),
            color='#90EE90',
            position=(self.size.w/2 - 130, top_y),
            parent=self
        )
        
        # 人机对战按钮（中间）
        self.bot_btn = scene.LabelNode(
            '人机对战',
            font=('Helvetica', 16),
            color='#00BFFF',
            position=(self.size.w/2, top_y),
            parent=self
        )
        
        # 重新开始按钮（右侧）
        self.restart_btn = scene.LabelNode(
            '重新开始',
            font=('Helvetica', 16),
            color='#FFD700',
            position=(self.size.w/2 + 130, top_y),
            parent=self
        )
    
    def draw_board_lines(self):
        line_color = '#333333'
        board_end = self.cell_size * (self.board_size - 1)
        
        for i in range(self.board_size):
            y = self.board_offset_y + i * self.cell_size
            line = scene.ShapeNode(
                path=('rect', -board_end/2, -0.5, board_end, 1),
                fill_color=line_color,
                stroke_color=line_color,
                position=(self.size.w/2, y),
                parent=self,
                z_position=1
            )
        
        for i in range(self.board_size):
            x = self.board_offset_x + i * self.cell_size
            line = scene.ShapeNode(
                path=('rect', -0.5, -board_end/2, 1, board_end),
                fill_color=line_color,
                stroke_color=line_color,
                position=(x, self.size.h/2),
                parent=self,
                z_position=1
            )
    
    def draw_star_points(self):
        star_positions = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        star_size = self.cell_size * 0.2
        for row, col in star_positions:
            x = self.board_offset_x + col * self.cell_size
            y = self.board_offset_y + row * self.cell_size
            star = scene.ShapeNode(
                path=('oval', -star_size/2, -star_size/2, star_size, star_size),
                fill_color='#333333',
                position=(x, y),
                parent=self,
                z_position=2
            )
    
    def update(self):
        # AI 思考动画和自动落子
        if self.ai_thinking and not self.game_over:
            self.ai_think_timer += self.dt
            
            # 动画效果
            period = 0.4
            active_index = int((self.ai_think_timer % (period * 3)) / period)
            
            for i, dot in enumerate(self.ai_dots):
                if i == active_index:
                    dot.alpha = 1.0
                    dot.scale = 1.2
                else:
                    dot.alpha = 0.3
                    dot.scale = 1.0
            
            # 思考时间到，执行落子
            if self.ai_think_timer >= self.ai_think_duration:
                # 确保还在人机模式且轮到AI
                if self.vs_bot and self.current_player == 2 and not self.game_over:
                    self.ai_place_stone()
                else:
                    # 状态不对，停止思考
                    self.stop_ai_thinking()
    
    def touch_began(self, touch):
        # 检查按钮点击 - 重新开始
        if self.restart_btn.frame.contains_point(touch.location):
            self.restart_game()
            return
        
        # 检查按钮点击 - 切换人机模式
        if self.bot_btn.frame.contains_point(touch.location):
            self.vs_bot = not self.vs_bot
            self.restart_game()
            return
        
        # 检查按钮点击 - 切换难度
        if self.difficulty_btn.frame.contains_point(touch.location):
            self.cycle_difficulty()
            return
        
        # 游戏结束或AI思考中时，忽略棋盘点击
        if self.game_over or self.ai_thinking:
            return
        
        # 人机模式下，只有玩家回合（黑棋）可以下棋
        if self.vs_bot and self.current_player == 2:
            return
        
        # 计算点击位置
        col = round((touch.location.x - self.board_offset_x) / self.cell_size)
        row = round((touch.location.y - self.board_offset_y) / self.cell_size)
        
        # 检查边界
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return
        
        # 检查位置是否已被占用
        if self.board[row][col] != 0:
            return
        
        # 玩家落子
        self.place_stone(row, col)
        
        # 人机模式下，玩家下完后启动AI思考
        if self.vs_bot and not self.game_over and self.current_player == 2:
            self.start_ai_thinking()
    
    def cycle_difficulty(self):
        """循环切换难度"""
        # 切换难度时停止AI思考
        self.stop_ai_thinking()
        
        current_idx = [d[0] for d in self.difficulties].index(self.difficulty)
        next_idx = (current_idx + 1) % 3
        self.difficulty, label_text = self.difficulties[next_idx]
        self.difficulty_btn.text = f'难度:{label_text}'
        
        # 根据难度调整AI思考时间
        if self.difficulty == "easy":
            self.ai_think_duration = 1.2
        elif self.difficulty == "medium":
            self.ai_think_duration = 0.6
        else:  # hard
            self.ai_think_duration = 0.3
        
        # 显示提示，然后恢复状态显示
        if self.vs_bot:
            status = '你回合（黑棋）' if self.current_player == 1 else f'AI 思考中 [{label_text}]'
        else:
            status = '黑棋回合' if self.current_player == 1 else '白棋回合'
        self.status_label.text = f'难度:{label_text} | {status}'
    
    def start_ai_thinking(self):
        """启动AI思考状态"""
        # 安全检查
        if self.game_over or self.current_player != 2:
            return
            
        self.ai_thinking = True
        self.ai_think_timer = 0
        
        difficulty_label = self.get_difficulty_label()
        self.status_label.text = f'AI 思考中 [{difficulty_label}]'
        
        # 显示思考指示器
        for dot in self.ai_dots:
            dot.alpha = 0.5
    
    def get_difficulty_label(self):
        """获取当前难度的中文标签"""
        for code, label in self.difficulties:
            if code == self.difficulty:
                return label
        return "中等"
    
    def ai_place_stone(self):
        """AI执行落子"""
        # 安全检查
        if self.game_over or self.current_player != 2:
            self.stop_ai_thinking()
            return
        
        try:
            row, col = self.get_ai_move()
            
            # 验证返回的位置有效
            if row is None or col is None:
                self.stop_ai_thinking()
                return
                
            if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
                self.stop_ai_thinking()
                return
                
            if self.board[row][col] != 0:
                # 位置被占，找第一个空位（备用方案）
                found = False
                for r in range(self.board_size):
                    for c in range(self.board_size):
                        if self.board[r][c] == 0:
                            row, col = r, c
                            found = True
                            break
                    if found:
                        break
                if not found:
                    self.stop_ai_thinking()
                    return
            
            self.stop_ai_thinking()
            self.place_stone(row, col)
            
        except Exception as e:
            # 发生错误，停止思考
            self.stop_ai_thinking()
            print(f"AI Error: {e}")
    
    def stop_ai_thinking(self):
        """停止AI思考状态"""
        self.ai_thinking = False
        self.ai_think_timer = 0
        
        # 隐藏思考指示器
        for dot in self.ai_dots:
            dot.alpha = 0.0
            dot.scale = 1.0
    
    def get_ai_move(self):
        """AI选择最优位置"""
        # 第一步下天元
        if self.is_first_move():
            return (7, 7)
        
        # 第二步策略
        if self.is_second_move():
            return self.get_second_move()
        
        # 收集所有可下位置
        candidates = []
        
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] == 0:
                    attack_score = self.evaluate_position(r, c, 2)
                    defense_score = self.evaluate_position(r, c, 1)
                    
                    # 根据难度调整权重
                    if self.difficulty == "easy":
                        total_score = attack_score * 0.9 + defense_score * 0.8
                    elif self.difficulty == "hard":
                        total_score = attack_score * 1.2 + defense_score * 1.1
                    else:
                        total_score = attack_score * 1.1 + defense_score
                    
                    # 必胜或必守
                    if attack_score >= 100000:
                        total_score = 1000000
                    elif defense_score >= 100000:
                        total_score = 900000
                    
                    candidates.append((r, c, total_score))
        
        # 没有可下位置
        if not candidates:
            return (7, 7)
        
        # 根据难度决定是否失误
        if self.difficulty == "easy" and len(candidates) > 1:
            if random.random() < 0.3:
                candidates.sort(key=lambda x: x[2], reverse=True)
                top_n = min(3, len(candidates))
                choice = random.choice(candidates[:top_n])
                return (choice[0], choice[1])
        
        elif self.difficulty == "medium" and len(candidates) > 1:
            if random.random() < 0.1:
                candidates.sort(key=lambda x: x[2], reverse=True)
                top_n = min(2, len(candidates))
                choice = random.choice(candidates[:top_n])
                return (choice[0], choice[1])
        
        # 选择最优位置
        candidates.sort(key=lambda x: x[2], reverse=True)
        
        best_score = candidates[0][2]
        best_candidates = [c for c in candidates if c[2] >= best_score - 100]
        
        if len(best_candidates) > 1:
            best_candidates.sort(key=lambda x: self.get_distance_to_nearest_stone(x[0], x[1]))
        
        best = best_candidates[0]
        return (best[0], best[1])
    
    def is_first_move(self):
        """检查是否是第一步"""
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] != 0:
                    return False
        return True
    
    def is_second_move(self):
        """检查是否是第二步"""
        count = 0
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] != 0:
                    count += 1
                    if count > 1:
                        return False
        return count == 1
    
    def get_second_move(self):
        """第二步策略"""
        # 找到第一颗棋子
        first_r, first_c = 7, 7
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] != 0:
                    first_r, first_c = r, c
                    break
        
        # 如果第一颗不在中心，下天元
        if not (6 <= first_r <= 8 and 6 <= first_c <= 8):
            if self.board[7][7] == 0:
                return (7, 7)
        
        # 选择附近的星位
        star_positions = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for sr, sc in star_positions:
            if self.board[sr][sc] == 0:
                dist = abs(sr - first_r) + abs(sc - first_c)
                if dist <= 5:
                    return (sr, sc)
        
        # 默认下天元或附近
        if self.board[7][7] == 0:
            return (7, 7)
        return (6, 6) if self.board[6][6] == 0 else (8, 8)
    
    def get_distance_to_nearest_stone(self, row, col):
        """计算到最近棋子的距离"""
        min_dist = float('inf')
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] != 0:
                    dist = abs(r - row) + abs(c - col)
                    min_dist = min(min_dist, dist)
        return min_dist if min_dist != float('inf') else 0
    
    def evaluate_position(self, row, col, player):
        """评估位置价值"""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        # 简单模式随机忽略一个方向
        if self.difficulty == "easy" and len(directions) > 1:
            directions = random.sample(directions, 3)
        
        for dr, dc in directions:
            line_info = self.analyze_line(row, col, dr, dc, player)
            score += self.calculate_pattern_score(line_info)
        
        # 困难模式增加密度评估
        if self.difficulty == "hard":
            score += self.evaluate_density(row, col, player) * 10
        
        return score
    
    def evaluate_density(self, row, col, player):
        """评估周围棋子密度"""
        count = 0
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < self.board_size and 0 <= c < self.board_size:
                    if self.board[r][c] == player:
                        count += 1
        return count
    
    def analyze_line(self, row, col, dr, dc, player):
        """分析某条线上的棋型"""
        # 正向
        count_forward = 0
        r, c = row + dr, col + dc
        while 0 <= r < self.board_size and 0 <= c < self.board_size:
            if self.board[r][c] == player:
                count_forward += 1
                r += dr
                c += dc
            else:
                break
        
        forward_end = 1 if (0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == 0) else 0
        
        # 反向
        count_backward = 0
        r, c = row - dr, col - dc
        while 0 <= r < self.board_size and 0 <= c < self.board_size:
            if self.board[r][c] == player:
                count_backward += 1
                r -= dr
                c -= dc
            else:
                break
        
        backward_end = 1 if (0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == 0) else 0
        
        total_count = count_forward + 1 + count_backward
        return (total_count, backward_end, forward_end)
    
    def calculate_pattern_score(self, line_info):
        """根据棋型计算分数"""
        count, left_end, right_end = line_info
        
        if count >= 5:
            return 100000
        if count == 4 and left_end == 1 and right_end == 1:
            return 50000
        if count == 4:
            return 10000
        if count == 3 and left_end == 1 and right_end == 1:
            return 5000
        if count == 3:
            return 800
        if count == 2 and left_end == 1 and right_end == 1:
            return 500
        if count == 2:
            return 100
        if count == 1 and left_end == 1 and right_end == 1:
            return 10
        return 0
    
    def place_stone(self, row, col):
        """放置棋子"""
        self.board[row][col] = self.current_player
        self.last_move = (row, col)
        
        x = self.board_offset_x + col * self.cell_size
        y = self.board_offset_y + row * self.cell_size
        
        color = 'black' if self.current_player == 1 else 'white'
        stone_size = self.cell_size * 0.85
        stone = scene.ShapeNode(
            path=('oval', -stone_size/2, -stone_size/2, stone_size, stone_size),
            fill_color=color,
            stroke_color='#333333',
            line_width=1.5,
            position=(x, y),
            parent=self,
            z_position=10
        )
        self.stones.append(stone)
        
        # 最后落子标记
        if hasattr(self, 'last_move_marker'):
            self.last_move_marker.remove_from_parent()
        marker_size = self.cell_size * 0.15
        self.last_move_marker = scene.ShapeNode(
            path=('oval', -marker_size/2, -marker_size/2, marker_size, marker_size),
            fill_color='#FF4444',
            position=(x, y),
            parent=self,
            z_position=11
        )
        
        # 检查胜负
        if self.check_winner(row, col):
            self.game_over = True
            self.winner = self.current_player
            self.stop_ai_thinking()
            if self.vs_bot:
                winner_text = '你赢了！' if self.winner == 1 else 'AI 获胜！'
            else:
                winner_text = '黑棋获胜！' if self.winner == 1 else '白棋获胜！'
            self.status_label.text = winner_text
        elif self.is_board_full():
            self.game_over = True
            self.stop_ai_thinking()
            self.status_label.text = '平局！'
        else:
            # 切换玩家
            self.current_player = 3 - self.current_player
            self.update_status_label()
    
    def update_status_label(self):
        """更新状态标签"""
        if self.vs_bot:
            if self.current_player == 1:
                self.status_label.text = f'你回合（黑棋） [{self.get_difficulty_label()}]'
            else:
                self.status_label.text = f'AI 思考中 [{self.get_difficulty_label()}]'
        else:
            self.status_label.text = '黑棋回合' if self.current_player == 1 else '白棋回合'
    
    def check_winner(self, row, col):
        """检查是否有玩家获胜"""
        player = self.board[row][col]
        directions = [
            [(0, 1), (0, -1)],
            [(1, 0), (-1, 0)],
            [(1, 1), (-1, -1)],
            [(1, -1), (-1, 1)]
        ]
        
        for direction in directions:
            count = 1
            
            dr, dc = direction[0]
            r, c = row + dr, col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            
            dr, dc = direction[1]
            r, c = row + dr, col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            
            if count >= 5:
                return True
        
        return False
    
    def is_board_full(self):
        """检查棋盘是否已满"""
        for row in self.board:
            if 0 in row:
                return False
        return True
    
    def restart_game(self):
        """重新开始游戏"""
        # 停止AI思考
        self.stop_ai_thinking()
        
        # 清除棋子
        for stone in self.stones:
            stone.remove_from_parent()
        self.stones = []
        
        if hasattr(self, 'last_move_marker'):
            self.last_move_marker.remove_from_parent()
        
        # 重置游戏状态
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.last_move = None
        
        # 更新显示
        self.update_status_label()

scene.run(GomokuGame(), show_fps=False, frame_interval=1)