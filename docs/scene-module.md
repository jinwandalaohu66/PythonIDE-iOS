# scene 模块 — 2D 游戏与动画引擎

基于 **SpriteKit** 的 Pythonista 兼容 2D 游戏/动画引擎。Python 侧实现位于 `pyboot/scene.py`，通过 ctypes 调用原生桥接；Classic 即时绘图 API 由 `pyboot/scene_drawing.py` 提供，并可通过 `scene` 模块的延迟导入直接使用（例如 `scene.fill`）。

**坐标系**：原点位于**左下角** `(0, 0)`，**y 轴向上**。这与 `ui` 模块（左上角原点、y 向下）相反，布局时务必区分。

---

## 坐标系

| 项目 | 说明 |
|------|------|
| 原点 | 左下角 `(0, 0)` |
| y 轴 | 向上为正 |
| 场景尺寸 | 在 `setup()` 及之后的生命周期回调中，使用 `self.size`（`Size` 类型），常用 `self.size.w`、`self.size.h` 表示逻辑分辨率下的宽、高 |
| 安全区域 | `self.safe_area_insets` → `EdgeInsets(top, bottom, left, right)`，单位与场景点一致；用于避开刘海、Home 指示条等 |

---

## 几何类型

### `Vector2(x, y)`

二维向量基类。

- **运算**：支持 `+`、`-`、`*`、`/`（标量或与另一向量分量相除）
- **`abs()`**：返回模长 `sqrt(x²+y²)`
- **`[]` / 迭代**：`[0]`→`x`，`[1]`→`y`；可迭代为 `(x, y)`
- 与 `tuple`/`list`（长度≥2）参与 `+`、`-`、`*` 时按分量运算

### `Point(x, y)`

`Vector2` 的子类，表示**位置**（与 `Vector2` 等价别名用途）。

### `Size(x, y)`

`Vector2` 的子类，表示**尺寸**。除 `x`、`y` 外提供：

- **`w`** / **`h`**：`x` / `y` 的别名属性（可读写）

### `Rect(x, y, w, h)`

轴对齐矩形，**原点为左下角**的 `(x, y)`，宽 `w`、高 `h`。

**属性**

- `width` / `height`：同 `w` / `h`
- `origin` → `Point`
- `size` → `Size`
- `min_x`, `max_x`, `min_y`, `max_y`

**方法**

- `center(p=None)`：`p is None` 时返回中心点 `Point`；否则将矩形中心移到 `p` 并返回 `p`
- `contains_point(p)`、`contains_rect(r)`
- `intersects(r)`、`intersection(r)`、`union(r)`
- `inset(top, left, bottom=None, right=None)`：`bottom`/`right` 缺省时分别默认等于 `top`/`left`，返回内缩后的新 `Rect`
- **`in` 运算符**：`point in rect` 支持 `Point` 或 `(x, y)` 序列

### `Vector3(x, y, z)`

三维向量，例如配合设备重力等（见模块函数 `gravity()`）。

### `EdgeInsets(top, bottom, left, right)`

安全区域边距，字段：`top`, `bottom`, `left`, `right`。

---

## `Scene` 类

### 构造与背景

```python
class MyScene(Scene):
    def __init__(self):
        super().__init__()
        self.background_color = (r, g, b, a)  # 各分量通常为 0.0–1.0
```

基类 `__init__` 中默认 `background_color = (0.2, 0.2, 0.2, 1.0)`。

### 主要属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `size` | `Size` | 场景逻辑尺寸（`setup` 时由桥接设置） |
| `bounds` | `Rect` | `Rect(0, 0, size.w, size.h)` |
| `background_color` | 元组 | `(r, g, b, a)` |
| `t` | `float` | 场景启动以来的时间（秒） |
| `dt` | `float` | 上一帧到当前帧的时间间隔（秒），在 `update()` 中有意义 |
| `touches` | `dict` | 当前按下未起的触摸，`touch_id` → `Touch` |
| `physics_world` | `PhysicsWorld` | 物理世界（重力等） |
| `safe_area_insets` | `EdgeInsets` | 调用 `get_safe_area_insets()` 的便捷属性 |

