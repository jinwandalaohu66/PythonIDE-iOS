# scene 模块 — 2D 游戏与动画引擎

基于 **SpriteKit** 的 Pythonista 兼容 2D 游戏/动画引擎。Python 侧实现位于 `pyboot/scene.py`，通过 ctypes 调用原生桥接（`pythonide/SceneBridge.swift`）；Classic 即时绘图 API 由 `pyboot/scene_drawing.py` 提供，并可通过 `scene` 模块的延迟导入直接使用（例如 `scene.fill`）。

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

二维向量基类，`Point` 和 `Size` 均继承自它。

**运算符**（全部支持）：

| 运算 | 说明 |
|------|------|
| `+` `-` `*` `/` | 与标量或另一向量分量运算，返回 `Vector2` |
| `+=` `-=` `*=` `/=` | 就地运算（`__iadd__` 等） |
| 反向运算 | `3 * v`、`(1,2) + v` 等（`__radd__`、`__rsub__`、`__rmul__`） |
| `-v` | 取反（`__neg__`） |
| `==` `!=` | 值比较 |
| `hash()` | 可哈希（可用作字典键） |
| `bool(v)` | 非零向量为 `True` |
| `abs(v)` | 返回模长 `sqrt(x² + y²)` |
| `v[0]` `v[1]` | 索引访问 |
| `iter(v)` | 可迭代为 `(x, y)` |
| `len(v)` | 返回 `2` |

### `Point(x, y)`

`Vector2` 的子类，表示**位置**。算术运算返回 `Point`（而非基类 `Vector2`）。

### `Size(x, y)`

`Vector2` 的子类，表示**尺寸**。除 `x`、`y` 外提供：

- **`w`** / **`h`**：`x` / `y` 的别名属性（可读写）
- 算术运算返回 `Size`（而非基类 `Vector2`）

### `Rect(x, y, w, h)`

轴对齐矩形，**原点为左下角**的 `(x, y)`，宽 `w`、高 `h`。

**属性**

- `width` / `height`：同 `w` / `h`
- `origin` → `Point`
- `size` → `Size`
- `min_x`、`max_x`、`min_y`、`max_y`
- `center` → `Point`（中心点）

**方法**

- `contains_point(p)`、`contains_rect(r)`
- `intersects(r)`、`intersection(r)`、`union(r)`
- `inset(top, left, bottom=None, right=None)`：`bottom`/`right` 缺省时分别默认等于 `top`/`left`，返回内缩后的新 `Rect`
- `translate(dx, dy)` → `Rect`：返回平移后的新矩形

**运算符**

- `point in rect`：支持 `Point` 或 `(x, y)` 序列
- `==`、`hash()`、`len(rect)` → `4`
- `__repr__`：`Rect(x, y, w, h)` 格式

### `Vector3(x, y, z)`

三维向量，例如配合设备重力（见 `gravity()`）。支持 `[0]`/`[1]`/`[2]` 索引、`iter`、`len()` → `3`。

### `EdgeInsets(top, bottom, left, right)`

安全区域边距，字段：`top`、`bottom`、`left`、`right`。

---

## `Scene` 类

### 构造与背景

```python
class MyScene(Scene):
    def setup(self):
        self.background_color = '#2c3e50'  # 支持颜色名、'#RRGGBB'、元组、灰度浮点
```

基类 `__init__` 中默认 `background_color = (0.2, 0.2, 0.2, 1.0)`。

### 主要属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `size` | `Size` | 场景逻辑尺寸（`setup` 时由桥接设置） |
| `bounds` | `Rect` | `Rect(0, 0, size.w, size.h)` |
| `background_color` | 元组 | 设置时支持颜色名/`#RRGGBB`/元组/灰度浮点；**读取始终返回 `(r,g,b,a)` 4-tuple** |
| `t` | `float` | 场景启动以来的时间（秒） |
| `dt` | `float` | 上一帧到当前帧的时间间隔（秒） |
| `touches` | `dict` | 当前按下未起的触摸，`touch_id` → `Touch` |
| `physics_world` | `PhysicsWorld` | 物理世界（重力等） |
| `safe_area_insets` | `EdgeInsets` | 调用 `get_safe_area_insets()` 的便捷属性 |
| `view` | `SceneView` | 当前场景所在的视图（只读，运行后可用） |
| `presented_scene` | `Scene` / `None` | 当前模态呈现的子场景 |
| `presenting_scene` | `Scene` / `None` | 呈现本场景的父场景 |
| `effects_enabled` | `bool` | 是否启用 EffectNode 效果（默认 `False`） |
| `crop_rect` | `Rect` / `None` | EffectNode 裁剪区域 |

