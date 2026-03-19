<p align="center">
  <img src="docs/icon.png" width="120" alt="PythonIDE Logo" />
</p>

<h1 align="center">Python IDE</h1>
<h3 align="center">掌上的 Python & JavaScript 开发环境</h3>
<p align="center">
  <strong>让编程从电脑走到手机与平板</strong> · Write, Run, Debug on iOS
</p>

<p align="center">
  <a href="https://apps.apple.com/app/id6753987304">
    <img src="https://img.shields.io/badge/App%20Store-下载-black?style=for-the-badge&logo=apple" alt="Download on App Store" height="44" />
  </a>
  &nbsp;
  <a href="https://github.com/jinwandalaohu66/PythonIDE-iOS">
    <img src="https://img.shields.io/github/stars/jinwandalaohu66/PythonIDE-iOS?style=for-the-badge&logo=github" alt="GitHub Stars" height="44" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/iOS-16.2+-blue?style=flat-square" alt="iOS 16.2+" />
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python" alt="Python 3.13" />
  <img src="https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat-square&logo=javascript" alt="JavaScript" />
  <img src="https://img.shields.io/badge/Swift-5.9-FA7343?style=flat-square&logo=swift" alt="Swift" />
  <img src="https://img.shields.io/badge/C_Extensions-12+-brightgreen?style=flat-square" alt="C Extensions" />
</p>

---

## 🌟 为什么选择 Python IDE？

> 不是把电脑版塞进手机，而是**专为触摸屏和移动场景重新设计**的编程环境。

- **完全本地运行** — 代码执行不依赖任何服务器，无网络也能用
- **Python 3.13 完整标准库** — 不是阉割版，`asyncio`、`threading`、`socket` 全都有
- **12 个预装 C 扩展库** — NumPy、Pillow、cryptography 等，直接 `import`，速度是纯 Python 的 10–100 倍
- **150+ 预装纯 Python Wheel** — 常用库开箱即用，还能搜索 PyPI 在线安装更多
- **AI 助手开箱即用** — 无需配置，免费额度直接用；支持接入自己的 Key 无限使用
- **深度集成 iOS 系统能力** — 灵动岛、Siri 快捷指令、x-callback-url、相册/相机 API 一应俱全

---

## ✨ 核心功能 / Core Features

### 🐍 多语言运行

| 功能 | 描述 |
|------|------|
| **Python 3.13** | 完整标准库本地运行，支持 `async/await`、多线程、交互式 `input()`、ANSI 彩色输出 |
| **JavaScript** | JavaScriptCore 执行 `.js`，内置 `alert/confirm/prompt`、`fetch`、`localStorage`、剪贴板等 iOS 桥接 |
| **HTML 预览** | WKWebView 全屏渲染，支持相对路径引用本地资源、`alert/console` 桥接、`±` 按钮与双指捏合缩放 |

---

### ✏️ 专业代码编辑器

| 功能 | 描述 |
|------|------|
| **语法高亮** | Python、JavaScript、HTML、CSS、JSON、Markdown、LOG 等多语言 |
| **智能代码补全** | 基于 Jedi 引擎的 Python 智能提示，函数签名、文档字符串一应俱全 |
| **自动缩进** | 按语言规范自动缩进，Tab 宽度可调 |
| **行号栏** | 实时行号显示，支持大文件流畅滚动 |
| **字体调节** | 可调字体大小（8–30 号），双指捏合快速缩放 |
| **查找 & 替换** | 全文搜索、正则匹配、高亮跳转，支持全部替换 |
| **快捷输入栏** | 按语言（Py/JS/HTML/CSS/JSON/MD）定制符号与 Snippets，支持自定义按钮、拖拽排序 |
| **实时保存** | 自动保存 + 手动保存，永不丢失修改 |
| **显示空白符** | 可选显示空格与制表符，对齐问题一眼看出 |
| **分屏模式** | 编辑器与控制台同屏并排，竖屏上下 / 横屏左右分割（`.py` 文件） |
| **错误跳转** | 控制台报错含行号时，点击自动跳转编辑器对应行并高亮 |
| **运行历史** | 查看带时间戳的代码快照，一键重新运行历史版本 |

---

### 📺 控制台与输出

