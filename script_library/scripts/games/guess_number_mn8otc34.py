import random

def guess_number_game():
    """
    猜数字游戏
    随机生成1-100的整数，玩家猜测直到猜对为止
    """
    # 生成随机数
    secret_number = random.randint(1, 100)
    attempts = 0
    guess_history = []  # 记录猜测历史
    
    print("🎮 欢迎来到猜数字游戏！")
    print("我已经想好了一个1到100之间的整数。")
    print("试着猜猜看是多少吧！")
    print("提示：输入 'q' 可以退出游戏")
    print("-" * 40)
    
    while True:
        try:
            # 获取玩家输入
            guess_input = input(f"第{attempts+1}次猜测（1-100）：")
            
            # 检查是否要退出
            if guess_input.lower() in ['q', 'quit', 'exit', '退出']:
                print(f"\n👋 游戏已退出。正确答案是 {secret_number}")
                print(f"你猜了 {attempts} 次，猜测历史：{guess_history}")
                return False
            
            guess = int(guess_input)
            
            # 验证输入范围
            if guess < 1 or guess > 100:
                print("⚠️  请输入1到100之间的数字！")
                continue
            
            attempts += 1
            guess_history.append(guess)
            
            # 判断猜测结果
            if guess < secret_number:
                print("🔽 小了！再试试看。")
            elif guess > secret_number:
                print("🔼 大了！再试试看。")
            else:
                print(f"\n🎉 恭喜你！猜对了！")
                print(f"🎯 正确答案是：{secret_number}")
                print(f"📊 你总共猜了 {attempts} 次")
                print(f"📝 猜测历史：{guess_history}")
                
                # 根据尝试次数给出评价
                if attempts == 1:
                    print("🌟 太厉害了！一次就猜中！")
                elif attempts <= 5:
                    print("👍 很棒！只用了很少的次数！")
                elif attempts <= 10:
                    print("👌 不错！表现很好！")
                else:
                    print("💪 继续努力，下次会更好！")
                
                return True
                
        except ValueError:
            print("❌ 请输入有效的数字！或者输入 q 退出游戏")
        except KeyboardInterrupt:
            print("\n\n👋 游戏已退出。")
            return False

def show_instructions():
    """显示游戏说明"""
    print("\n📖 游戏说明：")
    print("1. 我会随机生成一个1-100之间的整数")
    print("2. 你需要猜测这个数字是多少")
    print("3. 每次猜测后，我会告诉你'大了'或'小了'")
    print("4. 继续猜测直到猜对为止")
    print("5. 游戏会记录你猜的次数")
    print("6. 输入 'q' 可以随时退出游戏")
    print("-" * 40)

def main():
    """主函数，控制游戏流程"""
    print("=" * 50)
    print("           猜数字游戏 v1.0")
    print("=" * 50)
    
    show_instructions()
    
    total_games = 0
    total_attempts = 0
    best_score = float('inf')  # 最佳成绩（最少尝试次数）
    
    while True:
        total_games += 1
        print(f"\n🎲 第 {total_games} 局游戏开始！")
        
        # 玩一局游戏
        game_completed = guess_number_game()
        
        # 询问是否再玩一次
        print("\n" + "=" * 40)
        play_again = input("想再玩一次吗？(y/n): ").lower()
        
        if play_again not in ['y', 'yes', '是', '好的']:
            # 显示统计信息
            print("\n📈 游戏统计：")
            print(f"  总游戏局数：{total_games}")
            if total_games > 0 and total_attempts > 0:
                print(f"  平均尝试次数：{total_attempts/total_games:.1f}")
                if best_score < float('inf'):
                    print(f"  最佳成绩：{best_score} 次")
            print("\n谢谢游玩！再见！👋")
            break
        print("\n" + "=" * 40)

if __name__ == "__main__":
    main()