### 生命周期回调（子类重写）

| 回调 | 说明 |
|------|------|
| `setup()` | 场景开始时**调用一次**；此时 `self.size` 已可用 |
| `update()` 或 `update(dt)` | **每帧**在绘制前调用；两种签名均支持，推荐使用 `self.dt` |
| `draw()` | **Classic 模式**：每帧调用，内用绘图函数 |
| `did_evaluate_actions()` | 所有 Action 执行完毕后调用（每帧 `update` 之后） |
| `touch_began(touch)` / `touch_moved(touch)` / `touch_ended(touch)` | 触摸事件 |
| `did_change_size()` | 尺寸或方向变化（如旋转）后调用 |
| `contact_began(contact)` | 物理**接触开始**时调用（需配置物理体与掩码） |
| `pause()` / `resume()` | 应用进入后台 / 回到前台 |
| `stop()` | 场景结束或关闭时 |
| `controller_changed()` | 游戏控制器连接/断开时调用 |

### 方法

- `add_child(node)`：将节点加到场景根节点
- `present_modal_scene(scene)`：以模态方式叠放另一场景（自动设置 `presented_scene`/`presenting_scene`）
- `dismiss_modal_scene()`：关闭当前模态场景（自动清除引用）

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
    speed=1,
    parent=None,
)
```

内部会将 **`x_scale`、`y_scale` 设为 `scale * x_scale`、`scale * y_scale`**。若指定 `parent`，会自动 `parent.add_child(self)`。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `position` | `Point` | 可读可写；可赋 `Point` 或序列 |
| `rotation` | `float` | 弧度；可读可写 |
| `x_scale` / `y_scale` | `float` | 缩放 |
| `alpha` | `float` | 透明度 |
| `z_position` | `float` | 深度顺序 |
| `speed` | `float` | Action 执行速度倍率（默认 1.0，设为 0 暂停动画） |
| `paused` | `bool` | 节点及子树是否暂停 |
| `blend_mode` | `int` | 混合模式，见常量 `BLEND_*` |
| `physics_body` | `PhysicsBody` / `None` | 物理刚体 |
| `shader` | `Shader` / `None` | 自定义着色器 |
| `frame` / `bbox` | `Rect` | 只读，全局坐标包围盒 |
| `scene` | `Scene` / `None` | 所属场景（只读，沿 parent 链查找） |
| `children` | `list` | 子节点列表（只读） |
| `parent` | `Node` / `None` | 父节点（只读） |

### 方法

| 方法 | 说明 |
|------|------|
| `add_child(node)` | 添加子节点 |
| `remove_from_parent()` | 从父节点移除 |
| `run_action(action, key=None)` | 执行动作 |
| `remove_action(key)` | 移除指定动作 |
| `remove_all_actions()` | 移除所有动作 |
| `point_to_scene(point)` | 将本节点坐标转为场景坐标，返回 `Point` |
| `point_from_scene(point)` | 将场景坐标转为本节点坐标，返回 `Point` |
| `render_to_texture(crop_rect=None)` | 将节点渲染为 `Texture`，可选裁剪区域 |

---

## `SpriteNode` 类（继承 `Node`）

### 构造

```python
SpriteNode(
    texture=None,
    position=(0, 0),
    z_position=0,
    scale=1,
    x_scale=1,
    y_scale=1,
    alpha=1,
    speed=1,
    color='white',
    size=None,
    blend_mode=BLEND_NORMAL,
    parent=None,
)
```

- **`texture`**：`str`（内置图名如 `'plc:Alien_Green'`、或文件路径）、`Texture` 实例、或 `None`（纯色矩形）
- **`color`**：颜色名、`'#RRGGBB'`、`(r,g,b[,a])` 元组、或 `0.0-1.0` 灰度浮点
- **`size`**：可选 `(w, h)`；**无纹理时必须指定 `size`，否则不可见**

### 属性

| 属性 | 说明 |
|------|------|
| `size` | `Size`，可读 |
| `anchor_point` | 默认 `(0.5, 0.5)`，可读可写 |
| `color` | 设置时支持任意颜色格式；**读取始终返回 `(r,g,b,a)` 4-tuple** |

---

## `LabelNode` 类（继承 `Node`）

### 构造

```python
LabelNode(
    text,
    font=('Helvetica', 20),
    position=(0, 0),
    z_position=0,
    scale=1,
    x_scale=1,
    y_scale=1,
    alpha=1,
    speed=1,
    parent=None,
    color=None,
)
```

### 属性

| 属性 | 说明 |
|------|------|
| `text` | `str`，文本内容 |
| `font` | `(name, size)` 元组 |
| `color` | 设置时支持任意颜色格式；**读取始终返回 `(r,g,b,a)` 4-tuple** |
| `alignment` | `(horizontal, vertical)`：水平 0=Center 1=Left 2=Right；垂直 0=Center 1=Top 2=Bottom 3=Baseline |

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
    scale=1,
    x_scale=1,
    y_scale=1,
    alpha=1,
    speed=1,
    line_width=1,      # 别名 stroke_width
    shadow=None,
    parent=None,
)
```

