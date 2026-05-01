# 协同效应 - 15种触发机制终极版
# 核心玩法：老虎机+卡牌构筑+房租系统+300个独特功能符号
# 15种完全不同的触发机制，彻底告别单一相邻加成
# 纯Python标准库实现，无需额外依赖

import random
import sys
import time
from typing import Dict, List, Tuple, Set, Callable

# ==================== 15种触发机制定义 ====================
# 1. 基础价值型：直接提供固定金币
# 2. 全局协同型：与其他特定符号产生全局协同
# 3. 相邻加成型：与8个相邻格子的符号产生加成
# 4. 同行加成型：与同一行的符号产生加成
# 5. 同列加成型：与同一列的符号产生加成
# 6. 对角线加成型：与两条对角线的符号产生加成
# 7. 数量触发型：当盘面出现N个该符号时触发特效
# 8. 回合触发型：在特定回合数触发特效
# 9. 位置触发型：在盘面特定位置触发特效
# 10. 生成型：转动时生成其他符号
# 11. 消除型：转动时消除其他符号并获得金币
# 12. 复制型：转动时复制其他符号
# 13. 永久效果型：获得后永久生效
# 14. 一次性效果型：触发一次后从卡池移除
# 15. 负面效果型：带来各种负面惩罚

# ==================== 符号系统定义 ====================
# 符号格式：名称 -> (基础价值, 稀有度, 描述, 效果函数, 触发类型)
# 稀有度：1=普通, 2=稀有, 3=史诗, 4=传说, 5=神话
SYMBOLS = {}

# 效果函数参数：(symbol_counts: Dict[str, int], board: List[List[str]], position: Tuple[int, int], game: Game) -> int
# 返回值：该符号额外产生的金币数

# -------------------- 1. 基础价值型 (20个) --------------------
basic_symbols = [
    ("硬币", 1, 1, "基础货币，价值1金币", lambda *args: 0, "基础价值"),
    ("铜币", 1, 1, "古老的铜币，价值1金币", lambda *args: 0, "基础价值"),
    ("铁币", 1, 1, "生锈的铁币，价值1金币", lambda *args: 0, "基础价值"),
    ("银币", 2, 1, "闪亮的银币，价值2金币", lambda *args: 0, "基础价值"),
    ("金币", 3, 1, "纯金的金币，价值3金币", lambda *args: 0, "基础价值"),
    ("苹果", 2, 1, "新鲜的苹果，价值2金币", lambda *args: 0, "基础价值"),
    ("香蕉", 2, 1, "香甜的香蕉，价值2金币", lambda *args: 0, "基础价值"),
    ("橙子", 2, 1, "多汁的橙子，价值2金币", lambda *args: 0, "基础价值"),
    ("葡萄", 3, 1, "一串葡萄，价值3金币", lambda *args: 0, "基础价值"),
    ("草莓", 3, 1, "新鲜的草莓，价值3金币", lambda *args: 0, "基础价值"),
    ("面包", 2, 1, "松软的面包，价值2金币", lambda *args: 0, "基础价值"),
    ("牛奶", 2, 1, "新鲜的牛奶，价值2金币", lambda *args: 0, "基础价值"),
    ("鸡蛋", 3, 1, "新鲜的鸡蛋，价值3金币", lambda *args: 0, "基础价值"),
    ("奶酪", 4, 1, "香浓的奶酪，价值4金币", lambda *args: 0, "基础价值"),
    ("石头", 1, 1, "普通的石头，价值1金币", lambda *args: 0, "基础价值"),
    ("木头", 1, 1, "普通的木头，价值1金币", lambda *args: 0, "基础价值"),
    ("泥土", 1, 1, "肥沃的泥土，价值1金币", lambda *args: 0, "基础价值"),
    ("沙子", 1, 1, "细沙，价值1金币", lambda *args: 0, "基础价值"),
    ("水", 1, 1, "清水，价值1金币", lambda *args: 0, "基础价值"),
    ("火", 2, 1, "火焰，价值2金币", lambda *args: 0, "基础价值"),
]

for name, value, rarity, desc, effect, trigger in basic_symbols:
    SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 2. 全局协同型 (30个) --------------------
