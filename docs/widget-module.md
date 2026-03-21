# widget 模块 — iOS 桌面小组件

用 Python 创建 iOS 桌面和锁屏小组件。提供两种方式：**快捷函数 `show()`**（模板化快速输出）与 **布局 DSL `Widget`**（完全控制画布与嵌套结构）。

实现位置：`pyboot/widget.py`（运行时以 `widget` 模块名导入）。

---

## 尺寸常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `SMALL` | `"small"` | 主屏幕小组件（2×2） |
| `MEDIUM` | `"medium"` | 主屏幕中组件（4×2） |
| `LARGE` | `"large"` | 主屏幕大组件（4×4） |
| `CIRCULAR` | `"circular"` | 锁屏圆形 |
| `RECTANGULAR` | `"rectangular"` | 锁屏矩形 |
| `INLINE` | `"inline"` | 锁屏行内 |

### `family`

当前运行时的组件尺寸：**动态**从环境变量 `WIDGET_FAMILY` 读取；若未设置，默认 **`MEDIUM`**（`"medium"`）。

模块通过 `__getattr__` 实现：每次访问 `widget.family` 都会重新读取环境变量，因此在同一次解释器进程中多次运行脚本时也能得到正确值。

```python
from widget import family, SMALL, MEDIUM, LARGE, CIRCULAR

if family == SMALL:
    ...
```

---

## 方式一：快捷函数 `show()`

```python
show(
    title,
    value="",
    subtitle="",
    progress=None,
    color=None,
    icon=None,
    rows=None,
    display_type=None,
    style=None,
    background=None,
    text_color=None,
)
```

向小组件输出 **JSON 模板数据**（通过 `print("__WIDGET__...__WIDGET__")` 由主 App 捕获）。适用于简单展示；精细布局请用 `Widget` DSL。

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `title` | `str` | 标题（必填位置参数） |
| `value` | `str` | 主要内容，默认 `""` |
| `subtitle` | `str` | 副标题 |
| `progress` | `float` \| `None` | 进度值；序列化前会被限制在 **0.0～1.0**（与 `display_type` 为 `progress` 时配合使用） |
| `color` | `str` \| `None` | 主题色 |
| `icon` | `str` \| `None` | SF Symbol 图标名 |
| `rows` | `list[dict]` \| `None` | 键值行列表；每项可含 `label`、`value`，以及可选 `icon`、`color`（均为字符串） |
| `display_type` | `str` \| `None` | 展示类型：`"text"`、`"progress"`、`"keyvalue"`、`"multiline"`。**为 `None` 时按源码规则自动推断**（见下） |
| `style` | `str` \| `None` | 布局样式；输出字段名为 `layoutStyle` |
| `background` | `str` \| `None` | 背景色；输出字段名为 `backgroundColor` |
| `text_color` | `str` \| `None` | 文字颜色；输出字段名为 `textColor` |

### `display_type` 自动推断（`display_type is None` 时）

1. 若 `rows` 为真 → `"keyvalue"`
2. 否则若 `progress is not None` → `"progress"`
3. 否则若 `"\n" in str(value)` **且** `len(str(value)) > 60` → `"multiline"`
4. 否则 → `"text"`

---

## 方式二：布局 DSL — `Widget` 类

通过构建节点树并调用 `render()`，输出 `__WIDGET_LAYOUT__...__WIDGET_LAYOUT__` 包裹的 JSON（`version: 2` + `root` 布局树）。

### 构造函数

```python
Widget(background=None, padding=None)
```

| 参数 | 说明 |
|------|------|
| `background` | **可选。** `"system"` → 布局根级使用系统默认（序列化为 `"__SYSTEM__"`）。**纯色**：如 `"#1A1A2E"` 或命名色。**深浅色元组**：`("#FFF", "#111")`（浅色模式、深色模式）。**渐变字典**：`{"gradient": ["#FF6B6B", "#4ECDC4"], "direction": "diagonal"}`；`gradient` 至少 2 色，`direction` 可选。 |
| `padding` | **可选。** 根级内边距（数值，写入布局 JSON 的 `padding`）。 |

