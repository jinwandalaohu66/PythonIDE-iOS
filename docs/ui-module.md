# ui 模块 — 原生 iOS 界面

> **Pythonista 兼容的 `ui` 模块**：在 Python 中搭建 **UIKit 原生控件**，用于按钮、列表、网页、手势与自定义绘图等场景。  
> **坐标系**：左上角为原点 `(0, 0)`，`x` 向右增大，`y` **向下**增大（与 `scene` 模块的数学坐标相反）。

---

## 目录

1. [控件与类型参考（30+）](#控件与类型参考30)
2. [手势识别器](#手势识别器)
3. [自定义绘图](#自定义绘图)
4. [`Image` 类](#image-类)
5. [模块级函数](#模块级函数)
6. [常量](#常量)
7. [`flex` 自适应布局](#flex-自适应布局)
8. [完整示例](#完整示例)
9. [注意事项](#注意事项)

---

## 控件与类型参考（30+）

下列类型共同构成与 **Pythonista** 风格一致的 API。构造时普遍支持 `frame=(x, y, w, h)` 以及 `**kwargs` 批量设置属性。

### 1. `View` — 基类

**构造**：`ui.View(frame=None, **kwargs)`  
所有可视控件均继承自 `View`。

| 类别 | 名称 | 说明 |
|------|------|------|
| **几何** | `frame` | `(x, y, width, height)`，相对父视图 |
| | `bounds` | 自身坐标系下的矩形，常为 `(0, 0, w, h)` |
| | `center` | 中心点在父视图坐标系中的 `(cx, cy)` |
| | `x`, `y`, `width`, `height` | `frame` 的分量读写 |
| **外观** | `background_color` | 背景色（见[注意事项](#注意事项)） |
| | `tint_color` | 着色（影响模板图、部分控件强调色） |
| | `alpha` | `0.0`–`1.0` 不透明度 |
| | `hidden` | 是否隐藏 |
| | `corner_radius` | 圆角半径 |
| | `border_width`, `border_color` | 边框 |
| | `content_mode` | 内容缩放/对齐，见 [常量 · 内容模式](#内容模式-content_mode) |
| | `clips_to_bounds` | 是否裁剪子视图到边界（Pythonista 标准属性） |
| **交互** | `user_interaction_enabled` | 是否响应触摸（部分环境亦提供别名 `touch_enabled`） |
| | `multiple_touch_enabled` | 是否允许多指（别名 `multitouch_enabled`） |
| **其它** | `name` | 名称，便于 `load_view` 与子视图查找 |
| | `flex` | 自适应布局字符串，见 [`flex` 一节](#flex-自适应布局) |
| | `transform` | 2D 仿射变换（`ui.Transform`） |
| | `superview` | 父视图（只读） |
| | `subviews` | 子视图序列（只读） |
| **导航** | `title` | `present` 时导航栏标题（常用） |
| | `left_button_items` / `right_button_items` | 导航栏按钮项（`ui.ButtonItem` 列表） |

**方法**

| 方法 | 说明 |
|------|------|
| `add_subview(view)` | 添加子视图 |
| `remove_subview(view)` | 移除指定子视图 |
| `remove_from_superview()` | 从父视图移除自身 |
| `bring_to_front()` / `send_to_back()` | 调整绘制顺序 |
| `set_needs_display()` | 请求重绘（配合 `draw`） |
| `size_to_fit()` | 按内容收缩尺寸（Pythonista 标准；具体控件支持度因实现而异） |
| `layout()` | 布局更新时调用；可子类重写以自定义布局 |
| `present(style, animated=True, hide_title_bar=False, **kwargs)` | 模态展示。`style`：`'sheet'`、`'fullscreen'` / `'full_screen'`、`'popover'`、`'panel'` 等 |
| `close()` | 关闭当前展示 |
| `wait_modal()` | 阻塞直至界面关闭（常用于全屏流程） |
| `add_gesture_recognizer(gr)` | 添加手势 |
| `remove_gesture_recognizer(gr)` | 移除手势（Pythonista 标准 API） |

**回调（可重写）**

| 回调 | 说明 |
|------|------|
| `draw(self, rect)` | 自定义绘制；`rect` 为需更新的区域（元组或矩形） |
| `layout(self)` | `bounds` 变化后的布局 |
| `touch_began` / `touch_moved` / `touch_ended` | 触摸生命周期（若启用） |
| `will_close(self)` | 即将关闭时 |

---

### 2. `Button` — `ui.Button()`

**构造**：`ui.Button(frame=None, title='', **kwargs)`

| 属性 | 说明 |
|------|------|
| `title` | 标题文案 |
| `font` | `('字体名', 字号)` 或 `ui.Font` |
| `image` | `ui.Image`，前景图 |
| `background_image` | `ui.Image`，背景图 |
| `tint_color` | 着色 |
| `title_color` | 标题颜色（扩展） |
| `enabled` | 是否可用 |

**回调**：`action` — 可调用对象，`action(sender)`，`sender` 一般为按钮自身。

---

### 3. `Label` — `ui.Label()`

**构造**：`ui.Label(frame=None, text='', **kwargs)`

| 属性 | 说明 |
|------|------|
| `text` | 文本 |
| `text_color` | 颜色 |
| `font` | `('字体名', 字号)` |
| `alignment` | `ui.ALIGN_LEFT` / `ALIGN_CENTER` / `ALIGN_RIGHT` 等 |
| `number_of_lines` | 行数；`0` 表示不限制 |
| `line_break_mode` | `ui.LB_*`，换行与截断 |
| `adjusts_font_size_to_fit_width` | 是否自动缩小字体以适配宽度 |
| `minimum_scale_factor` | 最小缩放比例（相对字体） |

> 部分实现中对应别名为 `scales_font`、`min_font_scale`，语义与上表一致。

---

### 4. `TextField` — `ui.TextField()`

**构造**：`ui.TextField(frame=None, text='', placeholder='', **kwargs)`

| 属性 | 说明 |
|------|------|
| `text` | 当前文本 |
| `placeholder` | 占位提示 |
| `text_color` | 文本颜色 |
| `font` | 字体元组或 `ui.Font` |
| `alignment` | 水平对齐 |
| `secure_text_entry` | 密码遮蔽（Pythonista 名；亦常见别名 `secure`） |
| `keyboard_type` | 见 [键盘类型](#键盘类型-keyboard_type) |
| `autocorrection_type` | 自动更正 |
| `spellchecking_type` | 拼写检查 |
| `enabled` | 是否可编辑 |
| `bordered` | 是否显示边框样式 |

**回调**

- `action`：编辑结束或按下回车等（依平台行为）。
- `delegate`：对象实现 `textfield_*` 系列方法（如 `textfield_should_begin_editing`、`textfield_did_change` 等，名称以实际运行环境为准）。

---

### 5. `TextView` — `ui.TextView()`

**构造**：`ui.TextView(frame=None, text='', **kwargs)`

| 属性 | 说明 |
|------|------|
| `text` | 全文 |
| `text_color` | 颜色 |
| `font` | 字体 |
| `alignment` | 对齐 |
| `editable` | 是否可编辑 |
| `selectable` | 是否可选择 |
| `auto_content_inset` | 是否自动调整内容边距（随安全区/键盘） |

**回调**：`delegate` — 如 `textview_did_begin_editing`、`textview_did_change`、`textview_did_end_editing` 等。

---

### 6. `ImageView` — `ui.ImageView()`

**构造**：`ui.ImageView(frame=None, **kwargs)`

| 属性 | 说明 |
|------|------|
| `image` | `ui.Image` 实例 |
| `content_mode` | 与 `View` 相同常量族 |

**方法**：`load_from_url(url)` — 异步从网络加载图片（具体行为依赖实现）。

---

### 7. `ScrollView` — `ui.ScrollView()`

| 属性 | 说明 |
|------|------|
| `content_size` | 内容尺寸 `(w, h)` |
| `content_offset` | 可见区域偏移 `(x, y)` |
| `content_inset` | 内边距，常为 `(top, left, bottom, right)` |
| `bounces` | 边界弹性滚动 |
| `paging_enabled` | 是否按页对齐 |
| `scroll_enabled` | 是否允许滚动 |
| `always_bounce_vertical` / `always_bounce_horizontal` | 内容不足时是否仍可弹性 |
| `shows_vertical_scroll_indicator` / `shows_horizontal_scroll_indicator` | 是否显示滚动条 |

**方法**：`scroll_to(x, y, animated=True)` — 滚动到指定偏移。

**回调**：`delegate` — 如 `scrollview_did_scroll` 等。

---

### 8. `TableView` — `ui.TableView()`

| 属性 | 说明 |
|------|------|
| `data_source` | 实现数据源协议的对象，或简单列表数据（依实现） |
| `delegate` | 选中、编辑等回调 |
| `row_height` | 默认行高 |
| `editing` | 是否处于编辑模式 |
| `selected_row` | 当前选中行（元组或索引，依实现） |

**方法**

| 方法 | 说明 |
|------|------|
| `reload()` | 刷新数据（Pythonista 名） |
| `reload_data()` | 同上（常见别名） |
| `delete_rows(rows)` | 删除指定行 |

**数据源（典型方法名）**

- `tableview_number_of_sections(tableview) -> int`
- `tableview_number_of_rows(tableview, section) -> int`
- `tableview_cell_for_row(tableview, section, row) -> TableViewCell`
- `tableview_title_for_header` / `footer`（可选）

**代理（典型）**

- `tableview_did_select(tableview, section, row)`
- `tableview_can_delete(tableview, section, row) -> bool`
- `tableview_delete(tableview, section, row)`

辅助类：`ui.ListDataSource`、`ui.TableViewCell`。

---

### 9. `WebView` — `ui.WebView()`

**方法**

| 方法 | 说明 |
|------|------|
| `load_url(url)` | 加载 URL |
| `load_html(html, base_url=None)` | 加载 HTML 字符串 |
| `go_back()` / `go_forward()` | 历史前进后退 |
| `reload()` / `stop()` | 刷新 / 停止 |
| `eval_js(script)` | 同步执行 JS（若环境支持） |
| `eval_js_async(script, callback)` | 异步执行，结果回调；部分实现合并为 `eval_js(script, callback=...)` |

**回调**：`delegate` — 加载开始/结束、错误等（依平台）。

---

### 10. `NavigationView` — `ui.NavigationView(root_view)`

**构造**：`ui.NavigationView(root)`，`root` 为根 `View`。

**方法**

| 方法 | 说明 |
|------|------|
| `push_view(view, animated=True)` | 压入新页面 |
| `pop_view(animated=True)` | 弹出当前页 |

常见样式属性：`navigation_bar_hidden`、`bar_tint_color`、`title_color`。

---

### 11. `Switch` — `ui.Switch()`

| 属性 | 说明 |
|------|------|
| `value` | `bool`，开关状态 |
| `enabled` | 是否可操作 |

**回调**：`action(sender)`。

---

### 12. `Slider` — `ui.Slider()`

| 属性 | 说明 |
|------|------|
| `value` | `0.0`–`1.0`（Pythonista 常用归一化区间；亦可能有 `min`/`max` 扩展） |
| `continuous` | 拖动过程是否连续触发 `action` |

**回调**：`action(sender)`。

---

### 13. `SegmentedControl` — `ui.SegmentedControl()`

| 属性 | 说明 |
|------|------|
| `segments` | 字符串列表 |
| `selected_index` | 当前选中下标 |

**回调**：`action(sender)`。

---

### 14. `DatePicker` — `ui.DatePicker()`

| 属性 | 说明 |
|------|------|
| `date` | `datetime.datetime` |
| `mode` | `ui.DATE_PICKER_MODE_DATE` / `TIME` / `DATE_AND_TIME` / `COUNT_DOWN`（或 `COUNTDOWN`，依常量命名） |
| `enabled` | 是否可用 |

**回调**：`action(sender)`。

---

### 15. `ActivityIndicator` — `ui.ActivityIndicator()`

| 属性 | 说明 |
|------|------|
| `animating` | 是否正在旋转 |
| `style` | `ui.ACTIVITY_INDICATOR_STYLE_*` |
| `hides_when_stopped` | 停止时是否隐藏 |

**方法**：`start()` / `stop()`（别名 `start_animating` / `stop_animating`）。

---

### 16–30+. 其它常用类型（几何、导航、手势、绘图）

| 类型 | 作用 |
|------|------|
| `ui.Color` | RGBA 颜色封装 |
| `ui.Point` | 点 `(x, y)` |
| `ui.Size` | 尺寸 `(w, h)` |
| `ui.Rect` | 矩形与基础几何运算 |
| `ui.Transform` | 旋转、缩放、平移与矩阵运算 |
| `ui.Touch` | 触摸信息（位置、阶段等） |
| `ui.Font` | 字体；类方法如 `system_font_of_size` |
| `ui.ButtonItem` | 导航栏按钮项：`title`、`image`、`action` |
| `ui.GestureSender` | 手势回调中的 `sender` 信息 |
| `ui.TableViewCell` | 表格行单元格容器 |
| `ui.ListDataSource` | 表格数据源基类 |
| `ui.CanvasView` | 通过 `render(draw_func)` 将绘图结果呈现为位图贴图 |
| `ui.Path` | 矢量路径绘制 |
| `ui.GState` | `with ui.GState():` 保存/恢复绘图状态 |
| `ui.ImageContext` | 离屏位图上下文 |
| `ui.Image` | 位图对象 |

---

## 手势识别器

### 工厂形式（概念 API）

`ui.GestureRecognizer(type)`：`type` 可取 `'tap'`、`'pan'`、`'swipe'`、`'pinch'`、`'rotation'`、`'longpress'`、`'screenedge'` 等，返回配置好的识别器（具体以运行环境为准）。

### 具名子类（推荐）

| 类 | 说明 |
|----|------|
| `ui.TapGestureRecognizer` | 点击 |
| `ui.PanGestureRecognizer` | 拖动 |
| `ui.PinchGestureRecognizer` | 捏合缩放 |
| `ui.SwipeGestureRecognizer` | 轻扫；属性 `direction` |
| `ui.LongPressGestureRecognizer` | 长按；`minimum_press_duration` |

**通用属性**

- `enabled`
- `number_of_touches_required`
- `number_of_taps_required`（Tap）
- `action` — `action(sender)`，`sender` 为 `GestureSender`（含 `view`、`location`、`translation`、`scale` 等）

**挂载到视图**

```python
gr = ui.TapGestureRecognizer()
gr.action = lambda s: print(s.location)
view.add_gesture_recognizer(gr)
view.remove_gesture_recognizer(gr)
```

---

## 自定义绘图

重写 `View.draw(self, rect)`，在系统调用时完成绘制；属性变化后需 `set_needs_display()` 触发刷新。

### `ui.Path()`

| 方法 | 说明 |
|------|------|
| `move_to(x, y)` / `line_to(x, y)` | 路径移动与线段 |
| `curve_to(cp1x, cp1y, cp2x, cp2y, x, y)` | 三次贝塞尔到 `(x,y)`（部分实现为 `add_curve`） |
| `add_arc(cx, cy, r, start, end, clockwise=True)` | 圆弧 |
| `add_rect(x, y, w, h)` | 矩形子路径 |
| `add_rounded_rect(x, y, w, h, r)` | 圆角矩形；或类方法 `Path.rounded_rect(...)` |
| `close()` | 闭合子路径 |
| `fill()` / `stroke()` | 填充 / 描边 |
| `set_line_width(w)` | 线宽 |
| `eo_fill_rule` | 奇偶填充规则（属性） |

### 全局绘图状态

| 函数 / 上下文 | 说明 |
|---------------|------|
| `ui.set_color(color)` | 当前填充/描边颜色 |
| `ui.concat_ctm(transform)` | 乘以当前变换矩阵（与 `Transform` 配合） |
| `ui.set_shadow(color, dx, dy, radius)` | 阴影 |
| `ui.fill_rect` / `ui.stroke_rect` | 矩形快捷绘制 |
| `ui.draw_string(text, rect, font, color, alignment, line_break_mode)` | 文本绘制 |
| `with ui.GState():` | 保存/恢复图层状态 |

### 离屏图像

Pythonista 风格常用上下文管理器：

```python
with ui.ImageContext(width, height) as ctx:
    ui.set_color('blue')
    ui.fill_rect(0, 0, width, height)
    img = ctx.get_image()   # ui.Image
```

部分文档亦写作 `ui.begin_image_context(w, h, scale)` / `ui.end_image_context()`，与 `ImageContext` 等价语义。

---

## `Image` 类

| 入口 | 说明 |
|------|------|
| `ui.Image.named(name)` | 内置或捆绑资源名 |
| `ui.Image.from_data(data)` | 自字节加载 |
| `ui.Image(name)` | 常见等价于 `Image.named(name)` |

| 属性 / 方法 | 说明 |
|-------------|------|
| `size` | `Size(w, h)` |
| `to_png()` | `bytes` |
| `with_rendering_mode(mode)` | 模板/原色渲染模式 |
| `resized(size)` | 缩放副本 |
| `cropped(rect)` | 裁剪副本 |

---

## 模块级函数

| 函数 | 说明 |
|------|------|
| `ui.load_view(pyui_file)` | 从 `.pyui`（JSON/plist）加载界面树，返回根 `View` |
| `ui.load_view_str(json_str, ...)` | 自字符串加载（扩展） |
| `ui.delay(seconds, func)` | 延迟执行；**Pythonista 参数顺序为（秒数，函数）** |
| `ui.cancel_delays()` | 取消尚未执行的 `delay` |
| `ui.in_background(fn)` | 装饰器：在后台线程运行函数 |
| `ui.animate(animation, duration=0.25, delay=0, completion=None)` | 动画块调度（属性插值能力依实现而定） |
| `ui.get_screen_size()` | `(w, h)` |
| `ui.get_window_size()` | `(w, h)` 或 `Size` |
| `ui.parse_color(color_str)` | 归一化 `(r, g, b, a)`，`0.0`–`1.0` |
| `ui.convert_rect(rect, from_view, to_view)` | 坐标转换；返回 `Rect` 或 `(x, y, w, h)` |
| `ui.measure_string(text, max_width, font, ...)` | 文本测量 |
| `ui.close_all(animated=False)` | 关闭全部已展示 UI（扩展） |
| `ui.dump_view(view)` | 打印视图树（调试） |

---

## 常量

### 对齐 `alignment`

| 常量 | 值 |
|------|-----|
| `ALIGN_LEFT` | 0 |
| `ALIGN_CENTER` | 1 |
| `ALIGN_RIGHT` | 2 |
| `ALIGN_JUSTIFIED` | 3 |
| `ALIGN_NATURAL` | 4 |

### 内容模式 `content_mode`

| 常量 | 值 |
|------|-----|
| `CONTENT_SCALE_TO_FILL` | 0 |
| `CONTENT_SCALE_ASPECT_FIT` | 1 |
| `CONTENT_SCALE_ASPECT_FILL` | 2 |
| `CONTENT_CENTER` | 3（部分实现中 `CONTENT_REDRAW` 等为 3，`CENTER` 为 4，以模块导出为准） |
| … | 另有 `CONTENT_TOP`、`BOTTOM`、`LEFT`、`RIGHT`、角点组合等 |

### 键盘类型 `keyboard_type`

| 常量 | 值 |
|------|-----|
| `KEYBOARD_DEFAULT` | 0 |
| `KEYBOARD_ASCII` | 1 |
| `KEYBOARD_NUMBERS_AND_PUNCTUATION` | 2（部分实现名为 `KEYBOARD_NUMBERS`） |
| `KEYBOARD_URL` | 3 |
| `KEYBOARD_NUMBER_PAD` | 4 |
| `KEYBOARD_PHONE_PAD` | 5 |
| `KEYBOARD_EMAIL` | 7 |
| `KEYBOARD_DECIMAL_PAD` | 8 |

### 日期选择器 `DatePicker.mode`

| 常量 | 值 |
|------|-----|
| `DATE_PICKER_MODE_TIME` | 0 |
| `DATE_PICKER_MODE_DATE` | 1 |
| `DATE_PICKER_MODE_DATE_AND_TIME` | 2 |
| `DATE_PICKER_MODE_COUNT_DOWN` | 3（亦可能导出为 `DATE_PICKER_MODE_COUNTDOWN`） |

### 换行与截断 `line_break_mode`

| 常量 | 值 |
|------|-----|
| `LB_WORD_WRAP` | 0 |
| `LB_CHAR_WRAP` | 1 |
| `LB_CLIP` | 2 |
| `LB_TRUNCATE_HEAD` | 3 |
| `LB_TRUNCATE_TAIL` | 4 |
| `LB_TRUNCATE_MIDDLE` | 5 |

### 活动指示器 `ActivityIndicator.style`

| 常量 | 说明 |
|------|------|
| `ACTIVITY_INDICATOR_STYLE_GRAY` | 灰色小菊花 |
| `ACTIVITY_INDICATOR_STYLE_WHITE` | 白色 |
| `ACTIVITY_INDICATOR_STYLE_WHITE_LARGE` | 大号白色 |

---

## `flex` 自适应布局

`flex` 为字符串，每个字符表示在父视图尺寸变化时哪一侧或哪一维可伸缩：

| 字符 | 含义 |
|------|------|
| `L` | 左边距弹性 |
| `R` | 右边距弹性 |
| `T` | 上边距弹性 |
| `B` | 下边距弹性 |
| `W` | 宽度弹性 |
| `H` | 高度弹性 |

示例：

```python
v.flex = 'LRTBWH'   # 四边距与宽高均可变 → 充满父视图
v.flex = 'WH'       # 仅宽高随父视图变，位置由 frame 决定
```

---

## 完整示例

下面是一个**简易计算器**（连续加法 + 清除 + 小数点），演示 `View` / `Button` / `Label` / `present` 的典型用法。

```python
import ui

def calc_main():
    root = ui.View()
    root.background_color = '#1c1c1e'
    sw, sh = ui.get_screen_size()
    root.frame = (0, 0, sw, sh)

    display = ui.Label()
    display.text = '0'
    display.text_color = 'white'
    display.font = ('Helvetica', 36)
    display.alignment = ui.ALIGN_RIGHT
    display.background_color = '#2c2c2e'
    display.frame = (16, 60, sw - 32, 72)
    root.add_subview(display)

    grid = ui.View()
    grid.frame = (16, 148, sw - 32, sh - 164)
    root.add_subview(grid)

    cur = ['0']          # 当前输入字符串
    acc = [None]         # 暂存左操作数
    pending = [None]     # 待执行：'+' 等

    def show():
        display.text = cur[0]

    def on_digit(sender):
        d = sender.title
        if d == '.' and '.' in cur[0]:
            return
        if cur[0] == '0' and d != '.':
            cur[0] = d
        else:
            cur[0] += d
        show()

    def on_clear(sender):
        cur[0] = '0'
        acc[0] = None
        pending[0] = None
        show()

    def on_plus(sender):
        v = float(cur[0])
        if acc[0] is None:
            acc[0] = v
        elif pending[0] == '+':
            acc[0] = acc[0] + v
        cur[0] = '0'
        pending[0] = '+'
        show()

    def on_eq(sender):
        if acc[0] is not None and pending[0] == '+':
            acc[0] = acc[0] + float(cur[0])
            x = acc[0]
            cur[0] = str(int(x) if x == int(x) else round(x, 8))
            acc[0] = None
            pending[0] = None
            show()

    rows, cols = 5, 4
    gap = 8.0
    gw, gh = grid.frame[2], grid.frame[3]
    cw = (gw - gap * (cols - 1)) / cols
    ch = (gh - gap * (rows - 1)) / rows

    def add_button(title, r, c, colspan=1, action=None):
        b = ui.Button()
        b.title = title
        b.font = ('Helvetica', 22)
        b.background_color = '#3a3a3c'
        b.tint_color = 'white'
        w = cw * colspan + gap * (colspan - 1)
        x = c * (cw + gap)
        y = r * (ch + gap)
        b.frame = (x, y, w, ch)
        b.action = action
        grid.add_subview(b)

    add_button('C', 0, 0, action=on_clear)
    add_button('/', 0, 1, action=lambda s: None)  # 占位
    add_button('*', 0, 2, action=lambda s: None)
    add_button('-', 0, 3, action=lambda s: None)

    add_button('7', 1, 0, action=on_digit)
    add_button('8', 1, 1, action=on_digit)
    add_button('9', 1, 2, action=on_digit)
    add_button('+', 1, 3, action=on_plus)

    add_button('4', 2, 0, action=on_digit)
    add_button('5', 2, 1, action=on_digit)
    add_button('6', 2, 2, action=on_digit)
    add_button('+', 2, 3, action=on_plus)

    add_button('1', 3, 0, action=on_digit)
    add_button('2', 3, 1, action=on_digit)
    add_button('3', 3, 2, action=on_digit)
    add_button('=', 3, 3, action=on_eq)

    add_button('0', 4, 0, colspan=2, action=on_digit)
    add_button('.', 4, 2, action=on_digit)
    add_button('=', 4, 3, action=on_eq)

    root.present('sheet')
    # 全屏可改用 'fullscreen'；若要阻塞到关闭可调用 root.wait_modal()

if __name__ == '__main__':
    calc_main()
```

**任务列表示例思路**：用 `ui.TableView` + `ListDataSource`，在 `tableview_cell_for_row` 里返回带 `Label` 的 `TableViewCell`，`tableview_did_select` 中切换勾选或进入详情页。

---

## 注意事项

1. **坐标系**：原点**左上**，**y 向下**；与 `scene`（左下原点、y 向上）不同，混用时需自行换算。
2. **`present`**：在 `'fullscreen'` / `'full_screen'` 模式下，脚本常表现为阻塞直至用户关闭；`sheet` / `popover` 多为非阻塞，可配合 `wait_modal()`。
3. **颜色**：支持颜色名字符串（如 `'red'`）、十六进制 `'#FF0000'` / `'#F00'`、RGBA 元组 `(r, g, b)` 或 `(r, g, b, a)`（一般为 `0.0`–`1.0`）；可用 `ui.parse_color` 预览解析结果。
4. **`draw`**：由系统在适当时机调用；逻辑更新后请调用 `set_needs_display()` 请求重绘。
5. **线程安全**：**触摸、改 UI 属性、创建控件**等应在**主线程**执行；耗时计算请放在后台（如 `ui.in_background`），再回到主线程更新界面（需依具体运行环境提供的 `on_main_thread` 或等价机制）。
6. **标题与 `present`**：常见写法是先设置 `root.title = '我的界面'`，再 `present(...)`；亦可通过 `present` 的相关参数扩展（依实现而定）。
7. **版本差异**：本文件以 **Pythonista 公开 API** 为主整理；在 **Python IDE** 等嵌入环境中，个别常量名、别名（如 `touch_enabled` 与 `user_interaction_enabled`）、`TableView.reload_data` 与 `reload`、`animate` 是否真实插值动画等，可能与官方 Pythonista 略有差异，以当前打包的 `ui` 模块为准。

---

*文档版本：与项目 `ui` 模块（Pythonista 兼容层）对照整理，便于脚本编写与 AI 辅助开发引用。*