| 功能 | 描述 |
|------|------|
| **Rich 完整支持** | ANSI 彩色、粗体/斜体、进度条、表格、Markdown 渲染 |
| **多控制台** | 同时运行多个脚本，独立控制台，随时切换查看 |
| **交互式输入** | 完整支持 `input()` 实时键盘输入，包括密码遮蔽 |
| **输入历史** | 键盘上方快捷栏支持上下翻历史命令，↑↓ 箭头快速复用 |
| **配色主题** | 内置多套配色方案，黑色/白色/护眼绿等，可自由切换 |
| **字体与时间戳** | 可调字体大小，每行输出前可选显示时间戳 |
| **自定义背景** | 控制台背景支持纯色或自定义图片 |
| **运行历史** | 查看历史运行记录，快速回溯之前的输出 |

---

### 🤖 AI 助手

AI 助手**深度融入编辑器工作流**，不是简单的聊天窗口，而是真正的代码协作伙伴。

#### 三种使用方式，随心选择

| 方式 | 说明 |
|------|------|
| **平台内置额度** | 注册即赠免费次数，无需任何配置，打开即用 |
| **购买调用包** | 应用内购买 100 / 200 / 500 次额度包，立即到账，与免费次数叠加 |
| **自带 Key（BYOK）** | 一次性永久解锁，填入自己的 API 地址 + Key，完全不受额度限制 |

内置一键预设：**DeepSeek**、**OpenAI**、**OpenRouter**，以及任意兼容 OpenAI 格式的服务。支持保存多套预设并随时切换。

#### 行内修改模式

- 点击编辑器顶部 ✨ 或键盘上方 ✨ 按钮，用自然语言描述需求
- AI **直接修改当前文件**，以 **Diff 差异对比** 展示每一处改动（绿色新增 / 红色删除）
- 支持**逐条采纳 / 拒绝**，或一键全部接受 / 放弃
- 按文件类型自动切换角色：Python 专家 / JS 专家 / HTML 开发者 / Markdown 编辑

#### AI 聊天模式

- 底部滑出对话面板，支持多轮连续对话
- 当前编辑文件内容**自动作为上下文**传入，无需手动粘贴代码
- AI 回复中的代码块**一键应用到编辑器**
- 支持代码解释：选中任意代码段，弹出 AI 解释面板

#### 智能联动

- **报错一键修复**：脚本出错后，控制台底部自动弹出错误卡片，点击 ✨ 将报错上下文直接发给 AI，一键生成修复方案
- **智能装库**：AI 发现代码中缺少第三方库时，自动弹出安装提示，确认后**自动下载安装**，无需手动操作
- **iOS 感知 System Prompt**：AI 内置 iOS 沙盒环境知识，不会给出在手机上无法运行的建议

---

### ⚡ 内置 C 扩展库

> 由原生代码编译，运行速度比纯 Python 实现快 **10–100 倍**，直接 `import` 即用，无需安装。

| 分类 | 库 | 说明 |
|------|-----|------|
| 科学计算 | **NumPy 1.26** | 数组、矩阵、线性代数、FFT、随机数 |
| 图像处理 | **Pillow 12** | JPEG/PNG/WebP/AVIF 读写，滤镜、裁剪、合成 |
| 高性能 JSON | **ujson** | 比标准 `json` 快 10 倍，接口完全兼容 |
| 高性能序列化 | **msgpack** | 二进制序列化，体积更小、速度更快 |
| 高级正则 | **regex** | Unicode 分类、模糊匹配、重叠匹配，比 `re` 更强大 |
| 工业级加密 | **cryptography** | AES、RSA、ECDSA、Fernet 完整套件 |
| 密码哈希 | **bcrypt** | 密码安全存储的行业标准 |
| 密码哈希 | **argon2-cffi** | 比 bcrypt 更安全的新一代标准 |
| C 接口层 | **cffi** | Python 与 C 代码互调的基础桥接库 |
| 异步网络 | **aiohttp** | C 加速的高性能异步 HTTP 客户端 |
| 数据结构 | **bitarray / lru-dict** | 高效位数组、C 实现的 LRU 缓存 |
| 开发工具 | **coverage / kiwisolver** | 代码覆盖率统计、约束求解器 |

---

### 📚 第三方库与库管理

