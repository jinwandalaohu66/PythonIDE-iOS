import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoLocator
import math
import re

# ---------------------------- 表达式预处理（支持省略乘号） ----------------------------
def preprocess_expr(expr: str) -> str:
    """将数学表达式转换为Python可eval的形式，自动插入*号"""
    expr = expr.replace('π', 'math.pi').replace('e', 'math.e')
    expr = expr.replace('^', '**')
    # 插入隐式乘号：数字与字母/括号之间、字母与字母/括号之间、括号与数字/字母之间
    pattern = r'(?<=[0-9])(?=[a-zA-Z(])|(?<=[a-zA-Z)])(?=[0-9a-zA-Z(])'
    expr = re.sub(pattern, '*', expr)
    return expr

# ---------------------------- 主应用类 ----------------------------
class FunctionPlotter:
    def __init__(self, master):
        self.master = master
        master.title("函数图像绘制器")
        master.geometry("500x700")
        master.configure(bg="#f0f0f0")
        master.minsize(450, 600)

        self.mode = 'linear'          # 'linear' 或 'quadratic'
        self.animation = None
        self.current_line = None
        self.fig = None
        self.ax = None
        self.canvas = None

        self.create_widgets()
        self.init_plot()

    def create_widgets(self):
        # ---------- 顶部模式切换按钮 ----------
        top_frame = tk.Frame(self.master, bg="#f0f0f0", pady=10)
        top_frame.pack(fill=tk.X)

        self.btn_linear = tk.Button(
            top_frame, text="📈 一次函数", font=("微软雅黑", 12, "bold"),
            bg="#e0e0e0", fg="#333", padx=20, pady=5, relief=tk.RAISED,
            command=lambda: self.switch_mode('linear')
        )
        self.btn_linear.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

        self.btn_quadratic = tk.Button(
            top_frame, text="📉 二次函数", font=("微软雅黑", 12, "bold"),
            bg="#e0e0e0", fg="#333", padx=20, pady=5, relief=tk.RAISED,
            command=lambda: self.switch_mode('quadratic')
        )
        self.btn_quadratic.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=10)

        self.update_button_style()

        # ---------- 输入区域 ----------
        input_frame = tk.Frame(self.master, bg="#f0f0f0", pady=10)
        input_frame.pack(fill=tk.X, padx=15)

        tk.Label(input_frame, text="函数表达式：y=", font=("微软雅黑", 10), bg="#f0f0f0").pack(anchor=tk.W)
        self.entry = tk.Entry(input_frame, font=("Consolas", 12), bg="white")
        self.entry.pack(fill=tk.X, pady=(5,10))
        self.entry.insert(0, "x+1")

        self.plot_btn = tk.Button(
            input_frame, text="🎨 绘制图像", font=("微软雅黑", 10, "bold"),
            bg="#4caf50", fg="white", padx=10, pady=5,
            command=self.start_plot_animation
        )
        self.plot_btn.pack()

        # ---------- 数学符号面板 ----------
        symbol_frame = tk.LabelFrame(self.master, text="数学符号库", font=("微软雅黑", 9), bg="#f0f0f0", padx=5, pady=5)
        symbol_frame.pack(fill=tk.X, padx=15, pady=5)

        symbols = ['x', 'x^2', 'x^3', '+', '-', '*', '/', '(', ')', 'π', 'e',
                   'sin', 'cos', 'tan', 'sqrt', '^', '**']
        row, col = 0, 0
        for sym in symbols:
            btn = tk.Button(
                symbol_frame, text=sym, font=("Consolas", 9), width=5, relief=tk.GROOVE,
                command=lambda s=sym: self.insert_symbol(s)
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            col += 1
            if col >= 6:
                col = 0
                row += 1
        for i in range(6):
            symbol_frame.columnconfigure(i, weight=1)

        # ---------- 状态栏 ----------
        self.status = tk.Label(self.master, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#e0e0e0")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def init_plot(self):
        """初始化 matplotlib 图形，设置坐标轴样式和固定刻度间隔为1"""
        self.fig = Figure(figsize=(6, 4), dpi=100, facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.axhline(0, color='k', linewidth=0.8)
        self.ax.axvline(0, color='k', linewidth=0.8)
        self.ax.set_xlabel('x', fontsize=10)
        self.ax.set_ylabel('y', fontsize=10)
        self.ax.set_title('函数图像', fontsize=12)

        # x轴固定刻度间隔1，范围-10~10
        self.ax.set_xlim(-10, 10)
        self.ax.xaxis.set_major_locator(MultipleLocator(1))
        self.ax.xaxis.set_minor_locator(MultipleLocator(0.5))

        # y轴暂用自动，绘图时会根据数据重新调整
        self.ax.yaxis.set_major_locator(AutoLocator())
        self.fig.tight_layout()
        self.canvas.draw()

    def update_button_style(self):
        if self.mode == 'linear':
            self.btn_linear.config(bg="#4caf50", fg="white", relief=tk.SUNKEN)
            self.btn_quadratic.config(bg="#e0e0e0", fg="#333", relief=tk.RAISED)
        else:
            self.btn_quadratic.config(bg="#4caf50", fg="white", relief=tk.SUNKEN)
            self.btn_linear.config(bg="#e0e0e0", fg="#333", relief=tk.RAISED)

    def switch_mode(self, mode):
        if self.mode == mode:
            return
        self.mode = mode
        self.update_button_style()
        if mode == 'linear':
            default_expr = "2x+3"
        else:
            default_expr = "x^2+2x+1"
        self.entry.delete(0, tk.END)
        self.entry.insert(0, default_expr)
        self.status.config(text=f"已切换到{'一次' if mode=='linear' else '二次'}函数模式")
        self.entry.config(bg="#ffffcc")
        self.master.after(200, lambda: self.entry.config(bg="white"))

    def insert_symbol(self, symbol):
        pos = self.entry.index(tk.INSERT)
        text = self.entry.get()
        new_text = text[:pos] + symbol + text[pos:]
        self.entry.delete(0, tk.END)
        self.entry.insert(0, new_text)
        self.entry.icursor(pos + len(symbol))
        self.entry.focus_set()

    def evaluate_expression(self, expr_str, x_vals):
        """计算表达式值，返回y数组，若全部无效则返回None"""
        try:
            processed = preprocess_expr(expr_str)
            namespace = {
                'math': math,
                'np': np,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'pi': math.pi,
                'e': math.e
            }
            code = compile(f'lambda x: {processed}', '<string>', 'eval')
            f = eval(code, namespace)
            y_vals = []
            for x in x_vals:
                try:
                    y = f(x)
                    if isinstance(y, complex) or not np.isfinite(y):
                        y = np.nan
                    y_vals.append(y)
                except:
                    y_vals.append(np.nan)
            y_arr = np.array(y_vals)
            if np.all(np.isnan(y_arr)):
                messagebox.showerror("无效表达式", "表达式在所有x上均无有效值，请检查输入。")
                return None
            return y_arr
        except Exception as e:
            messagebox.showerror("表达式错误", f"解析表达式出错：\n{str(e)}")
            return None

    def start_plot_animation(self):
        """启动绘图动画，确保曲线正常显示"""
        # 停止旧动画
        if self.animation is not None:
            try:
                self.animation.event_source.stop()
            except:
                pass
            self.animation = None

        expr = self.entry.get().strip()
        if not expr:
            messagebox.showwarning("空表达式", "请输入函数表达式")
            return

        # 生成x点并计算y值
        x_vals = np.linspace(-10, 10, 200)
        y_vals = self.evaluate_expression(expr, x_vals)
        if y_vals is None:
            return

        # 清除旧曲线
        if self.current_line is not None:
            self.current_line.remove()
            self.current_line = None

        # 动态调整y轴范围（过滤无效点）
        valid_mask = ~np.isnan(y_vals)
        if np.any(valid_mask):
            y_min = np.nanmin(y_vals[valid_mask])
            y_max = np.nanmax(y_vals[valid_mask])
            y_range = y_max - y_min
            if y_range < 1e-6:
                y_min -= 1
                y_max += 1
            else:
                y_min -= 0.1 * y_range
                y_max += 0.1 * y_range
            self.ax.set_ylim(y_min, y_max)
            # 设置y轴刻度间隔为1（如果范围太大则自动调整）
            if y_max - y_min <= 20:
                self.ax.yaxis.set_major_locator(MultipleLocator(1))
            else:
                self.ax.yaxis.set_major_locator(MultipleLocator(5))
            self.ax.yaxis.set_minor_locator(MultipleLocator(1))
        else:
            self.ax.set_ylim(-5, 5)

        # 创建空曲线（占位）
        self.current_line, = self.ax.plot([], [], 'b-', linewidth=2, label=f'y = {expr}')
        self.ax.legend(loc='upper right')
        self.canvas.draw()

        # 动画参数
        self.total_points = len(x_vals)
        self.x_data = x_vals
        self.y_data = y_vals
        self.step = 0

        # 动画更新函数
        def animate(i):
            self.step = min(self.total_points, self.step + 5)
            if self.step >= 1:
                self.current_line.set_data(self.x_data[:self.step], self.y_data[:self.step])
                # 强制刷新画布
                self.canvas.draw_idle()
                self.canvas.flush_events()
            if self.step >= self.total_points:
                self.animation.event_source.stop()
                self.status.config(text="绘图完成")
            return self.current_line,

        from matplotlib.animation import FuncAnimation
        # 帧数 = 总点数/5 + 1
        frames = self.total_points // 5 + 1
        self.animation = FuncAnimation(
            self.fig, animate, frames=frames,
            interval=30, repeat=False, blit=False
        )
        self.status.config(text="正在绘制动画...")

        # 备用机制：如果动画因故未显示，强制重绘一次（极少情况）
        def fallback_draw():
            if self.current_line is not None and len(self.current_line.get_xdata()) == 0:
                self.current_line.set_data(self.x_data, self.y_data)
                self.canvas.draw()
                self.status.config(text="已绘制完整曲线")
        self.master.after(500, fallback_draw)  # 0.5秒后若仍无数据则直接画全

        # 动画结束后启用按钮（粗略延时）
        def enable_btn():
            self.plot_btn.config(state=tk.NORMAL)
        self.plot_btn.config(state=tk.DISABLED)
        self.master.after(2000, enable_btn)

# ---------------------------- 主程序 ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FunctionPlotter(root)
    root.mainloop()