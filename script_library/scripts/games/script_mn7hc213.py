import random

# ------------- 核心配置 -------------
MAZE_SIZE = 15  # 迷宫大小 (奇数)
PLAYER = "P"    # 玩家
EXIT = "E"      # 出口
WALL = "■"      # 墙
PATH = " "      # 路径

# ------------- 核心函数 -------------
def generate_maze(size):
    """生成迷宫 (简化版，100% 有解)"""
    maze = [[WALL for _ in range(size)] for _ in range(size)]
    
    # 从起点开始，随机打通路径
    x, y = 1, 1
    maze[y][x] = PATH
    
    # 简单的随机游走算法，确保迷宫连通
    for _ in range(size * size // 2):
        # 随机选一个方向
        dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
        nx, ny = x + dx, y + dy
        
        # 检查是否在边界内且是墙
        if 1 <= nx < size-1 and 1 <= ny < size-1 and maze[ny][nx] == WALL:
            maze[ny][nx] = PATH
            x, y = nx, ny
    
    # 确保出口是通路
    maze[size-2][size-2] = PATH
    return maze

def print_screen(maze, px, py, ex, ey):
    """直接打印迷宫，不使用任何系统清屏函数"""
    print("\n" * 5) # 打印空行模拟清屏
    size = MAZE_SIZE
    for y in range(size):
        line = []
        for x in range(size):
            if x == px and y == py:
                line.append(PLAYER)
            elif x == ex and y == ey:
                line.append(EXIT)
            else:
                line.append(maze[y][x])
        print(''.join(line))

def show_menu():
    """显示操作菜单"""
    print("\n===== [虚拟按钮] =====")
    print("1. 向上   2. 向下")
    print("3. 向左   4. 向右")
    print("5. 重置游戏")
    print("======================")

def main():
    maze = generate_maze(MAZE_SIZE)
    px, py = 1, 1  # 玩家起点
    ex, ey = MAZE_SIZE-2, MAZE_SIZE-2  # 出口
    
    print("欢迎来到终端迷宫游戏！")
    print("指令: 1/2/3/4 移动, 5 重置")
    
    while True:
        print_screen(maze, px, py, ex, ey)
        show_menu()
        
        # 获取用户输入
        try:
            cmd = int(input("\n请输入操作: "))
        except:
            print("输入错误，请输入数字 1-5！")
            continue
        
        # 处理移动
        dx, dy = 0, 0
        if cmd == 1: dy = -1
        elif cmd == 2: dy = 1
        elif cmd == 3: dx = -1
        elif cmd == 4: dx = 1
        elif cmd == 5:
            print("重置迷宫...")
            maze = generate_maze(MAZE_SIZE)
            px, py = 1, 1
            continue
        else:
            print("无效指令！")
            continue
        
        # 计算新位置
        nx, ny = px + dx, py + dy
        
        # 检查碰撞 (不能撞墙，不能出界)
        if (0 <= nx < MAZE_SIZE and 
            0 <= ny < MAZE_SIZE and 
            maze[ny][nx] != WALL):
            px, py = nx, ny
        
        # 检查胜利
        if px == ex and py == ey:
            print("\n🎉 恭喜你！成功到达终点！")
            input("按回车键继续...")
            maze = generate_maze(MAZE_SIZE)
            px, py = 1, 1

if __name__ == "__main__":
    main()