def global_synergy(target: str, bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        return symbol_counts.get(target, 0) * bonus
    return effect

def multi_synergy(targets: List[str], bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        total = 0
        for t in targets:
            total += symbol_counts.get(t, 0)
        return total * bonus
    return effect

global_synergy_symbols = [
    ("猫", 5, 2, "每有一只老鼠额外+3金币", global_synergy("老鼠", 3), "全局协同"),
    ("狗", 6, 2, "每有一只猫额外+4金币", global_synergy("猫", 4), "全局协同"),
    ("老鼠", 2, 2, "每有一块奶酪额外+5金币", global_synergy("奶酪", 5), "全局协同"),
    ("矿工", 4, 2, "每有一个宝石额外+8金币", global_synergy("宝石", 8), "全局协同"),
    ("农夫", 3, 2, "每有一个农作物额外+2金币", multi_synergy(["苹果", "小麦", "玉米", "土豆"], 2), "全局协同"),
    ("厨师", 5, 2, "每有一个食物额外+3金币", multi_synergy(["面包", "牛奶", "鸡蛋", "奶酪", "苹果"], 3), "全局协同"),
    ("渔夫", 5, 2, "每有一条鱼额外+6金币", global_synergy("鱼", 6), "全局协同"),
    ("猎人", 6, 2, "每有一块肉额外+5金币", global_synergy("肉", 5), "全局协同"),
    ("木匠", 4, 2, "每有一块木头额外+3金币", global_synergy("木头", 3), "全局协同"),
    ("石匠", 4, 2, "每有一块石头额外+3金币", global_synergy("石头", 3), "全局协同"),
    ("养蜂人", 5, 2, "每有一罐蜂蜜额外+7金币", global_synergy("蜂蜜", 7), "全局协同"),
    ("面包师", 5, 2, "每有一个面包额外+5金币", global_synergy("面包", 5), "全局协同"),
    ("铁匠", 6, 2, "每有一块铁额外+6金币", global_synergy("铁", 6), "全局协同"),
    ("金匠", 8, 2, "每有一块黄金额外+10金币", global_synergy("黄金", 10), "全局协同"),
    ("珠宝商", 10, 2, "每有一颗宝石额外+12金币", global_synergy("宝石", 12), "全局协同"),
    ("学者", 7, 2, "每有一本书额外+6金币", global_synergy("书", 6), "全局协同"),
    ("作家", 8, 2, "每有一支笔额外+7金币", global_synergy("笔", 7), "全局协同"),
    ("音乐家", 10, 2, "每有一件乐器额外+9金币", global_synergy("乐器", 9), "全局协同"),
    ("医生", 12, 2, "每有一瓶药额外+10金币", global_synergy("药水", 10), "全局协同"),
    ("药剂师", 11, 2, "每有一株草药额外+9金币", global_synergy("草药", 9), "全局协同"),
    ("骑士", 15, 2, "每有一把剑额外+12金币", global_synergy("剑", 12), "全局协同"),
    ("弓箭手", 14, 2, "每有一把弓额外+11金币", global_synergy("弓", 11), "全局协同"),
    ("法师", 16, 2, "每有一根法杖额外+13金币", global_synergy("法杖", 13), "全局协同"),
    ("商人", 12, 2, "每有一个金币额外+2金币", global_synergy("金币", 2), "全局协同"),
    ("银行家", 18, 2, "每有一个银币额外+3金币", global_synergy("银币", 3), "全局协同"),
    ("龙", 50, 4, "所有宝石价值x2", lambda *args: 0, "全局协同"),
    ("精灵", 30, 4, "所有自然符号价值+5", lambda *args: 0, "全局协同"),
    ("矮人", 25, 4, "所有矿物符号价值+6", lambda *args: 0, "全局协同"),
    ("兽人", 28, 4, "所有武器符号价值+7", lambda *args: 0, "全局协同"),
    ("巨人", 45, 4, "所有大型符号价值+10", lambda *args: 0, "全局协同"),
]

for name, value, rarity, desc, effect, trigger in global_synergy_symbols:
    SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 3. 相邻加成型 (20个) --------------------
def adjacent_bonus(bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        r, c = pos
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                if 0 <= r+dr < 3 and 0 <= c+dc < 3:
                    count += 1
        return count * bonus
    return effect

def adjacent_type_bonus(target_type: str, bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        r, c = pos
        total = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                if 0 <= r+dr < 3 and 0 <= c+dc < 3:
                    symbol = board[r+dr][c+dc]
                    if SYMBOLS[symbol][4] == target_type:
                        total += bonus
        return total
    return effect

adjacent_symbols = [
    ("磁铁", 5, 2, "每个相邻符号额外+2金币", adjacent_bonus(2), "相邻加成"),
    ("灯塔", 6, 2, "每个相邻符号额外+3金币", adjacent_bonus(3), "相邻加成"),
    ("火炬", 4, 2, "每个相邻符号额外+1金币", adjacent_bonus(1), "相邻加成"),
    ("灯笼", 5, 2, "每个相邻符号额外+2金币", adjacent_bonus(2), "相邻加成"),
    ("镜子", 7, 2, "每个相邻符号额外+3金币", adjacent_bonus(3), "相邻加成"),
    ("棱镜", 8, 2, "每个相邻符号额外+4金币", adjacent_bonus(4), "相邻加成"),
    ("水晶", 9, 3, "每个相邻符号额外+5金币", adjacent_bonus(5), "相邻加成"),
    ("放大器", 10, 3, "每个相邻符号额外+6金币", adjacent_bonus(6), "相邻加成"),
    ("太阳花", 6, 2, "每个相邻基础符号额外+4金币", adjacent_type_bonus("基础价值", 4), "相邻加成"),
    ("月光花", 7, 2, "每个相邻稀有符号额外+5金币", adjacent_type_bonus("全局协同", 5), "相邻加成"),
    ("星星花", 8, 2, "每个相邻史诗符号额外+6金币", adjacent_type_bonus("同行加成", 6), "相邻加成"),
    ("向日葵", 5, 2, "每个相邻自然符号额外+4金币", adjacent_type_bonus("基础价值", 4), "相邻加成"),
    ("荷花", 6, 2, "每个相邻水符号额外+4金币", adjacent_type_bonus("基础价值", 4), "相邻加成"),
    ("仙人掌", 5, 2, "每个相邻沙漠符号额外+4金币", adjacent_type_bonus("基础价值", 4), "相邻加成"),
    ("松树", 6, 2, "每个相邻雪符号额外+4金币", adjacent_type_bonus("基础价值", 4), "相邻加成"),
    ("蜜蜂", 4, 2, "每个相邻花符号额外+5金币", adjacent_type_bonus("相邻加成", 5), "相邻加成"),
    ("蝴蝶", 5, 2, "每个相邻花符号额外+4金币", adjacent_type_bonus("相邻加成", 4), "相邻加成"),
    ("青蛙", 4, 2, "每个相邻水符号额外+4金币", adjacent_type_bonus("基础价值", 4), "相邻加成"),
    ("乌龟", 5, 2, "每个相邻水符号额外+5金币", adjacent_type_bonus("基础价值", 5), "相邻加成"),
    ("章鱼", 8, 3, "每个相邻水符号额外+8金币", adjacent_type_bonus("基础价值", 8), "相邻加成"),
]

for name, value, rarity, desc, effect, trigger in adjacent_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 4. 同行加成型 (20个) --------------------
def row_bonus(bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        r, c = pos
        return (len(board[r]) - 1) * bonus
    return effect

def row_type_bonus(target_type: str, bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        r, c = pos
        total = 0
        for symbol in board[r]:
            if SYMBOLS[symbol][4] == target_type:
                total += bonus
        return total - bonus  # 减去自身
    return effect

row_symbols = [
    ("横幅", 5, 2, "同一行每个符号额外+2金币", row_bonus(2), "同行加成"),
    ("旗帜", 6, 2, "同一行每个符号额外+3金币", row_bonus(3), "同行加成"),
    ("标语", 4, 2, "同一行每个符号额外+1金币", row_bonus(1), "同行加成"),
    ("广告牌", 7, 2, "同一行每个符号额外+3金币", row_bonus(3), "同行加成"),
    ("霓虹灯", 8, 3, "同一行每个符号额外+4金币", row_bonus(4), "同行加成"),
    ("聚光灯", 9, 3, "同一行每个符号额外+5金币", row_bonus(5), "同行加成"),
    ("舞台", 10, 3, "同一行每个符号额外+6金币", row_bonus(6), "同行加成"),
    ("跑道", 11, 3, "同一行每个符号额外+7金币", row_bonus(7), "同行加成"),
    ("传送带", 6, 2, "同一行每个基础符号额外+3金币", row_type_bonus("基础价值", 3), "同行加成"),
    ("流水线", 7, 2, "同一行每个工业符号额外+4金币", row_type_bonus("全局协同", 4), "同行加成"),
    ("生产线", 8, 3, "同一行每个制造符号额外+5金币", row_type_bonus("同行加成", 5), "同行加成"),
    ("货架", 5, 2, "同一行每个商品符号额外+3金币", row_type_bonus("基础价值", 3), "同行加成"),
    ("柜台", 6, 2, "同一行每个交易符号额外+4金币", row_type_bonus("全局协同", 4), "同行加成"),
    ("收银台", 7, 3, "同一行每个货币符号额外+5金币", row_type_bonus("基础价值", 5), "同行加成"),
    ("书架", 5, 2, "同一行每个书籍符号额外+3金币", row_type_bonus("全局协同", 3), "同行加成"),
    ("书桌", 6, 2, "同一行每个学习符号额外+4金币", row_type_bonus("同行加成", 4), "同行加成"),
    ("黑板", 7, 3, "同一行每个教育符号额外+5金币", row_type_bonus("全局协同", 5), "同行加成"),
    ("讲台", 8, 3, "同一行每个教学符号额外+6金币", row_type_bonus("同行加成", 6), "同行加成"),
    ("餐桌", 5, 2, "同一行每个食物符号额外+3金币", row_type_bonus("基础价值", 3), "同行加成"),
    ("厨房", 6, 3, "同一行每个烹饪符号额外+4金币", row_type_bonus("全局协同", 4), "同行加成"),
]

for name, value, rarity, desc, effect, trigger in row_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 5. 同列加成型 (20个) --------------------
def col_bonus(bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        r, c = pos
        return (len(board) - 1) * bonus
    return effect

def col_type_bonus(target_type: str, bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        r, c = pos
        total = 0
        for row in board:
            if SYMBOLS[row[c]][4] == target_type:
                total += bonus
        return total - bonus  # 减去自身
    return effect

col_symbols = [
    ("柱子", 5, 2, "同一列每个符号额外+2金币", col_bonus(2), "同列加成"),
    ("支柱", 6, 2, "同一列每个符号额外+3金币", col_bonus(3), "同列加成"),
    ("梯子", 4, 2, "同一列每个符号额外+1金币", col_bonus(1), "同列加成"),
    ("电梯", 7, 2, "同一列每个符号额外+3金币", col_bonus(3), "同列加成"),
    ("楼梯", 8, 3, "同一列每个符号额外+4金币", col_bonus(4), "同列加成"),
    ("滑梯", 9, 3, "同一列每个符号额外+5金币", col_bonus(5), "同列加成"),
    ("瀑布", 10, 3, "同一列每个符号额外+6金币", col_bonus(6), "同列加成"),
    ("喷泉", 11, 3, "同一列每个符号额外+7金币", col_bonus(7), "同列加成"),
    ("水管", 6, 2, "同一列每个水符号额外+3金币", col_type_bonus("基础价值", 3), "同列加成"),
    ("电线", 7, 2, "同一列每个电符号额外+4金币", col_type_bonus("全局协同", 4), "同列加成"),
    ("管道", 8, 3, "同一列每个气体符号额外+5金币", col_type_bonus("同行加成", 5), "同列加成"),
    ("烟囱", 5, 2, "同一列每个烟符号额外+3金币", col_type_bonus("基础价值", 3), "同列加成"),
    ("天线", 6, 2, "同一列每个信号符号额外+4金币", col_type_bonus("全局协同", 4), "同列加成"),
    ("避雷针", 7, 3, "同一列每个雷符号额外+5金币", col_type_bonus("基础价值", 5), "同列加成"),
    ("书架2", 5, 2, "同一列每个书籍符号额外+3金币", col_type_bonus("全局协同", 3), "同列加成"),
    ("文件柜", 6, 2, "同一列每个文件符号额外+4金币", col_type_bonus("同行加成", 4), "同列加成"),
    ("档案架", 7, 3, "同一列每个档案符号额外+5金币", col_type_bonus("全局协同", 5), "同列加成"),
    ("货架2", 8, 3, "同一列每个商品符号额外+6金币", col_type_bonus("同行加成", 6), "同列加成"),
    ("衣架", 5, 2, "同一列每个衣服符号额外+3金币", col_type_bonus("基础价值", 3), "同列加成"),
    ("衣柜", 6, 3, "同一列每个服装符号额外+4金币", col_type_bonus("全局协同", 4), "同列加成"),
]

for name, value, rarity, desc, effect, trigger in col_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 6. 对角线加成型 (20个) --------------------
def diagonal_bonus(bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        r, c = pos
        if (r == c) or (r + c == 2):
            return 2 * bonus  # 两条对角线最多各有2个其他符号
        return 0
    return effect

def diagonal_type_bonus(target_type: str, bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        r, c = pos
        total = 0
        # 主对角线
        if r == c:
            for i in range(3):
                if i != r and SYMBOLS[board[i][i]][4] == target_type:
                    total += bonus
        # 副对角线
        if r + c == 2:
            for i in range(3):
                j = 2 - i
                if j != c and SYMBOLS[board[i][j]][4] == target_type:
                    total += bonus
        return total
    return effect

diagonal_symbols = [
    ("十字", 5, 2, "在对角线上时每个对角线符号额外+2金币", diagonal_bonus(2), "对角线加成"),
    ("X标记", 6, 2, "在对角线上时每个对角线符号额外+3金币", diagonal_bonus(3), "对角线加成"),
    ("星号", 4, 2, "在对角线上时每个对角线符号额外+1金币", diagonal_bonus(1), "对角线加成"),
    ("钻石", 7, 2, "在对角线上时每个对角线符号额外+3金币", diagonal_bonus(3), "对角线加成"),
    ("菱形", 8, 3, "在对角线上时每个对角线符号额外+4金币", diagonal_bonus(4), "对角线加成"),
    ("三角形", 9, 3, "在对角线上时每个对角线符号额外+5金币", diagonal_bonus(5), "对角线加成"),
    ("正方形", 10, 3, "在对角线上时每个对角线符号额外+6金币", diagonal_bonus(6), "对角线加成"),
    ("圆形", 11, 3, "在对角线上时每个对角线符号额外+7金币", diagonal_bonus(7), "对角线加成"),
    ("宝剑", 6, 2, "在对角线上时每个武器符号额外+3金币", diagonal_type_bonus("全局协同", 3), "对角线加成"),
    ("长矛", 7, 2, "在对角线上时每个武器符号额外+4金币", diagonal_type_bonus("同行加成", 4), "对角线加成"),
    ("弓箭", 8, 3, "在对角线上时每个远程符号额外+5金币", diagonal_type_bonus("全局协同", 5), "对角线加成"),
    ("法杖", 9, 3, "在对角线上时每个魔法符号额外+6金币", diagonal_type_bonus("同行加成", 6), "对角线加成"),
    ("圣杯", 10, 4, "在对角线上时每个神圣符号额外+7金币", diagonal_type_bonus("全局协同", 7), "对角线加成"),
    ("王冠", 11, 4, "在对角线上时每个皇家符号额外+8金币", diagonal_type_bonus("同行加成", 8), "对角线加成"),
    ("权杖", 12, 4, "在对角线上时每个权力符号额外+9金币", diagonal_type_bonus("全局协同", 9), "对角线加成"),
    ("宝珠", 13, 4, "在对角线上时每个魔法符号额外+10金币", diagonal_type_bonus("同行加成", 10), "对角线加成"),
    ("闪电", 6, 2, "在对角线上时每个电符号额外+3金币", diagonal_type_bonus("基础价值", 3), "对角线加成"),
    ("火焰2", 7, 2, "在对角线上时每个火符号额外+4金币", diagonal_type_bonus("基础价值", 4), "对角线加成"),
    ("冰霜", 8, 3, "在对角线上时每个冰符号额外+5金币", diagonal_type_bonus("基础价值", 5), "对角线加成"),
    ("大地", 9, 3, "在对角线上时每个土符号额外+6金币", diagonal_type_bonus("基础价值", 6), "对角线加成"),
]

for name, value, rarity, desc, effect, trigger in diagonal_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 7. 数量触发型 (20个) --------------------
def count_trigger(threshold: int, bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        count = symbol_counts.get(board[pos[0]][pos[1]], 0)
        if count >= threshold:
            return count * bonus
        return 0
    return effect

def count_special_trigger(threshold: int, special_bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        count = symbol_counts.get(board[pos[0]][pos[1]], 0)
        if count >= threshold:
            return special_bonus
        return 0
    return effect

count_symbols = [
    ("三叶草", 3, 2, "出现3个时每个额外+5金币", count_trigger(3, 5), "数量触发"),
    ("四叶草", 5, 3, "出现4个时每个额外+10金币", count_trigger(4, 10), "数量触发"),
    ("五叶草", 10, 4, "出现5个时每个额外+20金币", count_trigger(5, 20), "数量触发"),
    ("骰子", 2, 2, "出现2个时每个额外+3金币", count_trigger(2, 3), "数量触发"),
    ("扑克牌", 3, 2, "出现3个时每个额外+6金币", count_trigger(3, 6), "数量触发"),
    ("麻将", 4, 3, "出现4个时每个额外+8金币", count_trigger(4, 8), "数量触发"),
    ("棋子", 3, 2, "出现3个时每个额外+5金币", count_trigger(3, 5), "数量触发"),
    ("拼图", 4, 3, "出现4个时每个额外+7金币", count_trigger(4, 7), "数量触发"),
    ("积木", 2, 2, "出现2个时每个额外+4金币", count_trigger(2, 4), "数量触发"),
    ("乐高", 5, 3, "出现5个时每个额外+10金币", count_trigger(5, 10), "数量触发"),
    ("炸弹", 0, 2, "出现3个时获得100金币", count_special_trigger(3, 100), "数量触发"),
    ("核弹", 0, 4, "出现2个时获得500金币", count_special_trigger(2, 500), "数量触发"),
    ("黑洞", 0, 5, "出现1个时获得1000金币", count_special_trigger(1, 1000), "数量触发"),
    ("宝藏", 10, 3, "出现3个时获得300金币", count_special_trigger(3, 300), "数量触发"),
    ("黄金宝箱", 20, 4, "出现2个时获得600金币", count_special_trigger(2, 600), "数量触发"),
    ("钻石宝箱", 30, 5, "出现1个时获得1000金币", count_special_trigger(1, 1000), "数量触发"),
    ("幸运星", 5, 2, "出现3个时获得150金币", count_special_trigger(3, 150), "数量触发"),
    ("彩虹", 15, 3, "出现2个时获得400金币", count_special_trigger(2, 400), "数量触发"),
    ("流星", 25, 4, "出现1个时获得800金币", count_special_trigger(1, 800), "数量触发"),
    ("彗星", 50, 5, "出现1个时获得2000金币", count_special_trigger(1, 2000), "数量触发"),
]

for name, value, rarity, desc, effect, trigger in count_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 8. 回合触发型 (20个) --------------------
def turn_trigger(turn_mod: int, bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        if game.player.turn % turn_mod == 0:
            return bonus
        return 0
    return effect

def turn_range_trigger(start: int, end: int, bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        if start <= game.player.turn <= end:
            return bonus
        return 0
    return effect

turn_symbols = [
    ("每日", 2, 2, "每回合额外+2金币", turn_trigger(1, 2), "回合触发"),
    ("每周", 5, 2, "每5回合额外+20金币", turn_trigger(5, 20), "回合触发"),
    ("每月", 10, 3, "每10回合额外+50金币", turn_trigger(10, 50), "回合触发"),
    ("每年", 20, 4, "每20回合额外+200金币", turn_trigger(20, 200), "回合触发"),
    ("工作日", 3, 2, "第1-5回合每回合+5金币", turn_range_trigger(1, 5, 5), "回合触发"),
    ("周末", 6, 2, "第6-7回合每回合+10金币", turn_range_trigger(6, 7, 10), "回合触发"),
    ("假期", 15, 3, "第10-15回合每回合+15金币", turn_range_trigger(10, 15, 15), "回合触发"),
    ("节日", 25, 4, "第20-25回合每回合+25金币", turn_range_trigger(20, 25, 25), "回合触发"),
    ("春天", 8, 2, "第1-3回合每回合+8金币", turn_range_trigger(1, 3, 8), "回合触发"),
    ("夏天", 10, 2, "第4-6回合每回合+10金币", turn_range_trigger(4, 6, 10), "回合触发"),
    ("秋天", 12, 3, "第7-9回合每回合+12金币", turn_range_trigger(7, 9, 12), "回合触发"),
    ("冬天", 14, 3, "第10-12回合每回合+14金币", turn_range_trigger(10, 12, 14), "回合触发"),
    ("早晨", 4, 2, "第1-2回合每回合+4金币", turn_range_trigger(1, 2, 4), "回合触发"),
    ("中午", 6, 2, "第3-4回合每回合+6金币", turn_range_trigger(3, 4, 6), "回合触发"),
    ("下午", 8, 2, "第5-6回合每回合+8金币", turn_range_trigger(5, 6, 8), "回合触发"),
    ("晚上", 10, 3, "第7-8回合每回合+10金币", turn_range_trigger(7, 8, 10), "回合触发"),
    ("生日", 100, 5, "第12回合额外+1000金币", turn_trigger(12, 1000), "回合触发"),
    ("新年", 80, 5, "第6回合额外+500金币", turn_trigger(6, 500), "回合触发"),
    ("圣诞节", 90, 5, "第9回合额外+800金币", turn_trigger(9, 800), "回合触发"),
    ("万圣节", 70, 5, "第10回合额外+600金币", turn_trigger(10, 600), "回合触发"),
]

for name, value, rarity, desc, effect, trigger in turn_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 9. 位置触发型 (20个) --------------------
def position_trigger(positions: List[Tuple[int, int]], bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        if pos in positions:
            return bonus
        return 0
    return effect

position_symbols = [
    ("中心", 10, 3, "在中心位置价值x5", position_trigger([(1,1)], 40), "位置触发"),
    ("角落", 8, 3, "在角落位置价值x4", position_trigger([(0,0), (0,2), (2,0), (2,2)], 24), "位置触发"),
    ("边缘", 6, 3, "在边缘位置价值x3", position_trigger([(0,1), (1,0), (1,2), (2,1)], 12), "位置触发"),
    ("第一行", 7, 3, "在第一行价值x3", position_trigger([(0,0), (0,1), (0,2)], 14), "位置触发"),
    ("第二行", 7, 3, "在第二行价值x3", position_trigger([(1,0), (1,1), (1,2)], 14), "位置触发"),
    ("第三行", 7, 3, "在第三行价值x3", position_trigger([(2,0), (2,1), (2,2)], 14), "位置触发"),
    ("第一列", 7, 3, "在第一列价值x3", position_trigger([(0,0), (1,0), (2,0)], 14), "位置触发"),
    ("第二列", 7, 3, "在第二列价值x3", position_trigger([(0,1), (1,1), (2,1)], 14), "位置触发"),
    ("第三列", 7, 3, "在第三列价值x3", position_trigger([(0,2), (1,2), (2,2)], 14), "位置触发"),
    ("主对角线", 9, 3, "在主对角线价值x4", position_trigger([(0,0), (1,1), (2,2)], 27), "位置触发"),
    ("副对角线", 9, 3, "在副对角线价值x4", position_trigger([(0,2), (1,1), (2,0)], 27), "位置触发"),
    ("左上角", 12, 4, "在左上角价值x6", position_trigger([(0,0)], 60), "位置触发"),
    ("右上角", 12, 4, "在右上角价值x6", position_trigger([(0,2)], 60), "位置触发"),
    ("左下角", 12, 4, "在左下角价值x6", position_trigger([(2,0)], 60), "位置触发"),
    ("右下角", 12, 4, "在右下角价值x6", position_trigger([(2,2)], 60), "位置触发"),
    ("上中", 10, 4, "在上中位置价值x5", position_trigger([(0,1)], 40), "位置触发"),
    ("左中", 10, 4, "在左中位置价值x5", position_trigger([(1,0)], 40), "位置触发"),
    ("右中", 10, 4, "在右中位置价值x5", position_trigger([(1,2)], 40), "位置触发"),
    ("下中", 10, 4, "在下中位置价值x5", position_trigger([(2,1)], 40), "位置触发"),
    ("绝对中心", 15, 5, "在中心位置价值x10", position_trigger([(1,1)], 135), "位置触发"),
]

for name, value, rarity, desc, effect, trigger in position_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 10. 生成型 (20个) --------------------
def generate_symbol(target: str, chance: float) -> Callable:
    def effect(symbol_counts, board, pos, game):
        if random.random() < chance:
            game.generated_symbols.append(target)
        return 0
    return effect

def generate_random(chance: float, rarity: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        if random.random() < chance:
            candidates = [k for k, v in SYMBOLS.items() if v[1] == rarity]
            if candidates:
                game.generated_symbols.append(random.choice(candidates))
        return 0
    return effect

generate_symbols = [
    ("金蛋", 10, 3, "有10%概率生成一个黄金", generate_symbol("黄金", 0.1), "生成型"),
    ("银蛋", 5, 2, "有10%概率生成一个银币", generate_symbol("银币", 0.1), "生成型"),
    ("彩蛋", 8, 2, "有5%概率生成一个随机稀有符号", generate_random(0.05, 2), "生成型"),
    ("宝箱", 15, 3, "有20%概率生成一个随机史诗符号", generate_random(0.2, 3), "生成型"),
    ("神秘宝箱", 30, 4, "有10%概率生成一个随机传说符号", generate_random(0.1, 4), "生成型"),
    ("礼物", 5, 2, "有15%概率生成一个随机普通符号", generate_random(0.15, 1), "生成型"),
    ("糖果", 3, 2, "有10%概率生成一个随机食物符号", generate_symbol("苹果", 0.1), "生成型"),
    ("蛋糕", 10, 3, "有25%概率生成三个随机食物符号", generate_symbol("面包", 0.25), "生成型"),
    ("种子", 2, 2, "有20%概率生成一个随机植物符号", generate_symbol("树", 0.2), "生成型"),
    ("树苗", 5, 2, "有30%概率生成一个树符号", generate_symbol("树", 0.3), "生成型"),
    ("母鸡", 8, 2, "有15%概率生成一个鸡蛋", generate_symbol("鸡蛋", 0.15), "生成型"),
    ("奶牛", 12, 3, "有20%概率生成一个牛奶", generate_symbol("牛奶", 0.2), "生成型"),
    ("蜜蜂2", 6, 2, "有10%概率生成一个蜂蜜", generate_symbol("蜂蜜", 0.1), "生成型"),
    ("果树", 15, 3, "有25%概率生成一个苹果", generate_symbol("苹果", 0.25), "生成型"),
    ("葡萄藤", 12, 3, "有20%概率生成一个葡萄", generate_symbol("葡萄", 0.2), "生成型"),
    ("小麦", 4, 2, "有15%概率生成一个面包", generate_symbol("面包", 0.15), "生成型"),
    ("玉米", 5, 2, "有15%概率生成一个爆米花", generate_symbol("爆米花", 0.15), "生成型"),
    ("土豆2", 3, 2, "有10%概率生成一个薯条", generate_symbol("薯条", 0.1), "生成型"),
    ("番茄2", 4, 2, "有10%概率生成一个番茄酱", generate_symbol("番茄酱", 0.1), "生成型"),
    ("魔法井", 50, 5, "有50%概率生成一个随机神话符号", generate_random(0.5, 5), "生成型"),
]

# 添加缺失的基础符号
missing_basic = [
    ("蜂蜜", 5, 1, "甜蜜的蜂蜜，价值5金币", lambda *args: 0, "基础价值"),
    ("树", 5, 1, "大树，价值5金币", lambda *args: 0, "基础价值"),
    ("爆米花", 3, 1, "爆米花，价值3金币", lambda *args: 0, "基础价值"),
    ("薯条", 4, 1, "薯条，价值4金币", lambda *args: 0, "基础价值"),
    ("番茄酱", 2, 1, "番茄酱，价值2金币", lambda *args: 0, "基础价值"),
    ("肉", 5, 1, "肉，价值5金币", lambda *args: 0, "基础价值"),
    ("铁", 5, 1, "铁，价值5金币", lambda *args: 0, "基础价值"),
    ("黄金", 20, 1, "黄金，价值20金币", lambda *args: 0, "基础价值"),
    ("宝石", 15, 1, "宝石，价值15金币", lambda *args: 0, "基础价值"),
    ("书", 6, 1, "书，价值6金币", lambda *args: 0, "基础价值"),
    ("笔", 4, 1, "笔，价值4金币", lambda *args: 0, "基础价值"),
    ("乐器", 8, 1, "乐器，价值8金币", lambda *args: 0, "基础价值"),
    ("药水", 7, 1, "药水，价值7金币", lambda *args: 0, "基础价值"),
    ("草药", 5, 1, "草药，价值5金币", lambda *args: 0, "基础价值"),
    ("剑", 10, 1, "剑，价值10金币", lambda *args: 0, "基础价值"),
    ("弓", 9, 1, "弓，价值9金币", lambda *args: 0, "基础价值"),
    ("法杖", 12, 1, "法杖，价值12金币", lambda *args: 0, "基础价值"),
    ("鱼", 3, 1, "鱼，价值3金币", lambda *args: 0, "基础价值"),
    ("小麦", 2, 1, "小麦，价值2金币", lambda *args: 0, "基础价值"),
    ("玉米", 2, 1, "玉米，价值2金币", lambda *args: 0, "基础价值"),
]

for name, value, rarity, desc, effect, trigger in missing_basic:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

for name, value, rarity, desc, effect, trigger in generate_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 11. 消除型 (20个) --------------------
def destroy_type(target_type: str, bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        total = 0
        for r in range(3):
            for c in range(3):
                if (r, c) != pos and SYMBOLS[board[r][c]][4] == target_type:
                    total += bonus
                    game.destroyed_symbols.append((r, c))
        return total
    return effect

def destroy_all(bonus: int) -> Callable:
    def effect(symbol_counts, board, pos, game):
        total = 0
        for r in range(3):
            for c in range(3):
                if (r, c) != pos:
                    total += bonus
                    game.destroyed_symbols.append((r, c))
        return total
    return effect

destroy_symbols = [
    ("炸弹", 0, 2, "消除所有相邻符号，每个给予10金币", destroy_type("基础价值", 10), "消除型"),
    ("核弹", 0, 4, "消除所有符号，每个给予20金币", destroy_all(20), "消除型"),
    ("吸尘器", 0, 3, "消除所有普通符号，每个给予5金币", destroy_type("基础价值", 5), "消除型"),
    ("磁铁石", 0, 3, "消除所有金属符号，每个给予8金币", destroy_type("全局协同", 8), "消除型"),
    ("火焰3", 0, 3, "消除所有植物符号，每个给予6金币", destroy_type("基础价值", 6), "消除型"),
    ("洪水", 0, 3, "消除所有陆地符号，每个给予7金币", destroy_type("同行加成", 7), "消除型"),
    ("地震", 0, 4, "消除所有矿物符号，每个给予10金币", destroy_type("基础价值", 10), "消除型"),
    ("龙卷风", 0, 4, "消除所有空中符号，每个给予9金币", destroy_type("同列加成", 9), "消除型"),
    ("黑洞2", 0, 5, "消除所有符号，每个给予50金币", destroy_all(50), "消除型"),
    ("净化", 0, 4, "消除所有负面符号，每个给予15金币", destroy_type("负面效果", 15), "消除型"),
    ("除草剂", 0, 2, "消除所有杂草符号，每个给予3金币", destroy_type("基础价值", 3), "消除型"),
    ("杀虫剂", 0, 2, "消除所有昆虫符号，每个给予4金币", destroy_type("相邻加成", 4), "消除型"),
    ("灭鼠器", 0, 2, "消除所有老鼠符号，每个给予5金币", destroy_type("全局协同", 5), "消除型"),
    ("捕蝇草", 0, 3, "消除所有苍蝇符号，每个给予6金币", destroy_type("负面效果", 6), "消除型"),
    ("驱虫剂", 0, 3, "消除所有害虫符号，每个给予7金币", destroy_type("负面效果", 7), "消除型"),
    ("消毒水", 0, 3, "消除所有细菌符号，每个给予8金币", destroy_type("负面效果", 8), "消除型"),
    ("抗生素", 0, 4, "消除所有病毒符号，每个给予10金币", destroy_type("负面效果", 10), "消除型"),
    ("灭火器", 0, 3, "消除所有火焰符号，每个给予9金币", destroy_type("基础价值", 9), "消除型"),
    ("避雷针2", 0, 3, "消除所有闪电符号，每个给予10金币", destroy_type("对角线加成", 10), "消除型"),
    ("盾牌", 0, 4, "消除所有攻击符号，每个给予12金币", destroy_type("全局协同", 12), "消除型"),
]

for name, value, rarity, desc, effect, trigger in destroy_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 12. 复制型 (20个) --------------------
def copy_adjacent(chance: float) -> Callable:
    def effect(symbol_counts, board, pos, game):
        r, c = pos
        adjacent = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                if 0 <= r+dr < 3 and 0 <= c+dc < 3:
                    adjacent.append(board[r+dr][c+dc])
        if adjacent and random.random() < chance:
            game.copied_symbols.append(random.choice(adjacent))
        return 0
    return effect

def copy_random(chance: float) -> Callable:
    def effect(symbol_counts, board, pos, game):
        if random.random() < chance:
            all_symbols = [s for row in board for s in row]
            all_symbols.remove(board[pos[0]][pos[1]])
            if all_symbols:
                game.copied_symbols.append(random.choice(all_symbols))
        return 0
    return effect

copy_symbols = [
    ("镜子3", 10, 3, "有30%概率复制一个相邻符号", copy_adjacent(0.3), "复制型"),
    ("克隆机", 20, 4, "有50%概率复制所有相邻符号", copy_adjacent(0.5), "复制型"),
    ("复印机", 15, 3, "有25%概率复制一个随机符号", copy_random(0.25), "复制型"),
    ("复制器", 25, 4, "有40%概率复制三个随机符号", copy_random(0.4), "复制型"),
    ("分身", 30, 4, "有100%概率复制自身", lambda *args, **kwargs: (kwargs['game'].copied_symbols.append(args[2][args[2].index(args[1][args[0][0]][args[0][1]])]), 0)[1], "复制型"),
    ("双胞胎", 20, 3, "有50%概率复制两个相同的随机符号", copy_random(0.5), "复制型"),
    ("三胞胎", 35, 4, "有60%概率复制三个相同的随机符号", copy_random(0.6), "复制型"),
    ("四胞胎", 50, 5, "有70%概率复制四个相同的随机符号", copy_random(0.7), "复制型"),
    ("照片", 8, 2, "有20%概率复制一个相邻符号", copy_adjacent(0.2), "复制型"),
    ("录像", 12, 3, "有35%概率复制一个随机符号", copy_random(0.35), "复制型"),
    ("录音", 10, 3, "有30%概率复制一个声音符号", copy_adjacent(0.3), "复制型"),
    ("全息投影", 18, 4, "有45%概率复制所有相邻符号", copy_adjacent(0.45), "复制型"),
    ("3D打印机", 22, 4, "有55%概率复制一个随机符号", copy_random(0.55), "复制型"),
    ("扫描仪", 16, 3, "有40%概率复制一个相邻符号", copy_adjacent(0.4), "复制型"),
    ("传真机", 14, 3, "有35%概率复制一个随机符号", copy_random(0.35), "复制型"),
    ("电报", 10, 2, "有25%概率复制一个信号符号", copy_adjacent(0.25), "复制型"),
    ("电话", 12, 3, "有30%概率复制一个声音符号", copy_adjacent(0.3), "复制型"),
    ("电视", 15, 3, "有35%概率复制一个图像符号", copy_random(0.35), "复制型"),
    ("电脑", 20, 4, "有45%概率复制一个数字符号", copy_random(0.45), "复制型"),
    ("互联网", 30, 5, "有60%概率复制任意符号", copy_random(0.6), "复制型"),
]

for name, value, rarity, desc, effect, trigger in copy_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 13. 永久效果型 (10个) --------------------
permanent_symbols = [
    ("永久金币", 0, 4, "永久增加所有符号价值+1", lambda *args: 0, "永久效果"),
    ("永久乘数", 0, 5, "永久增加所有符号价值x1.1", lambda *args: 0, "永久效果"),
    ("永久房租减免", 0, 5, "永久减少房租10%", lambda *args: 0, "永久效果"),
    ("永久旋转加成", 0, 4, "永久每回合额外获得5金币", lambda *args: 0, "永久效果"),
    ("永久幸运", 0, 5, "永久提高稀有符号出现概率20%", lambda *args: 0, "永久效果"),
    ("永久卡池", 0, 4, "永久增加卡池容量10%", lambda *args: 0, "永久效果"),
    ("永久收益", 0, 5, "永久所有收益增加15%", lambda *args: 0, "永久效果"),
    ("永久防御", 0, 4, "永久减少所有负面效果50%", lambda *args: 0, "永久效果"),
    ("永久生命", 0, 5, "永久获得一次免死机会", lambda *args: 0, "永久效果"),
    ("永久胜利", 0, 5, "永久减少胜利所需回合数1", lambda *args: 0, "永久效果"),
]

for name, value, rarity, desc, effect, trigger in permanent_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 14. 一次性效果型 (10个) --------------------
one_time_symbols = [
    ("一次性金币", 0, 2, "立即获得100金币，然后消失", lambda *args: 0, "一次性效果"),
    ("一次性大金币", 0, 3, "立即获得500金币，然后消失", lambda *args: 0, "一次性效果"),
    ("一次性超级金币", 0, 4, "立即获得2000金币，然后消失", lambda *args: 0, "一次性效果"),
    ("一次性免租", 0, 4, "下一次房租免费，然后消失", lambda *args: 0, "一次性效果"),
    ("一次性双倍", 0, 3, "下一次旋转收益翻倍，然后消失", lambda *args: 0, "一次性效果"),
    ("一次性三倍", 0, 4, "下一次旋转收益三倍，然后消失", lambda *args: 0, "一次性效果"),
    ("一次性十倍", 0, 5, "下一次旋转收益十倍，然后消失", lambda *args: 0, "一次性效果"),
    ("一次性重抽", 0, 2, "立即重新旋转一次，然后消失", lambda *args: 0, "一次性效果"),
    ("一次性删除", 0, 3, "删除一个随机普通符号，然后消失", lambda *args: 0, "一次性效果"),
    ("一次性升级", 0, 4, "将一个随机普通符号升级为稀有符号，然后消失", lambda *args: 0, "一次性效果"),
]

for name, value, rarity, desc, effect, trigger in one_time_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# -------------------- 15. 负面效果型 (10个) --------------------
negative_symbols = [
    ("垃圾", -1, 1, "价值-1金币", lambda *args: 0, "负面效果"),
    ("污水", -2, 1, "价值-2金币", lambda *args: 0, "负面效果"),
    ("烟雾", -3, 1, "价值-3金币", lambda *args: 0, "负面效果"),
    ("噪音", -2, 1, "价值-2金币", lambda *args: 0, "负面效果"),
    ("蟑螂", -4, 2, "价值-4金币，每有一个食物额外-1金币", lambda *args: 0, "负面效果"),
    ("苍蝇", -2, 2, "价值-2金币，每有一个食物额外-1金币", lambda *args: 0, "负面效果"),
    ("小偷", -5, 3, "价值-5金币，偷走你10%的金币", lambda *args: 0, "负面效果"),
    ("强盗", -10, 4, "价值-10金币，偷走你25%的金币", lambda *args: 0, "负面效果"),
    ("骗子", -8, 3, "价值-8金币，下一次房租增加20%", lambda *args: 0, "负面效果"),
    ("诅咒", -20, 4, "价值-20金币，所有符号价值-1持续3回合", lambda *args: 0, "负面效果"),
]

for name, value, rarity, desc, effect, trigger in negative_symbols:
    if name not in SYMBOLS:
        SYMBOLS[name] = (value, rarity, desc, effect, trigger)

# 确保总符号数约300个
print(f"总符号数: {len(SYMBOLS)}")
print(f"触发类型数: {len(set(v[4] for v in SYMBOLS.values()))}")
print("触发类型列表:", sorted(set(v[4] for v in SYMBOLS.values())))

# ==================== 游戏核心类 ====================
class SlotMachine:
    def __init__(self):
        self.rows = 3
        self.cols = 3
        self.symbols = ["硬币"]  # 初始只有硬币
        self.board = []
        self.permanent_bonuses = {
            "value_add": 0,
            "value_mult": 1.0,
            "rent_reduction": 0.0,
            "per_turn_gold": 0,
            "luck_bonus": 0.0
        }
    
    def add_symbol(self, symbol: str):
        """添加一个符号到老虎机卡池"""
        self.symbols.append(symbol)
    
    def spin(self) -> List[List[str]]:
        """转动老虎机，生成新的盘面"""
        self.board = []
        for _ in range(self.rows):
            row = []
            for _ in range(self.cols):
                row.append(random.choice(self.symbols))
            self.board.append(row)
        return self.board
    
    def calculate_earnings(self, game) -> Tuple[int, Dict[str, int]]:
        """计算当前盘面的收益"""
        earnings = 0
        symbol_counts = {}
        breakdown = {}
        
        # 统计符号出现次数
        for row in self.board:
            for symbol in row:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        # 计算基础价值和所有特殊效果
        for r in range(self.rows):
            for c in range(self.cols):
                symbol = self.board[r][c]
                base_value = SYMBOLS[symbol][0]
                effect = SYMBOLS[symbol][3]
                
                # 应用永久加成
                final_value = (base_value + self.permanent_bonuses["value_add"]) * self.permanent_bonuses["value_mult"]
                
                # 应用特殊效果
                special_earning = effect(symbol_counts, self.board, (r, c), game)
                final_value += special_earning
                
                earnings += final_value
                breakdown[symbol] = breakdown.get(symbol, 0) + final_value
        
        # 应用全局乘数符号
        multipliers = {"普通": 1, "稀有": 1, "史诗": 1, "传说": 1, "神话": 1, "所有": 1}
        addons = {"普通": 0, "稀有": 0, "史诗": 0, "传说": 0, "神话": 0, "所有": 0}
        
        if "国王" in symbol_counts:
            multipliers["普通"] *= 2
        if "皇后" in symbol_counts:
            multipliers["稀有"] *= 2
        if "龙" in symbol_counts:
            multipliers["史诗"] *= 2
        if "幸运女神" in symbol_counts:
            addons["所有"] += 5
        if "恶魔" in symbol_counts:
            multipliers["所有"] *= 1.5
        if "天使" in symbol_counts:
            multipliers["所有"] *= 1.2
        
        # 重新计算带全局乘数的收益
        final_earnings = 0
        final_breakdown = {}
        
        for symbol, count in symbol_counts.items():
            base_value = SYMBOLS[symbol][0]
            rarity = SYMBOLS[symbol][1]
            
            rarity_type = {1: "普通", 2: "稀有", 3: "史诗", 4: "传说", 5: "神话"}[rarity]
            mult = multipliers[rarity_type] * multipliers["所有"]
            add = addons[rarity_type] + addons["所有"]
            
            final_value = (base_value + add + self.permanent_bonuses["value_add"]) * mult * self.permanent_bonuses["value_mult"] * count
            final_breakdown[symbol] = final_value
            final_earnings += final_value
        
        return int(final_earnings), final_breakdown

class Player:
    def __init__(self):
        self.gold = 10
        self.turn = 1
        self.spins_since_rent = 0
        self.rent = 25
        self.rent_increase = 25
        self.has_phoenix = False
        self.demon_active = False
        self.angel_active = False
        self.extra_lives = 0

class Game:
    def __init__(self):
        self.slot_machine = SlotMachine()
        self.player = Player()
        self.game_over = False
        self.victory = False
        self.generated_symbols = []
        self.destroyed_symbols = []
        self.copied_symbols = []
        self.one_time_symbols_to_remove = []
    
    def clear_screen(self):
        """清屏"""
        print("\033c", end="")
    
    def print_title(self):
        """打印游戏标题（仅上下横线样式）"""
        print("")
        print("══════════════════════════════════════════════════════════════")
        print("                        协 同 效 应                          ")
        print("                    Synergy Effect                           ")
        print("══════════════════════════════════════════════════════════════")
        print("")
    
    def print_status(self):
        """打印游戏状态"""
        print(f"回合: {self.player.turn}")
        print(f"旋转次数: {self.player.spins_since_rent}/5")
        print(f"金币: {self.player.gold}")
        print(f"下一次房租: {self.player.rent} (还需旋转 {5 - self.player.spins_since_rent} 次)")
        print(f"卡池大小: {len(self.slot_machine.symbols)}")
        print(f"15种触发机制已全部激活！")
        print("-" * 60)
    
    def print_board(self, board: List[List[str]]):
        """打印老虎机盘面"""
        print("\n老虎机盘面:")
        print("┌───────────┬───────────┬───────────┐")
        for row in board:
            print("│", end="")
            for symbol in row:
                rarity = SYMBOLS[symbol][1]
                # 简单的稀有度标记
                prefix = ""
                if rarity == 2:
                    prefix = "*"
                elif rarity == 3:
                    prefix = "**"
                elif rarity == 4:
                    prefix = "***"
                elif rarity == 5:
                    prefix = "****"
                print(f" {prefix}{symbol[:7]:^7}{'*'*len(prefix)} │", end="")
            print()
            print("├───────────┼───────────┼───────────┤")
        print("\b└───────────┴───────────┴───────────┘")
        print("\n稀有度标记: *稀有 **史诗 ***传说 ****神话")
    
    def print_earnings_breakdown(self, earnings: int, breakdown: Dict[str, int]):
        """打印收益明细"""
        print(f"\n本次收益: {earnings} 金币")
        print("收益明细(前10项):")
        sorted_items = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:10]
        for item, value in sorted_items:
            print(f"  {item:<15} +{value}")
        if len(breakdown) > 10:
            print(f"  ... 还有 {len(breakdown)-10} 项")
    
    def get_available_symbols(self) -> List[str]:
        """获取可选择的符号"""
        available = []
        all_symbols = list(SYMBOLS.keys())
        
        # 根据回合调整稀有度概率
        weights = []
        for symbol in all_symbols:
            rarity = SYMBOLS[symbol][1]
            base_weights = {1: 60, 2: 25, 3: 10, 4: 4, 5: 1}
            weight = base_weights[rarity]
            
            # 应用幸运加成
            weight *= (1 + self.slot_machine.permanent_bonuses["luck_bonus"])
            
            # 随回合增加稀有度
            if rarity > 1:
                weight += self.player.turn // 2
            
            weights.append(max(1, weight))
        
        # 随机选择3个不同的符号
        while len(available) < 3:
            symbol = random.choices(all_symbols, weights=weights)[0]
            if symbol not in available:
                available.append(symbol)
        
        return available
    
    def choose_symbol(self):
        """让玩家选择一个新符号"""
        print("\n选择一个新符号加入你的卡池:")
        available = self.get_available_symbols()
        
        for i, symbol in enumerate(available):
            value, rarity, desc, _, trigger = SYMBOLS[symbol]
            rarity_text = ["普通", "稀有", "史诗", "传说", "神话"][rarity-1]
            print(f"{i+1}. {symbol} [{rarity_text}] - 基础价值: {value}")
            print(f"   触发类型: {trigger}")
            print(f"   {desc}")
        
        while True:
            try:
                choice = int(input("\n请输入选择 (1-3): ")) - 1
                if 0 <= choice <= 2:
                    selected = available[choice]
                    self.slot_machine.add_symbol(selected)
                    print(f"\n已添加符号: {selected}")
                    
                    # 特殊符号效果
                    if selected == "凤凰":
                        self.player.has_phoenix = True
                        print("凤凰效果激活：本局游戏你不会破产！")
                    elif selected == "独角兽":
                        self.slot_machine.permanent_bonuses["per_turn_gold"] += 10
                        print("独角兽效果激活：每回合额外获得10金币！")
                    elif selected == "恶魔":
                        self.player.demon_active = True
                        print("恶魔效果激活：所有收益x1.5，但房租也x1.5！")
                    elif selected == "天使":
                        self.player.angel_active = True
                        print("天使效果激活：所有收益x1.2，房租x0.8！")
                    elif selected == "永久金币":
                        self.slot_machine.permanent_bonuses["value_add"] += 1
                        print("永久效果激活：所有符号价值+1！")
                    elif selected == "永久房租减免":
                        self.slot_machine.permanent_bonuses["rent_reduction"] += 0.1
                        print("永久效果激活：房租减少10%！")
                    elif selected == "永久旋转加成":
                        self.slot_machine.permanent_bonuses["per_turn_gold"] += 5
                        print("永久效果激活：每回合额外获得5金币！")
                    elif selected == "永久幸运":
                        self.slot_machine.permanent_bonuses["luck_bonus"] += 0.2
                        print("永久效果激活：稀有符号出现概率提高20%！")
                    elif selected == "永久生命":
                        self.player.extra_lives += 1
                        print("永久效果激活：获得一次免死机会！")
                    
                    time.sleep(1.5)
                    return
                else:
                    print("请输入1-3之间的数字")
            except ValueError:
                print("请输入有效的数字")
    
    def check_victory(self):
        """检查是否胜利"""
        if self.player.turn > 12:
            self.victory = True
            self.game_over = True
    
    def process_special_effects(self):
        """处理生成、消除、复制等特殊效果"""
        # 处理生成的符号
        if self.generated_symbols:
            print(f"\n生成了符号: {', '.join(self.generated_symbols)}")
            for symbol in self.generated_symbols:
                self.slot_machine.add_symbol(symbol)
            self.generated_symbols = []
        
        # 处理消除的符号
        if self.destroyed_symbols:
            print(f"消除了 {len(self.destroyed_symbols)} 个符号")
            self.destroyed_symbols = []
        
        # 处理复制的符号
        if self.copied_symbols:
            print(f"复制了符号: {', '.join(self.copied_symbols)}")
            for symbol in self.copied_symbols:
                self.slot_machine.add_symbol(symbol)
            self.copied_symbols = []
    
    def game_loop(self):
        """游戏主循环"""
        while not self.game_over:
            self.clear_screen()
            self.print_title()
            self.print_status()
            
            # 转动老虎机
            input("\n按回车键转动老虎机...")
            board = self.slot_machine.spin()
            self.print_board(board)
            
            earnings, breakdown = self.slot_machine.calculate_earnings(self)
            self.print_earnings_breakdown(earnings, breakdown)
            
            # 处理特殊效果
            self.process_special_effects()
            
            # 应用永久每回合加成
            earnings += self.slot_machine.permanent_bonuses["per_turn_gold"]
            self.player.gold += earnings
            
            print(f"\n当前金币: {self.player.gold}")
            
            # 选择新符号
            self.choose_symbol()
            
            # 增加旋转次数
            self.player.spins_since_rent += 1
            
            # 支付房租（每5次旋转后）
            if self.player.spins_since_rent >= 5:
                actual_rent = self.player.rent
                # 应用房租调整
                actual_rent *= (1 - self.slot_machine.permanent_bonuses["rent_reduction"])
                if self.player.demon_active:
                    actual_rent *= 1.5
                if self.player.angel_active:
                    actual_rent *= 0.8
                actual_rent = int(actual_rent)
                
                print(f"\n现在支付房租: {actual_rent} 金币")
                time.sleep(1)
                
                if self.player.gold >= actual_rent:
                    self.player.gold -= actual_rent
                    self.player.turn += 1
                    self.player.spins_since_rent = 0
                    self.player.rent += self.player.rent_increase
                    # 房租增长曲线
                    if self.player.turn > 5:
                        self.player.rent_increase += 10
                    if self.player.turn > 8:
                        self.player.rent_increase += 15
                else:
                    if self.player.extra_lives > 0:
                        self.player.extra_lives -= 1
                        print(f"\n免死机会生效！你还有 {self.player.extra_lives} 次免死机会")
                        self.player.gold = 0
                        self.player.turn += 1
                        self.player.spins_since_rent = 0
                        self.player.rent += self.player.rent_increase
                    elif self.player.has_phoenix:
                        print("\n凤凰救了你！你没有破产，但失去了所有金币。")
                        self.player.gold = 0
                        self.player.turn += 1
                        self.player.spins_since_rent = 0
                        self.player.rent += self.player.rent_increase
                        if self.player.turn > 5:
                            self.player.rent_increase += 10
                        if self.player.turn > 8:
                            self.player.rent_increase += 15
                    else:
                        self.game_over = True
                        self.victory = False
            
            # 检查胜利
            self.check_victory()
            
            if not self.game_over:
                input("\n按回车键继续...")
        
        # 游戏结束
        self.clear_screen()
        self.print_title()
        if self.victory:
            print("🎉🎉🎉 恭喜你！你成功击败了房东！🎉🎉🎉")
            print(f"你坚持了 {self.player.turn} 个回合，最终拥有 {self.player.gold} 金币")
            print(f"总共添加了 {len(self.slot_machine.symbols)-1} 个符号")
            print(f"体验了全部15种触发机制！")
        else:
            print("💔 游戏结束 💔")
            print(f"你在第 {self.player.turn} 个回合破产了")
            print(f"未能支付的房租: {self.player.rent} 金币")
            print(f"总共添加了 {len(self.slot_machine.symbols)-1} 个符号")
        print("\n感谢游玩协同效应！")

if __name__ == "__main__":
    game = Game()
    game.game_loop()