---

### 基础元素

以下方法均在当前栈顶容器（默认为根 `vstack`）上 **追加一个子节点**，并计入 **节点上限**（见文末「限制」）。

#### `text(content, size=None, weight=None, color=None, align=None, max_lines=None, design=None, opacity=None, padding=None, frame=None)`

| 参数 | 类型 | 说明 |
|------|------|------|
| `content` | `str` | 文字内容 |
| `size` | `int` \| `float` \| `None` | 字号 |
| `weight` | `str` \| `None` | 字重，如：`ultralight`、`thin`、`light`、`regular`、`medium`、`semibold`、`bold`、`heavy`、`black`（原样写入 JSON，由客户端解释） |
| `color` | `str` \| `(light, dark)` \| `[light, dark]` \| `None` | 颜色；元组/列表长度 ≥2 时拆成浅色/深色两字段 |
| `align` | `str` \| `None` | 对齐：`leading`、`center`、`trailing` |
| `max_lines` | `int` \| `None` | 最大行数 → JSON 字段 `maxLines` |
| `design` | `str` \| `None` | 字体设计：`rounded`、`monospaced`、`serif` |
| `opacity` | `float` \| `None` | 不透明度 |
| `padding` | `int` \| `float` \| `None` | 内边距 |
| `frame` | `dict` \| `None` | 如 `{"width": 100, "height": 50}`；仅当为 `dict` 时写入 |

#### `icon(name, size=None, color=None, weight=None, opacity=None, padding=None, frame=None)`

| 参数 | 说明 |
|------|------|
| `name` | SF Symbol 名称（字符串） |
| 其余 | 与 `text` 中同名参数含义一致（无 `align`、`max_lines`、`design`） |

#### `emoji(content, size=None, opacity=None, padding=None)`

| 参数 | 说明 |
|------|------|
| `content` | Emoji 字符（字符串） |
| `size`、`opacity`、`padding` | 可选，含义同其他元素 |

#### `spacer(length=None)`

| 参数 | 说明 |
|------|------|
| `length` | `int` \| `float` \| `None`；**`None` 表示弹性间距**（节点不含 `length` 字段） |

#### `divider(color=None, opacity=None)`

分隔线；`color` 支持单色或深浅色元组/列表（与 `_set_color` 一致）。

#### `progress(value, total=1.0, color=None, height=None, track_color=None)`

| 参数 | 说明 |
|------|------|
| `value` / `total` | 进度比为 `value / total`，再 **clamp 到 0.0～1.0** 写入节点 |
| `height` | 进度条高度 |
| `track_color` | 轨道颜色；支持深浅色（写入 `trackColor` / `darkTrackColor`） |

#### `gauge(value, total=1.0, label=None, size=None, color=None, track_color=None, line_width=None)`

圆形仪表盘（环形进度）。

| 参数 | 说明 |
|------|------|
| `value` / `total` | 同 `progress`，归一化到 0～1 |
| `label` | 中心文字；写入 JSON 字段 `content` |
| `size` | 直径等尺寸 |
| `color` / `track_color` | 弧线与轨道颜色（含深浅色） |
| `line_width` | 线宽；在 JSON 中映射为字段 **`height`**（与 Swift 端约定一致） |

#### `timer(target=None, style="timer", size=None, weight=None, color=None, design=None, opacity=None, padding=None, frame=None)`

使用 **WidgetKit 原生** 日期/计时展示，由系统刷新，无需脚本自行推进 timeline。

| 参数 | 说明 |
|------|------|
| `target` | `datetime.datetime` 或 **ISO 8601 字符串**；序列化为 `targetDate`。若为 `None`：使用 **`datetime.now().isoformat()`** |
| `style` | `"timer"`（倒计时）、`"relative"`（相对时间）、`"date"`、`"time"`、`"offset"`；写入 `timerStyle` |
| 其余 | 与 `text` 类似：`size`、`weight`、`color`、`design`、`opacity`、`padding`、`frame` |