150+ 纯 Python Wheel 预装，常用场景开箱即用，还能实时搜索 PyPI 安装更多。

| 分类 | 常用库 |
|------|--------|
| **网络请求** | `requests`、`httpx`、`aiohttp`、`urllib3`、`certifi` |
| **网页解析** | `beautifulsoup4`、`html5lib` |
| **数据格式** | `pyyaml`、`toml`、`jsonschema`、`pydantic`、`marshmallow` |
| **日期时间** | `python-dateutil`、`arrow`、`pendulum`、`pytz` |
| **安全加密** | `cryptography`、`bcrypt`、`argon2-cffi`、`pyjwt`、`passlib` |
| **工具与 CLI** | `click`、`rich`、`tqdm`、`loguru`、`colorama` |
| **文本处理** | `chardet`、`email-validator`、`phonenumbers`、`python-slugify` |
| **机器人** | `python-telegram-bot`、`telethon` |
| **Web 框架** | `flask`、`starlette`（轻量级） |

**库管理界面功能：**
- 🔍 搜索 PyPI 实时安装，显示**下载进度百分比**
- 📦 按分类浏览 40+ 热门库，含图标与颜色区分
- ✅ 已安装列表展示版本号与来源（预装 / 用户安装）
- 🗑 左滑一键卸载（含确认对话框，防误操作）
- 📋 长按复制 `import` 语句
- 📁 支持 `.whl` 文件直接导入安装

---

### 📂 文件管理

| 功能 | 描述 |
|------|------|
| **多层级文件夹** | 无限层级，面包屑导航，点击路径随时跳转 |
| **全类型文件** | 创建 `.py`、`.js`、`.html`、`.css`、`.md`、`.json`、`.txt` 等 |
| **文件着色** | 给文件和文件夹设置 12 种颜色标记，分类一目了然 |
| **回收站** | 删除后 7 天内可恢复，倒计时提示，批量清空 |
| **置顶** | 文件 / 文件夹置顶固定，左滑快速操作 |
| **全局搜索** | 按文件名搜索，高亮匹配，支持历史记录 |
| **批量操作** | 多选、批量删除、批量分享、批量移动 |
| **导入** | 从系统「文件」App 导入任意文件 |
| **排序** | 拖拽手动排序，或按更新时间自动排序 |

---

### 📄 多格式支持

| 类型 | 格式 |
|------|------|
| **可运行** | `.py`（Python 3.13）、`.js`（JavaScript） |
| **可预览** | `.html`（全屏网页）、`.md`（Markdown 渲染）、`.csv`（表格）、`.css`（套用示例）、图片、视频、PDF |
| **可编辑** | `.json`、`.txt`、`.log`、`.php` 以及其他纯文本格式 |

---

### 🛠️ 开发者工具箱（10 大工具）

| 工具 | 功能 |
|------|------|
| **编解码** | URL 编解码、Unicode 互转、MD5、Base64 |
| **JSON** | 格式化、压缩、校验，语法错误定位 |
| **API 调试** | HTTP 请求测试，自定义 Method / Header / Body，查看响应码与正文 |
| **二维码** | 生成 / 识别（相册图片识别）、Data URL 转换 |
| **图片 URL** | 在线图片 URL 转 Data URL、图片转 Base64 |
| **HTML 截图** | HTML 转图片、网页抓图、Data URL 导出 |
| **时间戳** | 毫秒 / 秒互转、多时区日期格式化 |
| **进制转换** | 二 / 八 / 十 / 十六进制互转 |
| **正则表达式** | 匹配测试、替换预览、分组捕获可视化 |
| **直链下载** | 自定义 UA / Referer / Cookie / Token，TLS 忽略，实时进度条，下载后直接导出 |

工具列表支持**关键词搜索**、**拖拽排序**，可随时恢复默认顺序。

---

### 📱 iOS 原生深度集成

#### 🏝 灵动岛 & 锁屏 Live Activity

脚本运行期间，灵动岛实时显示状态，无需解锁手机即可掌握运行进度：

- **运行中** — 动态波形动画 + 实时计时
- **等待输入** — 提示 `input()` 的提示文字
- **完成** — 显示完成信息，10 秒后自动消失
- **失败** — 显示错误摘要，点击跳回 App 查看详情