### `path` 格式

支持两种格式：

**`ui.Path` 对象**（推荐）：

```python
import ui
path = ui.Path.rect(0, 0, 100, 50)
path = ui.Path.oval(0, 0, 80, 80)
path = ui.Path.rounded_rect(0, 0, 100, 50, 10)
```

**元组格式**：

- `('rect', x, y, w, h)` 或 `('rect', x, y, w, h, corner_radius)`
- `('oval', x, y, w, h)`

### 属性与方法

| 属性/方法 | 说明 |
|------|------|
| `fill_color` | 设置时支持任意颜色格式；**读取始终返回 `(r,g,b,a)` 4-tuple** |
| `stroke_color` | 同上 |
| `line_width` | 描边宽度（`stroke_width` 为别名） |
| `shadow` | `(color, x_offset, y_offset, blur_radius)` 元组，阴影效果 |
| `set_path(path)` | 更新路径（支持 `ui.Path` 或元组格式） |

---

## `EmitterNode` 类（继承 `Node`）

```python
EmitterNode(
    file_named=None,
    position=(0, 0),
    z_position=0,
    scale=1,
    x_scale=1,
    y_scale=1,
    alpha=1,
    speed=1,
    parent=None,
)
```

`file_named` 为粒子系统资源名。

---

## `EffectNode` 类（继承 `Node`）

特效容器节点，子节点可应用滤镜/裁剪效果。