源码说明：当 `target is None` 且 `style` 为 `date`/`time` 等时，仍会把「当前时刻」作为 `targetDate` 传入，具体语义由客户端按 `timerStyle` 解释。

#### `image(name, width=None, height=None, corner_radius=None, opacity=None, padding=None, content_mode=None)`

显示通过 **`save_image()`** 预先缓存的图片（按名称引用）。

| 参数 | 说明 |
|------|------|
| `name` | 缓存名（与 `save_image(..., name)` 一致，无扩展名） |
| `width` / `height` | 可选，写入 `frame` |
| `corner_radius` | 圆角 → JSON `cornerRadius` |
| `opacity`、`padding` | 可选 |
| `content_mode` | 非空时写入；`"fit"`（文档字符串中的默认语义）或 `"fill"` 等，由客户端解析 |

---

### 容器

均通过 **`with`** 使用：进入时在节点栈压入该容器，退出时弹出。子元素在 `with` 块内追加到该容器。

**通用可选参数**（`hstack` / `vstack` / `zstack` / `card` 在源码中的组合略有差异，见下）：

- `spacing`：`hstack` / `vstack` / **`card`** 支持；**`zstack` 无 spacing 参数**（内部传入 `None`）。
- `align`、`padding`、`background`（纯色 / 深浅色 / 渐变字典）、`opacity`、`corner_radius`、`border_color`、`border_width`、`url`（点击跳转 deep link，字符串）

`background` 在容器上的解析规则与根级一致：渐变写入 `gradient` + `gradientDirection`；纯色写入 `background` / `darkBg`。

#### `hstack(...)`

水平排列子节点。

#### `vstack(...)`

垂直排列子节点。根布局在内部也是一个 **`spacing: 0` 的 `vstack`**。

#### `zstack(align=None, ...)`

叠加布局；**无 `spacing` 参数**。

#### `card(background=None, corner_radius=None, padding=None, spacing=None, opacity=None, align=None, border_color=None, border_width=None, url=None)`

圆角卡片容器；类型为 `card`，支持渐变/纯色背景与边框。

---

### 渲染输出：`render(url=None)`

将当前布局树序列化为 JSON 并 **`print`**，供主 App 捕获。

| 参数 | 说明 |
|------|------|
| `url` | **可选。** 小组件点击跳转的 deep link（写入布局根对象）；也可在各容器 `url` 上单独指定 |

**必须在脚本末尾调用**（或至少在构建完所有节点后调用），否则不会输出布局。

---

## `save_image()` 函数

```python
save_image(source, name)
```

将图片写入小组件可用的缓存通道（通过特殊格式的 `print` 输出，由 App 解析）。

| 参数 | 类型 | 说明 |
|------|------|------|
| `source` | `str` \| `bytes` | **`str`**：本地文件路径，按二进制读取；**`bytes`**：原始图像数据 |
| `name` | `str` | 缓存引用名（**不要扩展名**），与 `Widget.image(name)` 对应 |

### 行为（与源码一致）

- 若 `source` 既不是 `str` 也不是 `bytes`，抛出 **`TypeError`**。
- 若数据大小 **超过 512KB**：向 **stderr** 打印中文警告，然后调用 **`_compress_image`**：
  - 若已安装 **PIL**：尝试以 JPEG 质量阶梯压缩，必要时缩小尺寸，直至不超过 512KB。
  - 若 **无法导入 PIL**：**截断**为前 `512 * 1024` 字节（可能损坏图片文件，建议安装 PIL）。

模块顶部的 `save_image` 文档字符串中提到的 `ValueError` 与当前实现不一致；**实际实现以压缩/截断为主**，不单纯因超限抛错。

**典型用法：**