#### ⌘ Siri 快捷指令（App Intents）

深度集成 iOS 快捷指令，**无需打开 App** 即可执行 Python 脚本：

| 操作 | 说明 |
|------|------|
| **运行 Python 代码** | 直接执行代码片段，支持等待完成并返回输出结果 |
| **运行 Python 脚本** | 从工作区选择 `.py` 文件执行，支持传入命令行参数 |
| **在应用中运行脚本** | 强制打开 App 在控制台中运行，适合有 `input()` 的交互式脚本 |
| **获取脚本输出** | 配合「不等待」模式，异步获取上一次运行的输出结果 |
| **创建 Python 脚本** | 在工作区创建新文件，可链式传给「运行脚本」使用 |

- 支持 **Siri 语音触发**，说「在 Python IDE 中运行代码」即可
- 支持在「自动化」中设置定时触发，实现脚本计划任务
- 脚本文件支持 **Spotlight 全局搜索**（iOS 18+）

#### 🔗 URL Scheme & x-callback-url

支持从其他 App、Widget、通知等任意入口唤起并执行脚本：

```
pythonide://run-code?code=print("hello")
pythonide://run-script?name=main.py
pythonide://download?url=https://example.com/file.zip
pythonide://x-callback/?code=xxx&x-success=callback://&x-error=callback://
```