### 生命周期回调（子类重写）

| 回调 | 说明 |
|------|------|
| `setup()` | 场景开始时**调用一次**；此时 `self.size` 已可用 |
| `update()` | **每帧**在绘制前调用 |
| `draw()` | **Classic 模式**：每帧调用，内用 `scene`/`scene_drawing` 绘图函数 |
| `touch_began(touch)` / `touch_moved(touch)` / `touch_ended(touch)` | 触摸事件 |
| `did_change_size()` | 尺寸或方向变化（如旋转）后调用 |
| `contact_began(contact)` | 物理**接触开始**时调用，参数为 `Contact`（需实现物理体与掩码） |
| `pause()` / `resume()` | 应用进入后台 / 回到前台 |
| `stop()` | 场景结束或关闭时 |

### 方法

- `add_child(node)`：将节点加到场景根节点
- `present_modal_scene(scene)`：以模态方式叠放另一场景
- `dismiss_modal_scene()`：关闭**当前**作为模态展示的场景（在模态场景实例上调用）

---

## `Touch` 类

由引擎构造，无需自行实例化。

| 属性 | 类型 | 说明 |
|------|------|------|
| `location` | `Point` | 当前触点位置 |
| `prev_location` | `Point` | 上一位置 |
| `touch_id` | `int` | 触摸跟踪 ID |

---

## `Node` 类

### 构造

```python
Node(
    position=(0, 0),
    z_position=0,
    scale=1,
    x_scale=1,
    y_scale=1,
    alpha=1,
    parent=None,
)
```

内部会将 **`x_scale`、`y_scale` 设为 `scale * x_scale`、`scale * y_scale`**。若指定 `parent`，会自动 `parent.add_child(self)`。

### 属性

| 属性 | 说明 |
|------|------|
| `position` | `Point`，可读可写；可赋 `Point` 或序列 |
| `rotation` | **弧度**；可读可写 |
| `x_scale` / `y_scale` | 缩放 |
| `alpha` | 透明度；**注意**：源码中 getter 固定返回 `1.0`，实际透明度以 setter 下发为准 |
| `z_position` | 深度顺序 |
| `physics_body` | `PhysicsBody` 或 `None` |
| `frame` / `bbox` | 只读 `Rect`（来自原生层） |
| `blend_mode` | 见常量 `BLEND_*` |
| `shader` | `Shader` 或 `None` |

### 方法

- `add_child(node)`
- `remove_from_parent()`
- `run_action(action, key=None)`
- `remove_action(key)`、`remove_all_actions()`

---

## `SpriteNode` 类（继承 `Node`）

### 构造

```python
SpriteNode(
    texture=None,
    position=(0, 0),
    z_position=0,
    scale=1,
    color='white',
    size=None,
    parent=None,
)
```

- **`texture`**：`str`（内置图名如 `'plc:Alien_Green'`、或文件路径若存在则按文件加载）、`Texture` 实例、或 `None`（纯色矩形）
- **`color`**：颜色名或 `ui.parse_color` 可解析的字符串
- **`size`**：可选 `(w, h)`；**注意**：当前 `size` 的 property setter 为空实现，动态改尺寸能力取决于纹理与原生实现

### 属性

- `size`：可读；写入在源码中未桥接到原生（setter 为 `pass`）
- `anchor_point`：默认约 `(0.5, 0.5)`，可读可写
- `color`：可读可写

---

## `LabelNode` 类（继承 `Node`）

### 构造

```python
LabelNode(
    text,
    font=('Helvetica', 20),
    position=(0, 0),
    z_position=0,
    parent=None,
    color=None,
    font_color=None,
)
```

`color` 与 `font_color` 通过 `**kwargs` 传入，二者等价用途（任设其一即可）。

### 属性

- `text`、`font`（`(name, size)`）、`color`
- `alignment`：`(horizontal, vertical)`  
  - horizontal：`0`=Center，`1`=Left，`2`=Right  
  - vertical：`0`=Center，`1`=Top，`2`=Bottom，`3`=Baseline  

---

## `ShapeNode` 类（继承 `Node`）

### 构造