```python
EffectNode(
    position=(0, 0),
    z_position=0,
    parent=None,
)
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `effects_enabled` | `bool` | 是否启用特效渲染（默认 `False`） |
| `crop_rect` | `Rect` / `None` | 裁剪区域 |

---

## `Texture` 类

```python
Texture(name_or_image)
```

- **`name_or_image`**：`str`（若路径存在则按文件创建，否则作为纹理名/ID 使用）、或带 `to_base64()` / `to_png()` 的对象（如 `ui.Image`）

| 属性 | 类型 | 说明 |
|------|------|------|
| `size` | `Size` | 纹理尺寸 |
| `filtering_mode` | `int` | `FILTERING_LINEAR`（0，默认平滑）或 `FILTERING_NEAREST`（1，像素风格） |

---

## `Shader` 类

```python
Shader(source)  # GLSL 片段着色器源码字符串
```

### 方法

| 方法 | 说明 |
|------|------|
| `set_uniform(name, value)` | 设置 uniform 值。`value` 支持：`float`、`(x,y)` vec2、`(x,y,z)` vec3、`(r,g,b,a)` vec4、`Texture` 对象 |
| `get_uniform(name)` | 获取 uniform 当前值（返回 `float`） |

**注意**：仅在已赋值给某 `Node.shader` 后，`set_uniform` 才会向原生层发送。

---

## `Action` 类

均为**静态工厂方法**，返回 `Action` 实例。每个实例包含 `duration` 和 `timing_mode` 属性。

### 移动 / 旋转 / 缩放 / 透明度

| 方法 | 说明 |
|------|------|
| `move_to(x, y, duration=0.5, timing_mode=TIMING_LINEAR)` | 移动到绝对位置 |
| `move_by(dx, dy, duration=0.5, timing_mode=TIMING_LINEAR)` | 相对移动 |
| `rotate_to(angle, duration=0.5, timing_mode=TIMING_LINEAR)` | 旋转到角度（弧度） |
| `rotate_by(angle, duration=0.5, timing_mode=TIMING_LINEAR)` | 相对旋转（弧度） |
| `scale_to(scale, duration=0.5, timing_mode=TIMING_LINEAR)` | 统一缩放 |
| `scale_by(scale, duration=0.5, timing_mode=TIMING_LINEAR)` | 相对缩放 |
| `scale_x_to(x_scale, duration=0.5, timing_mode=TIMING_LINEAR)` | 仅缩放 x 轴 |
| `scale_y_to(y_scale, duration=0.5, timing_mode=TIMING_LINEAR)` | 仅缩放 y 轴 |
| `fade_to(alpha, duration=0.5, timing_mode=TIMING_LINEAR)` | 淡入淡出到目标透明度 |
| `fade_by(alpha, duration=0.5, timing_mode=TIMING_LINEAR)` | 相对透明度变化 |

### 控制与回调

| 方法 | 说明 |
|------|------|
| `wait(duration)` | 等待指定秒数 |
| `remove()` | 从父节点移除 |
| `call(callback)` | 执行无参回调函数 |
| `call(callback, duration=1.0)` | 带进度回调：`callback(node, progress)`，`progress` 从 0.0 到 1.0 |
| `set_uniform(name, value, duration)` | 动画插值 shader uniform 值 |

### 组合

| 方法 | 说明 |
|------|------|
| `sequence(*actions)` | 顺序执行；也可传列表 `sequence([a1, a2])` |
| `group(*actions)` | 并行执行；也可传列表 `group([a1, a2])` |
| `repeat(action, count)` | 重复 `count` 次 |
| `repeat_forever(action)` | 无限重复 |

**用法**：`node.run_action(Action.sequence(...), key='anim')`

---

## `PhysicsBody` 类

### 工厂

- `PhysicsBody.rectangle(w, h)`
- `PhysicsBody.circle(r)`

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `dynamic` | `bool` | `True` = 受物理模拟控制 |
| `affected_by_gravity` | `bool` | 是否受重力影响 |
| `allows_rotation` | `bool` | 是否允许旋转 |
| `mass` | `float` | 质量（千克） |
| `density` | `float` | 密度 |
| `restitution` | `float` | 弹性系数（0–1） |
| `friction` | `float` | 摩擦系数（0–1） |
| `linear_damping` | `float` | 线性阻尼 |
| `angular_damping` | `float` | 角阻尼 |
| `velocity` | `Vector2` | 线性速度，可读可写 |
| `angular_velocity` | `float` | 角速度（弧度/秒） |
| `category_bitmask` | `int` | 分类掩码（32 位） |
| `collision_bitmask` | `int` | 碰撞掩码 |
| `contact_test_bitmask` | `int` | 接触检测掩码 |

### 方法

- `apply_impulse(x, y)`：施加冲量

将 `node.physics_body = body` 时绑定到节点并同步到 SpriteKit。

**碰撞检测设置**：

```python
body_a.category_bitmask = 0x1
body_b.category_bitmask = 0x2
body_a.contact_test_bitmask = 0x2  # A 检测与 category=0x2 的碰撞
# 在 Scene 中实现 contact_began(contact) 接收回调
```

---

## `PhysicsWorld` 类

通过 **`scene.physics_world`** 访问。

- **`gravity`**：`Vector2`
  - 赋值时通过 `scene_set_gravity` 同步到原生
  - 默认 `(0, -9.8)`

---

## `Contact` 类

在 `Scene.contact_began(contact)` 中接收。

| 属性 | 类型 | 说明 |
|------|------|------|
| `node_a` / `node_b` | `Node` | 碰撞涉及的节点 |
| `body_a` / `body_b` | `Node` | 与 `node_a`/`node_b` 相同引用（兼容用） |
| `contact_point` | `Point` | 接触点 |
| `collision_impulse` | `float` | 冲量标量 |

---

## 关节（Joints）

| 关节 | 构造 | 说明 |
|------|------|------|
| `PinJoint` | `PinJoint(node_a, node_b, anchor)` | 铰链/销钉，`anchor` 为 `(x, y)` |
| `SpringJoint` | `SpringJoint(node_a, node_b, anchor_a, anchor_b, damping=0.5, frequency=1.0)` | 弹簧 |
| `RopeJoint` | `RopeJoint(node_a, node_b, anchor_a, anchor_b)` | 绳索（限制最大距离） |

均在构造时调用原生创建关节。

---

## `SceneView` 类

将场景嵌入 `ui` 界面：

```python
sv = SceneView()
sv.scene = MyScene()
v = sv.view   # ui.View，可 add_subview
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `paused` | `bool` | 暂停/恢复 |
| `frame_interval` | `int` | 帧间隔，≥1 |
| `anti_alias` | `bool` | 是否开启抗锯齿 |
| `shows_fps` | `bool` | 是否显示帧率 |

