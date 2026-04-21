import atlastk
import math
import numpy as np
import re

# 计算器状态
state = {
    "display": "0",
    "expression": "",
    "memory": {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "M": 0},
    "ans": 0,
    "angle_mode": "rad",  # rad / deg / grad
    "mode": "basic",  # basic / matrix / stats / solver
    "shift": False,
    "matrix_a": "",
    "matrix_b": "",
    "matrix_result": "",
    "stats_data": "",
    "stats_result": "",
    "history": [],
    "constants": {
        "c": 299792458, "g": 9.80665, "h": 6.62607015e-34,
        "e": math.e, "pi": math.pi, "NA": 6.02214076e23,
        "k": 1.380649e-23, "R": 8.314462618,
    },
}

BODY = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: "SF Pro", -apple-system, sans-serif;
            background: #0d1117;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 8px;
        }
        .calculator {
            max-width: 560px;
            width: 100%;
            background: #161b22;
            border-radius: 20px;
            padding: 14px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
            border: 1px solid #30363d;
        }
        .brand {
            display: flex;
            justify-content: space-between;
            padding: 0 6px 10px;
            color: #58a6ff;
            font-weight: 600;
            font-size: 13px;
        }
        .display-container {
            background: #0d1117;
            border-radius: 12px;
            padding: 16px 14px;
            margin-bottom: 12px;
            border: 1px solid #30363d;
        }
        #Expression {
            font-size: 13px;
            color: #8b949e;
            text-align: right;
            min-height: 20px;
            font-family: monospace;
        }
        #Display {
            font-size: 34px;
            color: #58a6ff;
            text-align: right;
            font-weight: 500;
            min-height: 48px;
            font-family: "SF Mono", monospace;
            word-break: break-all;
        }
        .indicators {
            display: flex;
            gap: 14px;
            padding: 6px 0 0;
            font-size: 10px;
            color: #6e7681;
        }
        .mode-tabs {
            display: flex;
            gap: 6px;
            margin-bottom: 10px;
        }
        .mode-tab {
            flex: 1;
            padding: 8px;
            border: none;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            background: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
        }
        .mode-tab.active {
            background: #238636;
            color: white;
        }
        .button-panel { display: flex; flex-direction: column; gap: 5px; }
        .button-row { display: flex; gap: 5px; }
        button {
            flex: 1;
            padding: 12px 4px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            background: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
            box-shadow: 0 2px 0 #0d1117;
            transition: all 0.1s;
        }
        button:active { transform: translateY(2px); box-shadow: none; }
        button.num { background: #30363d; color: #f0f6fc; }
        button.operator { background: #1f6feb; color: white; }
        button.func { background: #6e40c9; color: white; }
        button.equal { background: #238636; color: white; }
        button.clear { background: #da3633; color: white; }
        button.memory { background: #9e6a03; color: white; }
        .matrix-panel, .stats-panel {
            margin-top: 12px;
            padding: 14px;
            background: #21262d;
            border-radius: 10px;
        }
        textarea {
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #30363d;
            background: #0d1117;
            color: #c9d1d9;
            font-size: 13px;
            font-family: monospace;
            margin-bottom: 8px;
            resize: vertical;
        }
        .panel-title { color: #f0f6fc; font-weight: 600; margin-bottom: 8px; }
        .result-area {
            background: #0d1117;
            padding: 10px;
            border-radius: 8px;
            color: #58a6ff;
            font-family: monospace;
            margin-top: 10px;
            font-size: 13px;
        }
        .history-panel {
            margin-top: 12px;
            padding: 10px;
            background: #1c2128;
            border-radius: 10px;
            max-height: 100px;
            overflow-y: auto;
        }
        .history-item {
            color: #8b949e;
            font-size: 12px;
            padding: 3px 0;
            border-bottom: 1px solid #30363d;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="calculator">
        <div class="brand">
            <span>🧮 PRO-991EX</span>
            <span id="AngleIndicator">RAD</span>
        </div>
        
        <div class="display-container">
            <div id="Expression"></div>
            <div id="Display">0</div>
            <div class="indicators">
                <span id="ShiftIndicator"> </span>
                <span id="MemIndicator"> </span>
            </div>
        </div>
        
        <div class="mode-tabs">
            <button class="mode-tab active" id="ModeBasic" xdh:onevent="SetModeBasic">基础</button>
            <button class="mode-tab" id="ModeMatrix" xdh:onevent="SetModeMatrix">矩阵</button>
            <button class="mode-tab" id="ModeStats" xdh:onevent="SetModeStats">统计</button>
            <button class="mode-tab" id="ModeSolver" xdh:onevent="SetModeSolver">方程</button>
        </div>
        
        <!-- 基础模式 -->
        <div id="BasicPanel">
            <div class="button-panel">
                <div class="button-row">
                    <button class="clear" xdh:onevent="Clear">AC</button>
                    <button class="clear" xdh:onevent="Backspace">DEL</button>
                    <button class="func" xdh:onevent="PressShift">SHIFT</button>
                    <button class="func" xdh:onevent="PressAns">ANS</button>
                </div>
                <div class="button-row">
                    <button class="func" xdh:onevent="PressSin">sin</button>
                    <button class="func" xdh:onevent="PressCos">cos</button>
                    <button class="func" xdh:onevent="PressTan">tan</button>
                    <button class="operator" xdh:onevent="PressDiv">÷</button>
                </div>
                <div class="button-row">
                    <button class="func" xdh:onevent="PressAsin">sin⁻¹</button>
                    <button class="func" xdh:onevent="PressAcos">cos⁻¹</button>
                    <button class="func" xdh:onevent="PressAtan">tan⁻¹</button>
                    <button class="operator" xdh:onevent="PressMul">×</button>
                </div>
                <div class="button-row">
                    <button class="func" xdh:onevent="PressLog">log</button>
                    <button class="func" xdh:onevent="PressLn">ln</button>
                    <button class="func" xdh:onevent="PressSqrt">√</button>
                    <button class="operator" xdh:onevent="PressSub">−</button>
                </div>
                <div class="button-row">
                    <button class="func" xdh:onevent="PressPow">xʸ</button>
                    <button class="func" xdh:onevent="PressPi">π</button>
                    <button class="func" xdh:onevent="PressE">e</button>
                    <button class="operator" xdh:onevent="PressAdd">+</button>
                </div>
                <div class="button-row">
                    <button class="func" xdh:onevent="PressFact">n!</button>
                    <button class="func" xdh:onevent="PressComb">nCr</button>
                    <button class="func" xdh:onevent="PressPerm">nPr</button>
                    <button class="func" xdh:onevent="ToggleAngle">D/R/G</button>
                </div>
                <div class="button-row">
                    <button class="num" xdh:onevent="PressNum7">7</button>
                    <button class="num" xdh:onevent="PressNum8">8</button>
                    <button class="num" xdh:onevent="PressNum9">9</button>
                    <button class="equal" xdh:onevent="Calculate" style="grid-row: span 2;">=</button>
                </div>
                <div class="button-row">
                    <button class="num" xdh:onevent="PressNum4">4</button>
                    <button class="num" xdh:onevent="PressNum5">5</button>
                    <button class="num" xdh:onevent="PressNum6">6</button>
                </div>
                <div class="button-row">
                    <button class="num" xdh:onevent="PressNum1">1</button>
                    <button class="num" xdh:onevent="PressNum2">2</button>
                    <button class="num" xdh:onevent="PressNum3">3</button>
                    <button class="equal" xdh:onevent="Calculate">=</button>
                </div>
                <div class="button-row">
                    <button class="num" xdh:onevent="PressNum0" style="flex: 2;">0</button>
                    <button class="num" xdh:onevent="PressDot">.</button>
                    <button class="func" xdh:onevent="PressParen">( )</button>
                </div>
                <div class="button-row">
                    <button class="memory" xdh:onevent="MemoryStoreA">A</button>
                    <button class="memory" xdh:onevent="MemoryStoreB">B</button>
                    <button class="memory" xdh:onevent="MemoryStoreC">C</button>
                    <button class="memory" xdh:onevent="MemoryStoreM">M</button>
                </div>
            </div>
        </div>
        
        <!-- 矩阵模式 -->
        <div id="MatrixPanel" style="display: none;" class="matrix-panel">
            <div class="panel-title">矩阵 A</div>
            <textarea id="MatrixA" placeholder="1,2,3;4,5,6;7,8,9" rows="2"></textarea>
            <div class="panel-title">矩阵 B</div>
            <textarea id="MatrixB" placeholder="1,0,0;0,1,0;0,0,1" rows="2"></textarea>
            <div class="button-row" style="margin-top: 10px;">
                <button class="func" xdh:onevent="MatrixAdd">A+B</button>
                <button class="func" xdh:onevent="MatrixSub">A-B</button>
                <button class="func" xdh:onevent="MatrixMul">A×B</button>
                <button class="func" xdh:onevent="MatrixTranspose">Aᵀ</button>
            </div>
            <div class="button-row">
                <button class="func" xdh:onevent="MatrixInv">A⁻¹</button>
                <button class="func" xdh:onevent="MatrixDet">det</button>
                <button class="func" xdh:onevent="MatrixEig">特征值</button>
                <button class="clear" xdh:onevent="MatrixClear">清空</button>
            </div>
            <div id="MatrixResult" class="result-area"></div>
        </div>
        
        <!-- 统计模式 -->
        <div id="StatsPanel" style="display: none;" class="stats-panel">
            <div class="panel-title">数据</div>
            <textarea id="StatsData" placeholder="1,2,3,4,5,6,7,8,9,10" rows="2"></textarea>
            <div class="button-row" style="margin-top: 10px;">
                <button class="func" xdh:onevent="StatsMean">均值</button>
                <button class="func" xdh:onevent="StatsStd">标准差</button>
                <button class="func" xdh:onevent="StatsVar">方差</button>
                <button class="func" xdh:onevent="StatsMedian">中位数</button>
            </div>
            <div class="button-row">
                <button class="func" xdh:onevent="StatsMin">最小</button>
                <button class="func" xdh:onevent="StatsMax">最大</button>
                <button class="func" xdh:onevent="StatsSum">求和</button>
                <button class="clear" xdh:onevent="StatsClear">清空</button>
            </div>
            <div id="StatsResult" class="result-area"></div>
        </div>
        
        <!-- 方程求解 -->
        <div id="SolverPanel" style="display: none;" class="matrix-panel">
            <div class="panel-title">二次方程 ax² + bx + c = 0</div>
            <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                <input type="number" id="CoefA" placeholder="a" style="flex:1; padding:8px; border-radius:6px; background:#0d1117; color:white; border:1px solid #30363d;">
                <input type="number" id="CoefB" placeholder="b" style="flex:1; padding:8px; border-radius:6px; background:#0d1117; color:white; border:1px solid #30363d;">
                <input type="number" id="CoefC" placeholder="c" style="flex:1; padding:8px; border-radius:6px; background:#0d1117; color:white; border:1px solid #30363d;">
            </div>
            <button class="func" xdh:onevent="SolveQuadratic" style="width:100%;">求解</button>
            <div id="SolverResult" class="result-area"></div>
        </div>
        
        <!-- 历史记录 -->
        <div class="history-panel">
            <div id="HistoryList"><div class="history-item">就绪</div></div>
        </div>
    </div>
</body>
</html>
"""

# 辅助函数
def safe_eval(expr):
    namespace = {
        "np": np, "math": math,
        "sin": math.sin if state["angle_mode"] == "rad" else lambda x: math.sin(math.radians(x)),
        "cos": math.cos if state["angle_mode"] == "rad" else lambda x: math.cos(math.radians(x)),
        "tan": math.tan if state["angle_mode"] == "rad" else lambda x: math.tan(math.radians(x)),
        "asin": math.asin if state["angle_mode"] == "rad" else lambda x: math.degrees(math.asin(x)),
        "acos": math.acos if state["angle_mode"] == "rad" else lambda x: math.degrees(math.acos(x)),
        "atan": math.atan if state["angle_mode"] == "rad" else lambda x: math.degrees(math.atan(x)),
        "log": math.log10, "ln": math.log, "sqrt": math.sqrt,
        "pi": math.pi, "e": math.e, "factorial": math.factorial,
        "comb": math.comb, "perm": math.perm,
    }
    try:
        return str(eval(expr, {"__builtins__": {}}, namespace))
    except Exception as e:
        return f"错误"

def parse_matrix(text):
    if not text.strip(): return None
    rows = text.strip().split(";")
    return np.array([[float(x.strip()) for x in row.split(",")] for row in rows])

def update_display(dom):
    dom.setValue("Display", state["display"])
    dom.setValue("Expression", state["expression"])
    dom.setValue("AngleIndicator", {"rad": "RAD", "deg": "DEG", "grad": "GRAD"}[state["angle_mode"]])

def update_mode_ui(dom):
    for m in ["basic", "matrix", "stats", "solver"]:
        dom.removeClass(f"Mode{m.capitalize()}", "active")
        dom.setAttribute(f"{m.capitalize()}Panel", "style", f"display: {'block' if m == state['mode'] else 'none'}")
    dom.addClass(f"Mode{state['mode'].capitalize()}", "active")

def add_history(dom, entry):
    state["history"].append(entry)
    if len(state["history"]) > 8: state["history"] = state["history"][-8:]
    html = "".join(f'<div class="history-item">{h}</div>' for h in reversed(state["history"]))
    dom.inner("HistoryList", html or '<div class="history-item">就绪</div>')

# Atlas 回调
def atk(dom):
    dom.inner("", BODY)
    update_display(dom)
    update_mode_ui(dom)

def atkSetModeBasic(dom): state["mode"] = "basic"; update_mode_ui(dom)
def atkSetModeMatrix(dom): state["mode"] = "matrix"; update_mode_ui(dom)
def atkSetModeStats(dom): state["mode"] = "stats"; update_mode_ui(dom)
def atkSetModeSolver(dom): state["mode"] = "solver"; update_mode_ui(dom)

def atkPressNum0(dom): press_num(dom, "0")
def atkPressNum1(dom): press_num(dom, "1")
def atkPressNum2(dom): press_num(dom, "2")
def atkPressNum3(dom): press_num(dom, "3")
def atkPressNum4(dom): press_num(dom, "4")
def atkPressNum5(dom): press_num(dom, "5")
def atkPressNum6(dom): press_num(dom, "6")
def atkPressNum7(dom): press_num(dom, "7")
def atkPressNum8(dom): press_num(dom, "8")
def atkPressNum9(dom): press_num(dom, "9")

def press_num(dom, num):
    state["display"] = num if state["display"] in ("0", "错误") else state["display"] + num
    state["expression"] = state["display"]
    update_display(dom)

def atkPressDot(dom):
    if "." not in state["display"]: state["display"] += "."; state["expression"] = state["display"]
    update_display(dom)

def atkPressAdd(dom): press_op(dom, "+")
def atkPressSub(dom): press_op(dom, "-")
def atkPressMul(dom): press_op(dom, "*")
def atkPressDiv(dom): press_op(dom, "/")

def press_op(dom, op):
    state["display"] += op; state["expression"] = state["display"]
    update_display(dom)

def atkPressParen(dom):
    open_cnt = state["display"].count("("); close_cnt = state["display"].count(")")
    state["display"] += ")" if open_cnt > close_cnt else "("
    state["expression"] = state["display"]
    update_display(dom)

def atkPressSin(dom): press_func(dom, "sin")
def atkPressCos(dom): press_func(dom, "cos")
def atkPressTan(dom): press_func(dom, "tan")
def atkPressAsin(dom): press_func(dom, "asin")
def atkPressAcos(dom): press_func(dom, "acos")
def atkPressAtan(dom): press_func(dom, "atan")
def atkPressLog(dom): press_func(dom, "log")
def atkPressLn(dom): press_func(dom, "ln")
def atkPressSqrt(dom): press_func(dom, "sqrt")

def press_func(dom, func):
    state["display"] = func + "(" if state["display"] == "0" else state["display"] + func + "("
    state["expression"] = state["display"]
    update_display(dom)

def atkPressPow(dom): state["display"] += "**"; state["expression"] = state["display"]; update_display(dom)
def atkPressPi(dom): state["display"] += "pi"; state["expression"] = state["display"]; update_display(dom)
def atkPressE(dom): state["display"] += "e"; state["expression"] = state["display"]; update_display(dom)
def atkPressFact(dom): press_func(dom, "factorial")
def atkPressComb(dom): press_func(dom, "comb")
def atkPressPerm(dom): press_func(dom, "perm")
def atkPressAns(dom): state["display"] += str(state["ans"]); state["expression"] = state["display"]; update_display(dom)

def atkToggleAngle(dom):
    modes = {"rad": "deg", "deg": "grad", "grad": "rad"}
    state["angle_mode"] = modes[state["angle_mode"]]
    update_display(dom)

def atkClear(dom):
    state["display"] = "0"; state["expression"] = ""
    update_display(dom)

def atkBackspace(dom):
    state["display"] = state["display"][:-1] or "0"
    state["expression"] = state["display"]
    update_display(dom)

def atkCalculate(dom):
    result = safe_eval(state["display"])
    try:
        state["ans"] = float(result)
    except:
        pass
    add_history(dom, f"{state['display']} = {result}")
    state["display"] = result
    state["expression"] = ""
    update_display(dom)

# 矩阵运算
def atkMatrixAdd(dom): matrix_op(dom, lambda a,b: a+b, "A+B")
def atkMatrixSub(dom): matrix_op(dom, lambda a,b: a-b, "A-B")
def atkMatrixMul(dom): matrix_op(dom, lambda a,b: a@b, "A×B")

def matrix_op(dom, op, name):
    try:
        a = parse_matrix(dom.getValue("MatrixA"))
        b = parse_matrix(dom.getValue("MatrixB"))
        if a is None or b is None:
            dom.setValue("MatrixResult", "请输入矩阵")
            return
        result = op(a, b)
        dom.setValue("MatrixResult", str(result))
        add_history(dom, f"{name}: {result}")
    except Exception as e:
        dom.setValue("MatrixResult", f"错误: {e}")

def atkMatrixTranspose(dom):
    try:
        a = parse_matrix(dom.getValue("MatrixA"))
        if a is None: dom.setValue("MatrixResult", "请输入矩阵A"); return
        result = a.T
        dom.setValue("MatrixResult", str(result))
        add_history(dom, f"Aᵀ: {result}")
    except Exception as e:
        dom.setValue("MatrixResult", f"错误: {e}")

def atkMatrixInv(dom):
    try:
        a = parse_matrix(dom.getValue("MatrixA"))
        if a is None: dom.setValue("MatrixResult", "请输入矩阵A"); return
        result = np.linalg.inv(a)
        dom.setValue("MatrixResult", str(result))
        add_history(dom, f"A⁻¹: {result}")
    except Exception as e:
        dom.setValue("MatrixResult", f"不可逆: {e}")

def atkMatrixDet(dom):
    try:
        a = parse_matrix(dom.getValue("MatrixA"))
        result = np.linalg.det(a)
        dom.setValue("MatrixResult", str(result))
        add_history(dom, f"det(A) = {result}")
    except Exception as e:
        dom.setValue("MatrixResult", f"错误: {e}")

def atkMatrixEig(dom):
    try:
        a = parse_matrix(dom.getValue("MatrixA"))
        result = np.linalg.eigvals(a)
        dom.setValue("MatrixResult", str(result))
        add_history(dom, f"特征值: {result}")
    except Exception as e:
        dom.setValue("MatrixResult", f"错误: {e}")

def atkMatrixClear(dom):
    dom.setValue("MatrixA", ""); dom.setValue("MatrixB", ""); dom.setValue("MatrixResult", "")

# 统计
def get_stats_data(dom):
    text = dom.getValue("StatsData")
    return np.array([float(x) for x in re.split(r"[,\s]+", text.strip()) if x])

def atkStatsMean(dom):
    try:
        data = get_stats_data(dom)
        result = np.mean(data)
        dom.setValue("StatsResult", f"均值: {result}")
        add_history(dom, f"均值 = {result}")
    except Exception as e:
        dom.setValue("StatsResult", f"错误: {e}")

def atkStatsStd(dom):
    try:
        data = get_stats_data(dom)
        result = np.std(data)
        dom.setValue("StatsResult", f"标准差: {result}")
        add_history(dom, f"标准差 = {result}")
    except Exception as e:
        dom.setValue("StatsResult", f"错误: {e}")

def atkStatsVar(dom):
    try:
        data = get_stats_data(dom)
        result = np.var(data)
        dom.setValue("StatsResult", f"方差: {result}")
        add_history(dom, f"方差 = {result}")
    except Exception as e:
        dom.setValue("StatsResult", f"错误: {e}")

def atkStatsMedian(dom):
    try:
        data = get_stats_data(dom)
        result = np.median(data)
        dom.setValue("StatsResult", f"中位数: {result}")
        add_history(dom, f"中位数 = {result}")
    except Exception as e:
        dom.setValue("StatsResult", f"错误: {e}")

def atkStatsMin(dom):
    try:
        data = get_stats_data(dom)
        result = np.min(data)
        dom.setValue("StatsResult", f"最小值: {result}")
    except Exception as e:
        dom.setValue("StatsResult", f"错误: {e}")

def atkStatsMax(dom):
    try:
        data = get_stats_data(dom)
        result = np.max(data)
        dom.setValue("StatsResult", f"最大值: {result}")
    except Exception as e:
        dom.setValue("StatsResult", f"错误: {e}")

def atkStatsSum(dom):
    try:
        data = get_stats_data(dom)
        result = np.sum(data)
        dom.setValue("StatsResult", f"求和: {result}")
    except Exception as e:
        dom.setValue("StatsResult", f"错误: {e}")

def atkStatsClear(dom):
    dom.setValue("StatsData", ""); dom.setValue("StatsResult", "")

# 方程求解
def atkSolveQuadratic(dom):
    try:
        a = float(dom.getValue("CoefA") or 0)
        b = float(dom.getValue("CoefB") or 0)
        c = float(dom.getValue("CoefC") or 0)
        if a == 0:
            dom.setValue("SolverResult", "a不能为0")
            return
        delta = b**2 - 4*a*c
        if delta >= 0:
            x1 = (-b + math.sqrt(delta)) / (2*a)
            x2 = (-b - math.sqrt(delta)) / (2*a)
            result = f"x₁ = {x1:.6f}, x₂ = {x2:.6f}"
        else:
            real = -b / (2*a)
            imag = math.sqrt(-delta) / (2*a)
            result = f"x₁ = {real:.6f} + {imag:.6f}i, x₂ = {real:.6f} - {imag:.6f}i"
        dom.setValue("SolverResult", result)
        add_history(dom, f"{a}x²+{b}x+{c}=0 → {result}")
    except Exception as e:
        dom.setValue("SolverResult", f"错误: {e}")

# 记忆功能
def atkMemoryStoreA(dom):
    try: state["memory"]["A"] = float(state["display"]); dom.setValue("MemIndicator", "A已存")
    except: pass

def atkMemoryStoreB(dom):
    try: state["memory"]["B"] = float(state["display"]); dom.setValue("MemIndicator", "B已存")
    except: pass

def atkMemoryStoreC(dom):
    try: state["memory"]["C"] = float(state["display"]); dom.setValue("MemIndicator", "C已存")
    except: pass

def atkMemoryStoreM(dom):
    try: state["memory"]["M"] = float(state["display"]); dom.setValue("MemIndicator", "M已存")
    except: pass

def atkPressShift(dom):
    state["shift"] = not state["shift"]
    dom.setValue("ShiftIndicator", "SHIFT" if state["shift"] else " ")

# 启动
atlastk.launch(globals=globals())