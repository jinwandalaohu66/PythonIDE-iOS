# Python IDE — UI 模块完整文档

> Pythonista 兼容的 iOS 原生界面模块。在 iPhone 和 iPad 上使用 Python 创建原生 UIKit 界面，无需额外安装任何库。

---

## 目录

1. [概述](#1-概述)
2. [架构说明](#2-架构说明)
3. [快速开始](#3-快速开始)
4. [View 基础](#4-view-基础)
5. [present 与展示](#5-present-与展示)
6. [Button 按钮](#6-button-按钮)
7. [Label 标签](#7-label-标签)
8. [TextField 单行输入框](#8-textfield-单行输入框)
9. [TextView 多行文本](#9-textview-多行文本)
10. [ImageView 图片视图](#10-imageview-图片视图)
11. [Switch 开关](#11-switch-开关)
12. [Slider 滑块](#12-slider-滑块)
13. [SegmentedControl 分段控件](#13-segmentedcontrol-分段控件)
14. [DatePicker 日期选择器](#14-datepicker-日期选择器)
15. [ScrollView 滚动视图](#15-scrollview-滚动视图)
16. [TableView 表格视图](#16-tableview-表格视图)
17. [WebView 网页视图](#17-webview-网页视图)
18. [ActivityIndicator 加载指示器](#18-activityindicator-加载指示器)
19. [NavigationView 导航视图](#19-navigationview-导航视图)
20. [自定义 View 与绘图](#20-自定义-view-与绘图)
21. [load_view 与 load_view_str](#21-load_view-与-load_view_str)
22. [animate 与工具函数](#22-animate-与工具函数)
23. [常量与枚举](#23-常量与枚举)
24. [常见问题与排错](#24-常见问题与排错)

---

## 1. 概述

Python IDE 内置的 `ui` 模块提供与 [Pythonista](https://omz-software.com/pythonista/) 高度兼容的 iOS 原生界面能力。你可以在 Python 脚本中创建视图、按钮、标签、文本框、图片、列表等控件，并通过 `present()` 以全屏、半屏或弹出框形式展示，完全使用系统原生 UIKit 组件，无需 WebView 或跨平台框架。

### 主要特性

- **完全 Pythonista 兼容**：常用 API 与 Pythonista 保持一致，方便脚本迁移
- **真实 UIKit 渲染**：所有控件均为 iOS 原生组件，性能与系统 App 一致
- **无需安装**：`import ui` 即可使用，内置于 Python IDE
- **支持自绘**：可通过 `draw()`、`ImageContext`、`Path` 等 API 进行自定义绘图
- **支持 .pyui 文件**：可使用 JSON 或 plist 格式的界面描述文件快速构建界面

### 支持的控件一览

| 控件 | 类名 | 说明 |
|------|------|------|
| 基础视图 | `ui.View` | 所有视图的基类，可设置 frame、背景色、圆角等 |
| 按钮 | `ui.Button` | 可设置标题、颜色、点击回调 |
| 标签 | `ui.Label` | 显示单行或多行文本，支持字体、对齐 |
| 单行输入 | `ui.TextField` | 单行文本输入框 |
| 多行文本 | `ui.TextView` | 多行可编辑文本，支持 delegate |
| 图片 | `ui.ImageView` | 显示图片，支持网络加载 |
| 开关 | `ui.Switch` | 布尔开关控件 |
| 滑块 | `ui.Slider` | 0~1 连续数值滑块 |
| 分段控件 | `ui.SegmentedControl` | 多个选项切换 |
| 日期选择器 | `ui.DatePicker` | 日期/时间/日期时间选择 |
| 滚动视图 | `ui.ScrollView` | 可滚动内容区域，支持 delegate |
| 表格视图 | `ui.TableView` | 列表展示，支持 data_source、action、delegate |
| 网页视图 | `ui.WebView` | 加载 URL 或 HTML，支持 eval_js |
| 加载指示器 | `ui.ActivityIndicator` | 转圈加载动画 |
| 导航视图 | `ui.NavigationView` | 带导航栏的栈式页面管理 |
| 画布视图 | `ui.CanvasView` | 自绘视图，重写 draw 方法 |

---

## 2. 架构说明

### 调用流程

```
Python (ui.py)
    ↓ ctypes 调用 C 函数
Swift (UIBridge.swift) — 导出 @_cdecl 的 C 接口
    ↓
Swift (UIModule.swift) — UIViewWrapper、UICallbackManager
    ↓
UIKit (UIView、UIButton、UILabel、...)
```

- **Python 侧**：`pyboot/ui.py` 通过 `ctypes.CDLL(None)` 加载主程序符号，调用 `ui_create_view`、`ui_set_frame` 等 C 函数
- **Swift 侧**：`UIBridge.swift` 导出所有 `ui_*` C 函数，内部调用 `UIBridge.shared` 的对应方法
- **回调机制**：当用户点击按钮、选择表格行等时，Swift 通过 `UICallbackManager.triggerCallback` 执行 Python 代码，Python 通过 `ui._callbacks[callbackID]` 查找并调用注册的回调函数

### 视图 ID

每个创建的视图在 Swift 端都有一个唯一的 `view_id`（字符串），Python 侧通过 `_view_id` 属性持有。所有属性设置、方法调用都会把 `_view_id` 传给 C 接口，以便 Swift 找到对应的原生视图。

---

## 3. 快速开始

### 最简示例：弹出一个带按钮的界面

```python
import ui

# 创建根视图
v = ui.View()
v.background_color = 'white'
v.frame = (0, 0, 300, 400)

# 创建按钮
btn = ui.Button(title='点击我')
btn.frame = (50, 150, 200, 50)
btn.action = lambda sender: print('按钮被点击了')

# 将按钮添加到根视图
v.add_subview(btn)

# 以 sheet 形式展示（从底部弹出的半屏）
v.present('sheet')
```

**运行方式**：在 Python IDE 编辑器中打开此脚本，点击右下角运行按钮，即可看到原生界面弹出。

### 带标题的展示

```python
import ui

v = ui.View()
v.background_color = 'white'
v.frame = (0, 0, 320, 480)
v.title = '我的界面'  # 设置展示时的导航栏标题

btn = ui.Button(title='关闭')
btn.frame = (110, 200, 100, 44)
def on_close(sender):
    v.close()
btn.action = on_close
v.add_subview(btn)

v.present('sheet')
```

---

## 4. View 基础

所有控件的基类，提供位置、尺寸、颜色、子视图管理等功能。

### 创建

```python
v = ui.View()
v = ui.View(frame=(0, 0, 320, 480))  # 可指定初始 frame
```

### 属性（完整列表）

| 属性 | 类型 | 说明 |
|------|------|------|
| `frame` | `(x, y, width, height)` | 视图在其父视图中的位置和尺寸，单位为点（pt） |
| `bounds` | `(x, y, width, height)` | 相对于自身坐标系的矩形，只读，通常为 (0, 0, width, height) |
| `center` | `(x, y)` | 视图中心点在父视图中的坐标 |
| `x` | `float` | frame 的 x，即左边距 |
| `y` | `float` | frame 的 y，即上边距 |
| `width` | `float` | frame 的宽度 |
| `height` | `float` | frame 的高度 |
| `background_color` | `str` 或 `tuple` | 背景颜色，见下方颜色格式 |
| `bg_color` | 同上 | `background_color` 的别名 |
| `alpha` | `float` | 透明度，0.0（完全透明）~ 1.0（不透明） |
| `hidden` | `bool` | 是否隐藏视图 |
| `corner_radius` | `float` | 圆角半径，0 表示直角 |
| `border_width` | `float` | 边框宽度 |
| `border_color` | `str` 或 `tuple` | 边框颜色 |
| `content_mode` | `int` | 内容缩放模式，见常量 `CONTENT_*` |
| `tint_color` | `str` 或 `tuple` | 着色颜色，影响子控件等 |
| `flex` | `str` | 自动调整规则，如 `'W'` 宽度、`'H'` 高度、`'WH'` 宽高、`'TRBL'` 四边等 |
| `name` | `str` | 视图名称，用于 load_view 绑定和 `view['name']` 查找 |
| `touch_enabled` | `bool` | 是否响应触摸，默认 True |
| `multitouch_enabled` | `bool` | 是否支持多点触控，默认 False |
| `transform` | `ui.Transform` 或 `None` | 仿射变换 |
| `title` | `str` | 展示时的导航栏标题（present 时生效） |
| `left_button_items` | `tuple` | 导航栏左侧按钮项列表 |
| `right_button_items` | `tuple` | 导航栏右侧按钮项列表 |

### 颜色格式

支持以下格式：

```python
v.background_color = 'white'           # 预设名称
v.background_color = 'red'
v.background_color = (1, 0, 0, 1)     # RGBA，每通道 0~1
v.background_color = (1, 0, 0, 0.5)   # 半透明红
v.background_color = '#ff0000'        # 十六进制，6 位或 8 位
v.background_color = '#ff000080'      # 含 alpha
```

### 方法

| 方法 | 说明 |
|------|------|
| `add_subview(v)` | 将视图 `v` 添加为子视图 |
| `remove_subview(v)` | 从子视图中移除 `v` |
| `remove_from_superview()` | 从父视图中移除自己 |
| `bring_to_front()` | 移到同层级最前面 |
| `send_to_back()` | 移到同层级最后面 |
| `set_needs_display()` | 标记需要重绘（自定义 View 的 draw 会被调用） |

### 只读属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `subviews` | `tuple` | 所有子视图的元组 |
| `superview` | `View` 或 `None` | 父视图 |

### 按名称查找子视图

```python
v.add_subview(btn)
btn.name = 'submit_btn'
# 稍后可通过名称查找
found = v['submit_btn']  # 等同于按 name 遍历 subviews
```

### 示例：创建一个带圆角和边框的卡片视图

```python
import ui

card = ui.View()
card.frame = (20, 100, 280, 150)
card.background_color = 'white'
card.corner_radius = 12
card.border_width = 1
card.border_color = (0.8, 0.8, 0.8, 1)

label = ui.Label(text='卡片内容')
label.frame = (20, 20, 240, 30)
card.add_subview(label)
```

---

## 5. present 与展示

### present 方法

```python
v.present(style='fullscreen', animated=True, hide_title_bar=False)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `style` | `str` | 展示样式：`'fullscreen'`、`'full_screen'`（同上）、`'sheet'`、`'popover'` |
| `animated` | `bool` | 是否使用过渡动画，默认 True |
| `hide_title_bar` | `bool` | 是否隐藏导航栏标题栏，默认 False |

### 展示样式说明

- **fullscreen**：全屏展示，占据整个屏幕
- **sheet**：从底部弹出的半屏模态，可下滑关闭
- **popover**：弹出框样式（iPad 上更常用）

### 关闭视图

```python
v.close()           # 关闭当前展示的视图
ui.close_all()      # 关闭所有已展示的界面
ui.close_all(animated=False)  # 无动画关闭
```

### 阻塞等待关闭

```python
v.present('sheet')
v.wait_modal()  # 阻塞直到用户关闭视图，常用于需要等待用户操作后再继续的流程
```

### NavigationView：栈式导航

```python
import ui

root = ui.View()
root.background_color = 'white'
root.frame = (0, 0, 320, 480)

nv = ui.NavigationView(root)
nv.navigation_bar_hidden = False   # 是否隐藏导航栏
nv.bar_tint_color = 'white'       # 导航栏背景色

# 推入新页面
def go_next(sender):
    next_view = ui.View()
    next_view.background_color = 'white'
    next_view.frame = (0, 0, 320, 480)
    nv.push_view(next_view, animated=True)

btn = ui.Button(title='下一页')
btn.frame = (110, 200, 100, 44)
btn.action = go_next
root.add_subview(btn)

nv.present('sheet')
```

| 方法 | 说明 |
|------|------|
| `push_view(view, animated=True)` | 将新视图推入导航栈 |
| `pop_view(animated=True)` | 弹出当前视图，返回上一页 |

---

## 6. Button 按钮

### 创建

```python
btn = ui.Button()
btn = ui.Button(title='确定')
btn = ui.Button(frame=(50, 100, 200, 44))
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `title` | `str` | 按钮标题文字 |
| `title_color` | `str` 或 `tuple` | 标题颜色 |
| `enabled` | `bool` | 是否可点击，默认 True |

### action 回调

点击按钮时调用，接收一个参数 `sender`（即按钮本身）：

```python
def on_tap(sender):
    print('按钮被点击')
    print(sender.title)

btn.action = on_tap
# 或使用 lambda
btn.action = lambda s: print(s.title)
```

### 完整示例

```python
import ui

v = ui.View()
v.background_color = 'white'
v.frame = (0, 0, 300, 400)

btn = ui.Button(title='提交')
btn.frame = (50, 150, 200, 44)
btn.title_color = 'blue'
btn.enabled = True
btn.action = lambda s: print('提交')
v.add_subview(btn)

v.present('sheet')
```

---

## 7. Label 标签

### 创建

```python
lbl = ui.Label()
lbl = ui.Label(text='Hello')
lbl = ui.Label(frame=(10, 10, 300, 40))
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `text` | `str` | 显示的文本 |
| `text_color` | `str` 或 `tuple` | 文字颜色 |
| `font` | `(name, size)` 或 `str` | 字体，如 `('Helvetica', 17)`、`(' ', 17)` 表示系统字体 |
| `alignment` | `int` | 对齐：0 左、1 中、2 右 |
| `number_of_lines` | `int` | 最大行数，0 表示不限制 |
| `line_break_mode` | `int` | 换行模式 |
| `adjusts_font_size_to_fit` | `bool` | 是否自动缩小字体以适应 |
| `minimum_scale_factor` | `float` | 自动缩小时的最小比例 |

### 示例

```python
lbl = ui.Label(text='标题')
lbl.frame = (20, 20, 280, 40)
lbl.font = ('Helvetica', 24)
lbl.alignment = 1  # 居中
lbl.text_color = 'black'
```

---

## 8. TextField 单行输入框

### 创建

```python
tf = ui.TextField()
tf = ui.TextField(placeholder='请输入')
tf = ui.TextField(text='初始值')
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `text` | `str` | 当前输入的文本 |
| `placeholder` | `str` | 占位提示文字 |
| `text_color` | `str` 或 `tuple` | 文字颜色 |
| `alignment` | `int` | 对齐方式 |
| `secure` | `bool` | 是否为密码输入（遮罩显示） |
| `keyboard_type` | `int` | 键盘类型 |

### action 回调

编辑完成（失去焦点或按回车）时调用：

```python
tf.action = lambda sender: print('输入内容:', sender.text)
```

---

## 9. TextView 多行文本

### 创建

```python
tv = ui.TextView()
tv = ui.TextView(text='多行文本内容')
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `text` | `str` | 文本内容 |
| `editable` | `bool` | 是否可编辑 |
| `selectable` | `bool` | 是否可选中等 |
| `text_color` | `str` 或 `tuple` | 文字颜色 |
| `font` | `(name, size)` | 字体 |

### delegate 委托

可设置一个对象，实现以下方法以响应编辑事件：

| 方法 | 说明 |
|------|------|
| `textview_did_begin_editing(textview)` | 开始编辑时调用 |
| `textview_did_end_editing(textview)` | 结束编辑时调用 |

```python
class MyDelegate:
    def textview_did_begin_editing(self, tv):
        print('开始编辑')
    def textview_did_end_editing(self, tv):
        print('结束编辑')

tv = ui.TextView(text='')
tv.delegate = MyDelegate()
```

---

## 10. ImageView 图片视图

### 创建

```python
iv = ui.ImageView()
iv = ui.ImageView(frame=(0, 0, 200, 200))
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `image` | `PIL.Image` 或 `ui.Image` | 要显示的图片 |
| `content_mode` | `int` | 缩放模式，如 `ui.CONTENT_SCALE_TO_FILL` |

### 方法

| 方法 | 说明 |
|------|------|
| `load_from_url(url)` | 异步从网络 URL 加载图片 |

### 示例

```python
iv = ui.ImageView()
iv.frame = (20, 20, 280, 200)
iv.load_from_url('https://example.com/image.png')
# 或使用本地图片
# iv.image = ui.Image.named('local.png')
```

---

## 11. Switch 开关

### 创建

```python
sw = ui.Switch()
sw = ui.Switch(value=True)
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `value` | `bool` | 开关状态，True 开、False 关 |
| `enabled` | `bool` | 是否可用 |

### action 回调

值改变时调用：

```python
sw.action = lambda sender: print('开关状态:', sender.value)
```

---

## 12. Slider 滑块

### 创建

```python
sl = ui.Slider()
sl = ui.Slider(frame=(20, 100, 280, 30))
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `value` | `float` | 当前值，0.0 ~ 1.0 |
| `continuous` | `bool` | 是否在拖动过程中持续触发 action |

### action 回调

```python
sl.action = lambda sender: print('值:', sender.value)
```

---

## 13. SegmentedControl 分段控件

### 创建

```python
seg = ui.SegmentedControl()
seg.frame = (20, 100, 280, 32)
seg.segments = ['选项 A', '选项 B', '选项 C']  # 或用换行分隔的字符串
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `segments` | `list` 或 `str` | 分段标题列表，或换行分隔字符串 |
| `selected_index` | `int` | 当前选中的索引 |

### action 回调

```python
seg.action = lambda sender: print('选中:', sender.selected_index)
```

---

## 14. DatePicker 日期选择器

### 创建

```python
dp = ui.DatePicker()
dp.frame = (20, 100, 280, 200)
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `date` | `float` | 当前选中的日期时间戳 |
| `mode` | `str` | `'date'`、`'time'`、`'datetime'` |
| `enabled` | `bool` | 是否可用 |

### action 回调

```python
dp.action = lambda sender: print('选中时间:', sender.date)
```

---

## 15. ScrollView 滚动视图

### 创建

```python
sv = ui.ScrollView()
sv.frame = (0, 0, 320, 400)
sv.content_size = (320, 800)  # 内容区域尺寸
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `content_size` | `(width, height)` | 内容区域尺寸 |
| `content_offset` | `(x, y)` | 当前滚动偏移 |
| `content_inset` | `(top, left, bottom, right)` | 内容内边距 |
| `bounces` | `bool` | 是否允许回弹效果 |
| `always_bounce_horizontal` | `bool` | 水平方向是否始终回弹 |
| `always_bounce_vertical` | `bool` | 垂直方向是否始终回弹 |
| `scroll_enabled` | `bool` | 是否允许滚动 |
| `paging_enabled` | `bool` | 是否分页滚动 |

### 方法

| 方法 | 说明 |
|------|------|
| `scroll_to(x, y, animated=True)` | 滚动到指定偏移 |

### delegate 委托

设置 `scrollview_did_scroll(x, y)` 回调，在滚动时持续触发：

```python
class MyDelegate:
    def scrollview_did_scroll(self, x, y):
        print('滚动到:', x, y)

sv = ui.ScrollView()
sv.content_size = (300, 800)
sv.delegate = MyDelegate()
```

### 示例：可滚动的长内容

```python
sv = ui.ScrollView()
sv.frame = (0, 0, 320, 400)
sv.content_size = (320, 1200)
sv.bounces = True
sv.always_bounce_vertical = True

# 添加一个很长的标签作为内容
lbl = ui.Label(text='很长很长的一段文本...')
lbl.frame = (10, 10, 300, 1180)
sv.add_subview(lbl)

root.add_subview(sv)
```

---

## 16. TableView 表格视图

### 创建

```python
tv = ui.TableView()
tv.frame = (0, 0, 320, 400)
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `data_source` | `list` | 数据源，见下方格式 |
| `action` | `callable` | 行选择回调 |
| `delegate` | `object` | 委托对象 |

### data_source 格式

- 一维列表：`[{'title': 'A', 'subtitle': 'a'}, {'title': 'B'}]`
- 二维列表（多 section）：`[[{...}, {...}], [{...}]]`
- 每个元素至少包含 `title`，可选 `subtitle`

### action 回调

```python
tv.action = lambda sender, section, row: print('选中', section, row)
```

### delegate

可实现 `tableview_did_select(tableview, section, row)` 方法。

### 方法

| 方法 | 说明 |
|------|------|
| `reload_data()` | 刷新表格显示 |

### 示例

```python
tv = ui.TableView()
tv.frame = (0, 0, 320, 400)
tv.data_source = [
    {'title': '第一行', 'subtitle': '说明'},
    {'title': '第二行'},
    {'title': '第三行', 'subtitle': '另一说明'},
]
tv.action = lambda s, sec, r: print(f'Section {sec}, Row {r}')
tv.reload_data()
root.add_subview(tv)
```

---

## 17. WebView 网页视图

### 创建

```python
wv = ui.WebView()
wv.frame = (0, 0, 320, 400)
```

### 方法

| 方法 | 说明 |
|------|------|
| `load_url(url)` | 加载指定 URL |
| `load_html(html, base_url=None)` | 加载 HTML 字符串 |
| `go_back()` | 后退 |
| `go_forward()` | 前进 |
| `reload()` | 刷新 |
| `stop()` | 停止加载 |
| `eval_js(code, callback=None)` | 执行 JavaScript，callback 接收结果字符串 |

### 示例

```python
wv = ui.WebView()
wv.frame = (0, 0, 320, 400)
wv.load_url('https://www.apple.com')
# 执行 JS 并获取结果
wv.eval_js('document.title', lambda result: print('标题:', result))
```

---

## 18. ActivityIndicator 加载指示器

### 创建

```python
ai = ui.ActivityIndicator()
ai.frame = (140, 200, 37, 37)
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `animating` | `bool` | 是否正在旋转 |
| `style` | `int` | 样式：`ACTIVITY_INDICATOR_STYLE_GRAY`、`WHITE`、`WHITE_LARGE` |
| `hides_when_stopped` | `bool` | 停止时是否隐藏 |

### 方法

```python
ai.start()   # 或 ai.start_animating()
ai.stop()    # 或 ai.stop_animating()
```

---

## 19. NavigationView 导航视图

见 [5. present 与展示](#5-present-与展示) 中的 NavigationView 部分。

---

## 20. 自定义 View 与绘图

### 继承 View 并重写 draw

```python
class MyView(ui.View):
    def draw(self):
        # 在视图上绘制
        pass
```

### 触摸回调

| 方法 | 说明 |
|------|------|
| `touch_began(touch)` | 手指按下 |
| `touch_moved(touch)` | 手指移动 |
| `touch_ended(touch)` | 手指抬起 |

`touch` 对象有 `location`、`prev_location` 等属性。

### CanvasView 与 ImageContext

`CanvasView` 用于自定义绘制，需重写 `draw` 方法，内部使用 `ImageContext` 和 `Path` 等 API：

```python
import ui

def draw_canvas(canvas):
    with ui.ImageContext(200, 200) as ctx:
        ui.set_color('red')
        ui.fill_rect(0, 0, 200, 200)
        ui.set_color('white')
        ui.draw_string('Hello', rect=(50, 80, 100, 40))
        img = ctx.get_image()
    if img:
        canvas.image = img

cv = ui.CanvasView()
cv.frame = (60, 100, 200, 200)
cv.render = draw_canvas  # 或继承 CanvasView 重写 draw
```

### 绘图 API 简要

| API | 说明 |
|-----|------|
| `ui.set_color(color)` | 设置绘图颜色 |
| `ui.fill_rect(x, y, w, h)` | 填充矩形 |
| `ui.stroke_rect(x, y, w, h)` | 描边矩形 |
| `ui.draw_string(text, rect=(x,y,w,h))` | 绘制文本 |
| `Path.rect(x, y, w, h)` | 矩形路径 |
| `Path.oval(x, y, w, h)` | 椭圆路径 |
| `Path.round_rect(x, y, w, h, r)` | 圆角矩形 |
| `path.fill()` / `path.stroke()` | 填充/描边路径 |
| `path.move_to(x, y)` / `path.line_to(x, y)` | 直线路径 |
| `path.add_arc(cx, cy, r, start, end, clockwise)` | 圆弧 |
| `path.add_curve(...)` | 贝塞尔曲线 |
| `GState()` | 保存/恢复绘图状态 |
| `ui.set_blend_mode(mode)` | 混合模式 |
| `ui.set_shadow(...)` | 阴影 |

### ImageContext

```python
with ui.ImageContext(200, 200) as ctx:
    ui.set_color('blue')
    ui.fill_rect(0, 0, 200, 200)
    # ... 更多绘图 ...
    img = ctx.get_image()  # 得到 PIL.Image
```

---

## 21. load_view 与 load_view_str

### load_view(name, bindings=None, ...)

从文件加载界面。`name` 为文件名（不含扩展名会自动加 `.pyui`），支持 JSON 和 plist 格式。会在当前工作目录和用户主目录下查找。

```python
v = ui.load_view('MyView')
v = ui.load_view('MyView', bindings={'submit': on_submit})
```

### load_view_str(json_str, bindings=None, ...)

从 JSON 字符串加载：

```python
json_str = '''
{
  "UIView": {
    "frame": "{{0,0},{320,400}}",
    "subviews": [
      {"UIButton": {"frame": "{{50,100},{200,44}}", "title": "确定"}}
    ]
  }
}
'''
v = ui.load_view_str(json_str, bindings={'submit': on_submit})
```

### frame 格式

`.pyui` 中 frame 使用 `{{x,y},{width,height}}` 格式，例如 `{{0,0},{320,480}}`。

### bindings

将名称映射到可调用对象，用于绑定按钮的 action 等。在 JSON 中若某控件有 `"action": "submit"`，则会在 bindings 中查找 `submit` 并设为 action。

---

## 22. animate 与工具函数

### animate

```python
ui.animate(animation, duration=0.25, delay_sec=0.0, completion=None)
```

- `animation`：可调用对象，无参数，在延迟后执行
- `duration`：动画持续秒数（当前实现中，completion 在此时间后调用）
- `delay_sec`：延迟秒数后再执行 animation
- `completion`：可调用对象，在 duration 秒后执行

**注意**：animation 回调为异步执行，视图属性变更会立即生效，不会参与 UIKit 的渐变动画。若需流畅的属性动画，需在 animation 中预先设置好目标值。

### 工具函数

| 函数 | 说明 |
|------|------|
| `ui.get_screen_size()` | 返回 `(width, height)` 屏幕尺寸 |
| `ui.get_window_size()` | 返回窗口尺寸 |
| `ui.get_ui_style()` | 返回 `'light'` 或 `'dark'` |
| `ui.convert_point(point, from_view, to_view)` | 坐标转换 |
| `ui.convert_rect(rect, from_view, to_view)` | 矩形转换 |
| `ui.measure_string(text, font, max_width)` | 测量文本尺寸，返回 `(width, height)` |
| `ui.close_all(animated=False)` | 关闭所有已展示界面 |
| `ui.dump_view(view)` | 调试用，输出视图树 |
| `ui.delay(sec, fn)` | 延迟执行 |
| `ui.in_background(fn)` | 在后台线程执行 |

---

## 23. 常量与枚举

### 内容模式 CONTENT_*

| 常量 | 说明 |
|------|------|
| `ui.CONTENT_SCALE_TO_FILL` | 拉伸填满 |
| `ui.CONTENT_SCALE_ASPECT_FIT` | 保持比例适配 |
| `ui.CONTENT_SCALE_ASPECT_FILL` | 保持比例填满 |
| `ui.CONTENT_REDRAW` | 重绘 |
| 等 | 对应 UIView.ContentMode |

### ActivityIndicator 样式

| 常量 | 说明 |
|------|------|
| `ui.ACTIVITY_INDICATOR_STYLE_GRAY` | 灰色 |
| `ui.ACTIVITY_INDICATOR_STYLE_WHITE` | 白色 |
| `ui.ACTIVITY_INDICATOR_STYLE_WHITE_LARGE` | 大号白色 |

### Line break / alignment

与系统 UILabel 等对齐、换行常量一致，具体见 Pythonista 文档。

---

## 24. 常见问题与排错

### AttributeError: 属性不存在

- 检查属性名是否与文档一致（如 `background_color` 不是 `backgroundColor`）
- 确认该控件支持该属性

### 回调不触发（action、delegate 无反应）

- 确认已正确设置 `action` 或 `delegate`
- 检查 `enabled` 是否为 True
- 若为自定义 delegate，确认实现了正确的方法名（如 `scrollview_did_scroll`）

### present 后白屏或崩溃

- 确保根视图有合理的 `frame`（宽高大于 0）
- 避免在 sheet 内再次 present 造成嵌套问题

### load_view 解析失败

- 确认文件格式为有效 JSON 或 plist
- frame 使用 `{{x,y},{w,h}}` 格式
- 复杂嵌套或自定义类可能不完全支持

### 绘图不显示

- 自定义 View 需调用 `set_needs_display()` 触起重绘
- `ImageContext.get_image()` 需在 `with` 块内调用

---

*文档版本：2025-03 · 适用于 Python IDE iOS 应用*