完整支持 [x-callback-url](http://x-callback-url.com/) 规范（`x-success`、`x-error`、`x-cancel`），可与 Drafts、Toolbox for Writer 等 App 联动。

#### 📷 photos & dialogs 模块

Python 直接调用 iOS 系统能力，与 Pythonista 完全兼容：

```python
import photos
import dialogs

# 从相册选图，配合 Pillow 处理
asset = photos.pick_asset()
img = asset.get_image()

# 原生弹窗交互
name = dialogs.input_alert("请输入名字")
choice = dialogs.list_dialog("选择颜色", ["红", "绿", "蓝"])
dialogs.hud_alert("操作完成！")
```

还支持 `clipboard`（读写系统剪贴板）和 `console`（彩色输出、清屏、粗体）模块。

#### 📐 ui 模块 — 原生界面

Pythonista 兼容的 UI 模块，用 Python 创建原生 iOS 界面（View、Button、Label、TextField、ScrollView、TableView、WebView 等），支持 `present()` 全屏/半屏展示、自绘、load_view 等。

- **[UI 模块完整文档（中文）](docs/ui-module-zh.md)** · [Full docs (English)](docs/ui-module-en.md)

#### 🎮 scene 模块 — 2D 游戏引擎

Pythonista 兼容的 Scene 模块，用 Python 开发 2D 游戏和动画。底层基于 SpriteKit，提供**两种开发模式**：经典逐帧绘制（`draw()`）和现代节点树（Node + Action）。

##### 节点体系

| 节点 | 说明 |
|------|------|
| **`Node`** | 基础节点，支持 `position`、`rotation`、`alpha`、`z_position`、`physics_body` |
| **`SpriteNode`** | 精灵节点，加载图片纹理，支持 `color`、`size`、`anchor_point` |
| **`LabelNode`** | 文字节点，支持 `font`、`color`、`alignment` |
| **`ShapeNode`** | 形状节点，支持矩形（可圆角）、椭圆，可设 `fill_color`、`stroke_color` |
| **`EmitterNode`** | 粒子发射器节点 |

##### Action 动画系统（14 种动作）

| 动作 | 说明 |
|------|------|
| `move_to` / `move_by` | 移动到绝对位置 / 相对偏移 |
| `rotate_to` / `rotate_by` | 旋转到角度 / 旋转偏移量 |
| `scale_to` / `scale_by` | 缩放到倍数 / 缩放偏移 |
| `fade_to` / `fade_by` | 淡入淡出到透明度 / 透明度偏移 |
| `sequence` | 按顺序执行一组动作 |
| `group` | 同时并行执行一组动作 |
| `repeat` / `repeat_forever` | 重复执行 N 次 / 无限循环 |
| `wait` | 等待指定秒数 |
| `call` | 执行回调函数 |
| `remove` | 从父节点移除 |

所有动作支持 **16 种缓动曲线**：`TIMING_LINEAR`、`TIMING_EASE_IN/OUT`、`TIMING_ELASTIC_IN/OUT`、`TIMING_BOUNCE_IN/OUT`、`TIMING_EASE_BACK_IN/OUT` 等。

##### 物理引擎

| 功能 | 说明 |
|------|------|
| **`PhysicsWorld`** | 场景物理世界，可设置 `gravity` 全局重力 |
| **`PhysicsBody`** | 物理体，支持 `rectangle(w,h)` 和 `circle(r)` 两种形状 |
| **碰撞属性** | `restitution`（弹性）、`friction`（摩擦）、`linear_damping`（阻尼）、`velocity`（速度） |
| **碰撞检测** | `category_bitmask`、`collision_bitmask`、`contact_test_bitmask` 位掩码 |
| **`Contact`** | 碰撞回调，包含 `node_a`、`node_b`、`contact_point`、`collision_impulse` |
| **力与冲量** | `apply_impulse(x, y)` 施加冲量 |
| **关节** | `PinJoint`（铰链）、`SpringJoint`（弹簧）、`RopeJoint`（绳索） |

##### 经典绘图 API（scene_drawing）

在 `Scene.draw()` 中使用的逐帧绘制函数，适合快速原型和简单动画：

| 函数 | 说明 |
|------|------|
| `background(r,g,b)` | 填充背景色 |
| `fill(r,g,b,a)` / `no_fill()` | 设置 / 取消填充色 |
| `stroke(r,g,b,a)` / `no_stroke()` | 设置 / 取消描边色 |
| `stroke_weight(w)` | 设置描边宽度 |
| `rect(x,y,w,h)` | 绘制矩形（支持圆角） |
| `ellipse(x,y,w,h)` | 绘制椭圆 |
| `line(x1,y1,x2,y2)` | 绘制线段 |
| `image(name,x,y,w,h)` | 绘制图片 |
| `text(txt,font,size,x,y)` | 绘制文字 |
| `tint(r,g,b,a)` / `no_tint()` | 设置 / 取消图片着色 |
| `translate` / `rotate` / `scale` | 矩阵变换 |
| `push_matrix` / `pop_matrix` | 保存 / 恢复变换状态 |
| `load_image_file(path)` | 从文件加载图片 |
| `render_text(txt,font,size)` | 将文字渲染为纹理 |

##### 其他功能

| 功能 | 说明 |
|------|------|
| `Scene.touch_began/moved/ended` | 多点触摸事件回调 |
| `Scene.present_modal_scene` | 模态场景（菜单、暂停画面等） |
| `Scene.did_change_size` | 屏幕旋转回调 |
| `run(scene, orientation, show_fps)` | 启动场景，支持竖屏/横屏/自动 |
| `get_screen_size()` / `get_screen_scale()` | 屏幕尺寸与缩放因子 |
| `gravity()` | 读取设备重力传感器（陀螺仪） |
| `play_effect(name)` | 播放音效 |
| `Texture(name)` | 加载纹理资源 |
| `Shader(source)` | 自定义着色器 |
| `SceneView` | 将场景嵌入 `ui.View` 中 |

##### 代码示例

```python
from scene import *

class MyGame(Scene):
    def setup(self):
        self.background_color = (0.05, 0.05, 0.15)
        self.player = SpriteNode('plc:Alien_Green',
                                  position=self.size / 2,
                                  parent=self)

    def touch_began(self, touch):
        self.player.run_action(
            Action.move_to(*touch.location, 0.3, TIMING_EASE_OUT)
        )

run(MyGame())
```

应用内置 **16 款游戏示例**，包括贪吃蛇、Flappy Bird、打砖块、2048、水果忍者、俄罗斯方块、塔防、节奏大师、太空射击、打地鼠、重力迷宫等，可直接运行学习。

#### 📲 widget 模块 — iOS 桌面小组件

用 Python 创建 **iOS 桌面小组件**，脚本运行后自动渲染到主屏幕。支持声明式布局 DSL 和快捷模板两种模式。

##### 支持的组件（14 种）

| 组件 | 方法 | 说明 |
|------|------|------|
| **文字** | `w.text(content, size, weight, color, align, max_lines, design)` | 支持字号、字重、颜色、对齐、行数限制、字体设计（`rounded` / `monospaced` / `serif`） |
| **图标** | `w.icon(name, size, color, weight)` | SF Symbol 图标，支持 6000+ 系统图标 |
| **Emoji** | `w.emoji(content, size)` | Emoji 表情，支持自定义大小 |
| **间距** | `w.spacer(length)` | 弹性间距或固定间距 |
| **分割线** | `w.divider(color, opacity)` | 水平分割线 |
| **进度条** | `w.progress(value, total, color, height, track_color)` | 线性进度条，支持自定义颜色和轨道色 |
| **仪表盘** | `w.gauge(value, total, label, size, color, track_color, line_width)` | 圆形仪表盘，支持中心文字 |
| **实时计时** | `w.timer(target, style, size, weight, color)` | WidgetKit 原生倒计时，无需刷新；支持 `timer` / `relative` / `date` / `time` / `offset` 五种样式 |
| **图片** | `w.image(name, width, height, corner_radius, content_mode)` | 显示通过 `save_image()` 缓存的图片，支持 `fit` / `fill` |
| **水平布局** | `w.hstack(spacing, align, background, corner_radius, url)` | `with` 语法，支持嵌套 |
| **垂直布局** | `w.vstack(...)` | 同上 |
| **叠加布局** | `w.zstack(...)` | 多层叠加 |
| **卡片** | `w.card(background, corner_radius, padding, border_color, border_width, url)` | 带圆角、背景、边框的容器 |
| **渲染输出** | `w.render(url)` | 输出最终布局，可设置点击跳转 URL |

##### 小组件尺寸

| 常量 | 说明 |
|------|------|
| `SMALL` | 主屏幕小组件（2×2） |
| `MEDIUM` | 主屏幕中组件（4×2） |
| `LARGE` | 主屏幕大组件（4×4） |
| `CIRCULAR` | 锁屏圆形小组件 |
| `RECTANGULAR` | 锁屏矩形小组件 |
| `INLINE` | 锁屏行内小组件 |

通过 `widget.family` 获取当前尺寸，按需适配不同布局。

##### 特色功能

- **深色模式适配**：颜色支持 `(light_color, dark_color)` 元组，自动跟随系统
- **渐变背景**：`{"gradient": ["#FF6B6B", "#4ECDC4"], "direction": "diagonal"}`，支持 4 个方向
- **图片缓存**：`save_image(source, name)` 支持文件路径和 bytes，自动压缩（限 512KB）
- **深链跳转**：容器和 `render()` 支持 `url` 参数，点击小组件跳转到指定页面
- **快捷模板**：`widget.show(title, value, progress, rows)` 一行代码生成常用布局

##### 代码示例

```python
from widget import Widget, family, SMALL, MEDIUM

w = Widget(background=("#1a1a2e", "#0f0f1a"))

with w.vstack(spacing=8, padding=12):
    w.text("🔥 今日目标", size=13, color="#aaa")
    with w.hstack(spacing=12):
        w.gauge(0.75, label="75%", size=50,
                color="#FF6B6B", track_color="#333")
        with w.vstack(spacing=4, align="leading"):
            w.text("步数 8,432", size=14, weight="semibold", color="white")
            w.text("目标 10,000", size=12, color="#888")
    w.divider(color="#333")
    w.progress(0.6, color="#4ECDC4", height=6, track_color="#222")

w.render()
```

应用内置 **8 款小组件示例**，包括健身环、习惯追踪、学习计时、货币汇率、音乐播放器等，可直接运行体验。

---

### 🔒 隐私与个性化

| 功能 | 描述 |
|------|------|
| **Face ID / Touch ID** | 应用锁定保护代码隐私，可设置锁定延迟（立即 / 1 / 2 / 5 / 30 分钟） |
| **5 套 App 图标** | 默认、深色、渐变、极简，以及捐赠专属图标，随时切换 |
| **外观模式** | 跟随系统 / 强制浅色 / 强制深色 |
| **自定义背景** | 编辑器与控制台背景支持纯色或自定义图片 |
| **触觉反馈** | 操作成功 / 失败 / 提示三级触感反馈 |
| **后台运行** | 长任务后台继续执行，音频保活防系统杀进程 |
| **启动动画** | Lottie 动态启动页，冷启动更流畅 |

---

## 📱 截图 / Screenshots

| 首页 | 编辑器 |
|:---:|:---:|
| <img src="docs/首页.png" width="280" /> | <img src="docs/编辑页面.png" width="280" /> |
| 文件管理、颜色标记、置顶、搜索、批量操作、回收站 | 语法高亮、智能补全、快捷输入栏、查找替换、分屏 |

| 控制台 | AI 助手 |
|:---:|:---:|
| <img src="docs/控制台页面.png" width="280" /> | <img src="docs/AI分析.png" width="280" /> |
| Rich 彩色输出、进度条、多控制台切换、交互式 input() | Diff 差异对比、逐条采纳/拒绝、一键修复报错、智能装库 |

| 库管理 | 工具箱 |
|:---:|:---:|
| <img src="docs/库管理.png" width="280" /> | <img src="docs/工具箱.png" width="280" /> |
| PyPI 搜索安装、热门库分类、进度条、版本管理、一键卸载 | 编解码、JSON、API 调试、二维码、时间戳、正则、直链下载 |

| HTML 预览 | Markdown 渲染 |
|:---:|:---:|
| <img src="docs/html预览.png" width="280" /> | <img src="docs/md文件.png" width="280" /> |
| 全屏网页渲染、双指缩放、alert/console 桥接 | 实时渲染，支持标题、列表、代码块、表格、任务列表 |

| 新建文件 | 设置 |
|:---:|:---:|
| <img src="docs/新建文件.png" width="280" /> | <img src="docs/设置.png" width="280" /> |
| 支持 py/js/html/css/md/json 等多种格式，可设置颜色标记 | 外观、编辑器字体、AI 配置、应用锁定、快捷指令帮助 |

---

## 📥 安装 / Install

<p align="center">
  <a href="https://apps.apple.com/app/id6753987304">
    <img src="https://img.shields.io/badge/App%20Store-下载-black?style=for-the-badge&logo=apple" alt="Download on App Store" height="44" />
  </a>
</p>

| 要求 | 说明 |
|------|------|
| **系统** | iOS 16.2 或更高版本 |
| **设备** | iPhone / iPad 均支持 |
| **价格** | 免费下载，AI 功能提供免费额度 |

---

## 💬 社区与反馈 / Community & Feedback

| 渠道 | 链接 |
|------|------|
| **✈️ Telegram 频道** | [iOS 端 Py 编程 IDE](https://t.me/pythonzwb) — 获取更新动态，与其他用户交流 |
| **💡 功能建议** | [GitHub Discussions](https://github.com/jinwandalaohu66/PythonIDE-Landing/discussions) |
| **🐛 问题反馈** | [GitHub Issues](https://github.com/jinwandalaohu66/PythonIDE-Landing/issues) |
| **📧 邮件** | 应用内「设置 → 反馈 → 发送邮件」 |
| **⭐ 支持** | [App Store 评分](https://apps.apple.com/app/id6753987304) · [GitHub Star](https://github.com/jinwandalaohu66/PythonIDE-Landing) |

---

## ☕ 支持开发 / Support

如果 PythonIDE 对你有帮助，欢迎通过以下方式支持后续开发：

- **App Store 评分** — 五星好评是最大的鼓励
- **GitHub Star** — 让更多开发者发现这个项目
- **应用内捐赠** — 支持 🍭 棒棒糖 / 🍗 鸡腿 / 🧋 奶茶 三个档位，捐赠后可解锁专属 App 图标

<p align="center">
  <img src="docs/赞赏码.jpg" width="200" alt="赞赏码" /><br/>
  <em>扫码赞赏 · Thank you for your support ♥</em>
</p>

---

## 🙏 致谢 / Thanks

感谢所有使用、反馈和支持 PythonIDE 的开发者们。
每一条反馈都推动着这个项目变得更好。

<p align="center">
  <strong>PythonIDE</strong> —— 本地、纯粹、实用的移动端编程环境
</p>

---

<p align="center">
  <sub>
    <strong>Topics</strong> · ios · python · javascript · ide · numpy · pillow · cryptography · app-intents · siri · shortcuts · live-activity · mobile-development · swift · scripting · developer-tools · game-engine · widgets
  </sub>
</p>