```python
ShapeNode(
    path=None,
    fill_color='white',
    stroke_color='clear',
    position=(0, 0),
    z_position=0,
    parent=None,
)
```

### `path` 元组格式

- `('rect', x, y, w, h)` 或 `('rect', x, y, w, h, corner_radius)`
- `('oval', x, y, w, h)`

### 属性与方法

- `fill_color`、`stroke_color`（字符串，含 `'clear'` 等）
- `set_path(path)`：按上述元组更新路径

---

## `EmitterNode` 类（继承 `Node`）

```python
EmitterNode(file_named=None, position=(0, 0), z_position=0, parent=None)
```

`file_named` 为粒子系统资源名（由应用包内资源决定，具体格式与 Pythonista/工程资源一致）。

---

## `Texture` 类

```python
Texture(name_or_image)
```

- **`name_or_image`**：`str`（若路径存在则按文件创建，否则作为纹理名/ID 使用）、或带 `to_base64()` / `to_png()` 的对象（如 `ui.Image`）用于上传纹理  
- 属性 **`size`** → `Size`（通过桥接查询）

---

## `Shader` 类

```python
Shader(source)  # GLSL 片段着色器源码字符串
```

- `set_uniform(name, value)`：设置 **float** 型 uniform；**仅在已赋值给某 `Node.shader` 后**才会向原生层发送

---

## `Action` 类

均为**静态工厂方法**，返回 `Action` 实例。凡移动/旋转/缩放/淡入淡出类动作，均可选 **`timing_mode`**（默认 `TIMING_LINEAR`），对应**最后一个**参数。

| 方法 | 说明 |
|------|------|
| `move_to(x, y, duration=0.5, timing_mode=TIMING_LINEAR)` | 移动到 |
| `move_by(dx, dy, duration=0.5, timing_mode=TIMING_LINEAR)` | 相对移动 |
| `rotate_to(angle, duration=0.5, timing_mode=TIMING_LINEAR)` | **弧度** |
| `rotate_by(angle, duration=0.5, timing_mode=TIMING_LINEAR)` | **弧度** |
| `scale_to(scale, duration=0.5, timing_mode=TIMING_LINEAR)` | 统一缩放 |
| `scale_by(scale, duration=0.5, timing_mode=TIMING_LINEAR)` | 相对缩放 |
| `fade_to(alpha, duration=0.5, timing_mode=TIMING_LINEAR)` | 透明度 |
| `fade_by(alpha, duration=0.5, timing_mode=TIMING_LINEAR)` | 相对透明度 |
| `sequence(*actions)` | 顺序执行 |
| `group(*actions)` | 同时执行 |
| `repeat(action, count)` | 重复 `count` 次 |
| `repeat_forever(action)` | 内部为 `repeat(action, 0)` |
| `wait(duration)` | 等待（无 `timing_mode` 参数） |
| `call(callback, scene=None)` | 执行无参可调用对象；`scene` 默认取当前已注册场景以派发回调 |
| `remove()` | 从父节点移除 |

使用：`node.run_action(Action.sequence(...), key='anim')`。

---

## `PhysicsBody` 类

### 工厂

- `PhysicsBody.rectangle(w, h)`
- `PhysicsBody.circle(r)`（内部用直径 `2*r` 传给原生矩形近似/圆形类型，见源码）

### 属性

- `affected_by_gravity`、`allows_rotation`、`dynamic`：`bool`
- `restitution`、`friction`、`linear_damping`：浮点（阻尼等为桥接约定）
- `velocity`：`Vector2`，可读可写
- `category_bitmask`、`collision_bitmask`、`contact_test_bitmask`：32 位掩码（与 `Contact` / `contact_began` 配合）

### 方法

- `apply_impulse(x, y)`

将 `node.physics_body = body` 时绑定到节点并同步到 SpriteKit。

---

## `PhysicsWorld` 类

通过 **`scene.physics_world`** 访问。

- **`gravity`**：`Vector2`  
  - **赋值**时通过 `scene_set_gravity` 同步到原生  
  - **读取**时 Python 侧默认返回 `Vector2(0, -9.8)`，未必反映运行时真实值（以 setter 与原生为准）

---

## `Contact` 类