---

## Classic 绘图 API（`scene_drawing` / `scene.*`）

在 **`Scene.draw()`** 中调用。可直接 `import scene` 后使用 `scene.fill`、`scene.rect` 等（模块级延迟加载），或 `import scene_drawing as sd`。

| 函数 | 说明 |
|------|------|
| `background(r, g, b)` | 清屏背景色 |
| `fill(r, g, b, a)` / `no_fill()` | 设置/取消填充 |
| `stroke(r, g, b, a)` / `no_stroke()` | 设置/取消描边 |
| `stroke_weight(w)` | 线宽 |
| `tint(r, g, b, a)` / `no_tint()` | 图像与文字着色 |
| `rect(x, y, w, h, corner_radius=0)` | 矩形 |
| `ellipse(x, y, w, h)` | 椭圆（外接矩形） |
| `line(x1, y1, x2, y2)` | 线段 |
| `image(name, x, y, w, h, from_x, from_y, from_w, from_h)` | 绘制图像；后四个为可选子区域 |
| `text(txt, font_name, font_size, x, y, alignment)` | `alignment`：1–9 小键盘布局，**5=居中** |
| `translate(x, y)` / `rotate(deg)` / `scale(x, y)` | 变换；**`rotate` 为度** |
| `push_matrix()` / `pop_matrix()` | 矩阵栈 |
| `load_image_file(path)` | 返回供 `image()` 使用的名称 |
| `render_text(txt, font_name, font_size)` | 返回 `(name, Size)`，文字纹理 |

---

## 模块级函数

### `run()`

```python
run(
    scene,
    orientation=DEFAULT_ORIENTATION,
    frame_interval=1,
    anti_alias=False,
    show_fps=False,
    multi_touch=True,
    _mode='auto',  # 'main' 为主线程模式
)
```

### 其他函数

| 函数 | 返回值 | 说明 |
|------|--------|------|
| `get_screen_size()` | `Size` | 屏幕逻辑尺寸 |
| `get_screen_scale()` | `float` | 像素比例（Retina 2.0 / 3.0） |
| `gravity()` | `Vector3` | 设备重力向量 |
| `get_safe_area_insets()` | `EdgeInsets` | 安全区；API 不可用时返回全 0 |
| `play_effect(name, volume=1.0, pitch=1.0)` | — | 播放音效 |
| `get_image_path(name)` | `str` / `None` | 内置资源路径 |
| `get_controllers()` | `list` | 获取已连接的游戏控制器 |