```python
save_image("/path/to/img.png", "my_pic")
# 之后在 DSL 中：
w.image("my_pic", width=60, height=60, corner_radius=8)
```

---

## 颜色系统

与 `_resolve_color` / `_set_background` / `_set_color` 行为一致：

1. **单色字符串**：`"#FF6B6B"`、`"red"`、`"white"` 等。
2. **深浅色适配**：`("#000", "#FFF")` 或 `["#000", "#FFF"]`（至少 2 个元素）→ 浅色模式用第一项，深色模式用第二项（对应 JSON 中的 `dark*` 字段）。
3. **渐变**（根、`Widget` 背景、容器、`card`）：`{"gradient": ["#FF6B6B", "#4ECDC4"], "direction": "diagonal"}`  
   - `gradient`：至少两种颜色。  
   - `direction`（可选）：`"diagonal"`（默认）、`"horizontal"`、`"vertical"`、`"reverse_diagonal"`。

---

## 限制

1. **节点上限：50**  
   每追加一个节点（含 `text`、`icon`、`spacer`、`divider`、`progress`、`gauge`、`timer`、`image` 以及每个容器节点等），内部计数器 `+1`。  
   - 当计数达到 **45**（`_MAX_NODES - 5`）时，向 **stderr** 打印警告。  
   - 当计数 **超过 50** 时，抛出 **`RuntimeError`**（第 51 个节点添加时触发）。

2. **图片大小**  
   单张原始数据 **> 512KB** 时会触发压缩逻辑（见 `save_image`）；目标为不超过 512KB 的缓存策略。

---

## 完整示例

```python
from widget import Widget, family, SMALL, MEDIUM, save_image

w = Widget(background=("#1a1a2e", "#0f0f1a"))

with w.vstack(spacing=8, padding=12):
    w.text("🔥 今日目标", size=13, color="#aaa")
    with w.hstack(spacing=12):
        w.gauge(0.75, label="75%", size=50, color="#FF6B6B", track_color="#333")
        with w.vstack(spacing=4, align="leading"):
            w.text("步数 8,432", size=14, weight="semibold", color="white")
            w.text("目标 10,000", size=12, color="#888")
    w.divider(color="#333")
    w.progress(0.6, color="#4ECDC4", height=6, track_color="#222")

w.render()
```

可按 `family` 分支为 `SMALL` / `MEDIUM` 等编写不同布局（同一脚本会被系统按尺寸多次执行）。

---

## 注意事项

1. **多次运行与 `family`**：系统通常会 **按每种小组件尺寸分别调用** 脚本；用 **`family`**（环境变量 `WIDGET_FAMILY`）判断当前这一次对应哪一档尺寸。
2. **渐变背景**：支持在 **`Widget` 根**、**`hstack` / `vstack` / `zstack`** 以及 **`card`** 上使用渐变字典。
3. **`render()`**：必须在构建完整棵树之后调用（一般在 **脚本末尾**），否则不会输出布局 JSON。
4. **`timer`**：基于 **WidgetKit** 原生能力，倒计时可精确到秒级显示，**无需**在 Python 侧手动刷新 timeline。
5. **快捷方式 `show()`**：适合模板化数据；需要 SF Symbol、渐变、嵌套卡片等能力时，优先使用 **`Widget` DSL**。

---

## 与 Swift / App 的契约摘要

- `show()` → 单行打印：`__WIDGET__` + JSON + `__WIDGET__`  
- `Widget.render()` → 单行打印：`__WIDGET_LAYOUT__` + JSON + `__WIDGET_LAYOUT__`  
- `save_image()` → 含 `__WIDGET_IMG__{name}:{base64}__WIDGET_IMG__` 的输出  

详细字段名以 `pyboot/widget.py` 中构建的 `dict` 为准（如 `layoutStyle`、`backgroundColor`、`maxLines`、`contentMode`、`timerStyle`、`targetDate` 等）。