在 `Scene.contact_began(contact)` 中接收。

| 属性 | 说明 |
|------|------|
| `node_a`, `node_b` | 碰撞涉及的节点 |
| `body_a`, `body_b` | 与 `node_a`/`node_b` 相同引用（兼容部分脚本） |
| `contact_point` | `Point`，接触点 |
| `collision_impulse` | `float`，冲量标量 |

---

## 关节（Joints）

- **`PinJoint(node_a, node_b, anchor)`**：铰链/销钉，`anchor` 为 `(x, y)`
- **`SpringJoint(node_a, node_b, anchor_a, anchor_b, damping=0.5, frequency=1.0)`**
- **`RopeJoint(node_a, node_b, anchor_a, anchor_b)`**：限制最大距离

均在构造时调用原生创建关节。

---

## `SceneView` 类

将场景嵌入 `ui` 界面：

```python
sv = SceneView()
sv.scene = MyScene()
v = sv.view   # ui.View，可 add_subview
```

| 属性 | 说明 |
|------|------|
| `paused` | `bool` |
| `frame_interval` | `int`，≥1 |

---

## Classic 绘图 API（`scene_drawing` / `scene.*`）

在 **`Scene.draw()`** 中调用。可直接 `import scene` 后使用 `scene.fill`、`scene.rect` 等（模块级延迟加载），或 `import scene_drawing as sd`。

| 函数 | 说明 |
|------|------|
| `background(r, g, b)` | 清屏背景色 |
| `fill(r, g, b, a)` / `no_fill()` | 填充 |
| `stroke(r, g, b, a)` / `no_stroke()` | 描边 |
| `stroke_weight(w)` | 线宽 |
| `rect(x, y, w, h, corner_radius=0)` | 矩形 |
| `ellipse(x, y, w, h)` | 椭圆（外接矩形） |
| `line(x1, y1, x2, y2)` | 线段 |
| `image(name, x, y, w, h, from_x, from_y, from_w, from_h)` | 绘制已注册名称的图像；后四个为可选子区域（未传时用占位值表示整图，见桥接） |
| `text(txt, font_name, font_size, x, y, alignment)` | `alignment`：1–9 小键盘布局，**5=居中** |
| `tint(r, g, b, a)` / `no_tint()` | 图像与文字着色 |
| `translate(x, y)`、`rotate(deg)`、`scale(x, y)` | 变换；**`rotate` 为度** |
| `push_matrix()` / `pop_matrix()` | 矩阵栈 |
| `load_image_file(path)` | 返回供 `image(name, ...)` 使用的名称，失败可能为 `None` |
| `render_text(txt, font_name, font_size)` | 返回 `(name, Size)`，供 `image` 绘制文字纹理 |

以下在 `scene_drawing` 中存在但为占位或未完全桥接：`blend_mode`、`use_shader`、`load_image`、`load_pil_image`、`unload_image`、`image_quad`、`triangle_strip`。

---

## 模块级函数

```python
run(
    scene,
    orientation=DEFAULT_ORIENTATION,
    frame_interval=1,
    anti_alias=False,
    show_fps=False,
    multi_touch=True,
    _mode='auto',  # 内部：'main' 为主线程模式（IDE「Scene 模式运行」会设置）
)
```

| 函数 | 返回值 | 说明 |
|------|--------|------|
| `get_screen_size()` | `Size` | 屏幕逻辑尺寸 |
| `get_screen_scale()` | `float` | 像素比例（如 Retina 2.0） |
| `gravity()` | `Vector3` | 设备重力向量（约 0–1 量级，依设备） |
| `get_safe_area_insets()` | `EdgeInsets` | 安全区；API 不可用时返回全 0 |
| `play_effect(name, volume=1.0, pitch=1.0)` | — | 播放音效 |
| `get_image_path(name)` | `str` \| `None` | 内置资源路径 |

---

## 常量

### 方向

- `DEFAULT_ORIENTATION = 0`
- `PORTRAIT = 1`
- `LANDSCAPE = 2`

### 混合模式

- `BLEND_NORMAL = 0`
- `BLEND_ADD = 1`
- `BLEND_MULTIPLY = 2`