---

## 颜色系统

场景模块中所有颜色参数（`color`、`fill_color`、`stroke_color`、`background_color` 等）在**设置**时支持以下格式：

| 格式 | 示例 |
|------|------|
| 颜色名字符串 | `'white'`、`'red'`、`'blue'`、`'green'`、`'orange'`、`'yellow'`、`'cyan'`、`'magenta'`、`'clear'` |
| 十六进制字符串 | `'#FF6B6B'`、`'#2c3e50'` |
| RGB/RGBA 元组 | `(0.2, 0.5, 0.8)` 或 `(0.2, 0.5, 0.8, 1.0)` |
| 灰度浮点 | `0.5`（等价于 `(0.5, 0.5, 0.5, 1.0)`） |

**读取**时，所有颜色属性**始终返回 `(r, g, b, a)` 4-tuple**。

---

## 常量

### 方向

| 常量 | 值 | 说明 |
|------|-----|------|
| `DEFAULT_ORIENTATION` | `0` | 自动方向 |
| `PORTRAIT` | `1` | 竖屏 |
| `LANDSCAPE` | `2` | 横屏 |

### 混合模式

| 常量 | 值 |
|------|-----|
| `BLEND_NORMAL` | `0` |
| `BLEND_ADD` | `1` |
| `BLEND_MULTIPLY` | `2` |

### 纹理过滤

| 常量 | 值 | 说明 |
|------|-----|------|
| `FILTERING_LINEAR` | `0` | 平滑过滤（默认） |
| `FILTERING_NEAREST` | `1` | 最近邻（像素风格） |

### 缓动曲线（共 16 种，作 `timing_mode` 传入 Action）

| 常量 | 值 |
|------|-----|
| `TIMING_LINEAR` | `0` |
| `TIMING_EASE_IN` / `TIMING_EASE_IN_2` | `1` / `2` |
| `TIMING_EASE_OUT` / `TIMING_EASE_OUT_2` | `3` / `4` |
| `TIMING_EASE_IN_OUT` | `5` |
| `TIMING_SINODIAL` | `6` |
| `TIMING_ELASTIC_IN` / `TIMING_ELASTIC_OUT` / `TIMING_ELASTIC_IN_OUT` | `7` / `8` / `9` |
| `TIMING_BOUNCE_IN` / `TIMING_BOUNCE_OUT` / `TIMING_BOUNCE_IN_OUT` | `10` / `11` / `12` |
| `TIMING_EASE_BACK_IN` / `TIMING_EASE_BACK_OUT` / `TIMING_EASE_BACK_IN_OUT` | `13` / `14` / `15` |

---

## 完整示例：弹跳球（Node + 物理 + 动画）

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
        bb.mass = 1.0
        bb.restitution = 0.85
        bb.friction = 0.4
        self.ball.physics_body = bb

        self.physics_world.gravity = (0, -18)

    def touch_began(self, touch):
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
6. **`update()` 签名**：`def update(self)` 和 `def update(self, dt)` 两种均可，推荐用 `self.dt`。
7. **颜色属性**：设置时支持多种格式，读取时始终返回 `(r,g,b,a)` 4-tuple。
8. **ShapeNode path**：推荐使用 `ui.Path.rect()` / `ui.Path.oval()` / `ui.Path.rounded_rect()`，也支持元组格式。
9. **`Action.sequence` / `Action.group`**：可传多个参数或一个列表，`Action.sequence(a1, a2)` 等效于 `Action.sequence([a1, a2])`。
10. **SpriteNode 无纹理时**必须指定 `size=(w,h)`，否则不可见。
11. **`run(..., _mode='main')`**：由 IDE 场景运行入口使用，保证回调在主线程执行。

---

*文档版本对应源码：`pyboot/scene.py`、`pyboot/scene_drawing.py`、`pythonide/SceneBridge.swift`。*