### 缓动（共 16 种，作 `timing_mode` 传入 Action）

- `TIMING_LINEAR = 0`
- `TIMING_EASE_IN = 1`, `TIMING_EASE_IN_2 = 2`
- `TIMING_EASE_OUT = 3`, `TIMING_EASE_OUT_2 = 4`
- `TIMING_EASE_IN_OUT = 5`
- `TIMING_SINODIAL = 6`
- `TIMING_ELASTIC_IN = 7`, `TIMING_ELASTIC_OUT = 8`, `TIMING_ELASTIC_IN_OUT = 9`
- `TIMING_BOUNCE_IN = 10`, `TIMING_BOUNCE_OUT = 11`, `TIMING_BOUNCE_IN_OUT = 12`
- `TIMING_EASE_BACK_IN = 13`, `TIMING_EASE_BACK_OUT = 14`, `TIMING_EASE_BACK_IN_OUT = 15`

源码中另有纹理过滤常量 `FILTERING_LINEAR`、`FILTERING_NEAREST`（未在 Pythonista 最小集中列出时可按需使用）。

---

## 完整示例：弹跳球（Node + 物理 + 动画）

下列示例演示：`Scene` 子类、`setup`/`update`/`touch_began`、`ShapeNode` 地面与圆球、`self.size` 布局、`PhysicsBody` 重力与碰撞、`Action` 缩放脉冲。运行方式：`run(BounceScene())`。

```python
from scene import *


class BounceScene(Scene):
    def setup(self):
        w, h = self.size.w, self.size.h
        self.background_color = (0.15, 0.18, 0.22, 1.0)

        # 地面（静态矩形）
        ground_h = 36
        self.ground = ShapeNode(
            path=('rect', 0, 0, w, ground_h),
            fill_color='#444',
            stroke_color='clear',
            position=(0, 0),
        )
        self.add_child(self.ground)
        gb = PhysicsBody.rectangle(w, ground_h)
        gb.dynamic = False
        gb.affected_by_gravity = False
        self.ground.physics_body = gb

        # 球
        r = 24
        self.ball = ShapeNode(
            path=('oval', -r, -r, 2 * r, 2 * r),
            fill_color='orange',
            stroke_color='white',
            position=(w * 0.5, h * 0.55),
        )
        self.add_child(self.ball)
        bb = PhysicsBody.circle(r)
        bb.restitution = 0.85
        bb.friction = 0.4
        self.ball.physics_body = bb

        self.physics_world.gravity = (0, -18)

    def touch_began(self, touch):
        # 点击时给一个冲量并播放缩放动画
        if self.ball.physics_body:
            self.ball.physics_body.apply_impulse(0, 120)
        pulse = Action.sequence(
            Action.scale_to(1.15, 0.08, TIMING_EASE_OUT),
            Action.scale_to(1.0, 0.12, TIMING_EASE_IN),
        )
        self.ball.run_action(pulse, key='pulse')

    def update(self):
        pass


if __name__ == '__main__':
    run(BounceScene(), show_fps=True)
```

---

## 注意事项

1. **坐标系**：左下角为原点、y 向上；与 `ui` 相反，勿混用坐标习惯。
2. **布局**：全屏或自适应请使用 **`self.size.w` / `self.size.h`**（及 `did_change_size`），勿硬编码像素。
3. **安全区**：HUD、按钮等建议用 **`safe_area_insets` 或 `get_safe_area_insets()`** 留白。
4. **导入**：`from scene import *` 与 `__all__` 一致，可一次性导入节点、动作、常量及绘图名。
5. **Action 缓动**：`timing_mode` 作为各工厂方法**最后一个**参数传入（`wait` 除外）。
6. **实现细节**：`Node.alpha` 的 getter 在源码中恒为 `1.0`；`SpriteNode.size` 的 setter 未桥接；`PhysicsWorld.gravity` 读取值为 Python 侧默认值，以写入为准。
7. **`run(..., _mode='main')`**：由 IDE 场景运行入口使用，保证回调在主线程执行；普通脚本默认 `_mode='auto'`。

---

*文档版本对应源码：`pyboot/scene.py`、`pyboot/scene_drawing.py`。*
