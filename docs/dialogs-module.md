# dialogs 模块 — 原生弹窗与表单

Pythonista 兼容的对话框模块，提供原生 iOS 弹窗交互。所有函数都是**阻塞式**的：调用后当前协程/线程会等待用户完成操作，再返回结果；若用户取消（例如点击「取消」或关闭弹窗），则抛出 `KeyboardInterrupt`，与 Pythonista 行为一致。

**导入方式：**

```python
import dialogs
```

---

## 完整 API

### `alert(title, message='', *button_titles, hide_cancel_button=False)` → `int`

弹出确认类对话框，可配置多个操作按钮。

| 参数 | 类型 | 说明 |
|------|------|------|
| `title` | `str` | 对话框标题 |
| `message` | `str` | 正文说明，默认为空字符串 |
| `*button_titles` | `str` | 可变参数，各按钮的标题；未传入时等价于 `('OK',)` |
| `hide_cancel_button` | `bool` | 为 `True` 时，所有按钮均为普通样式（不强调取消语义）；为 `False` 时按平台惯例区分主按钮与取消等 |

**返回值：** 用户所点按钮的索引，**从 1 开始**（与 Pythonista 兼容）。例如第一个按钮为 `1`，第二个为 `2`。

**取消：** 用户取消或关闭对话框时抛出 `KeyboardInterrupt`。

**示例：**

```python
if dialogs.alert('确认删除？', '此操作不可撤销', '删除', '取消') == 1:
    do_delete()
```

---

### `input_alert(title, message='', placeholder='', secure=False, default_text='')` → `str`

弹出单行文本输入对话框。

| 参数 | 类型 | 说明 |
|------|------|------|
| `title` | `str` | 标题 |
| `message` | `str` | 辅助说明 |
| `placeholder` | `str` | 输入框占位提示 |
| `secure` | `bool` | `True` 时使用密码样式输入（字符遮蔽） |
| `default_text` | `str` | 输入框初始内容 |

**返回值：** 用户确认后输入的字符串。

**取消：** 抛出 `KeyboardInterrupt`。

**示例：**

```python
name = dialogs.input_alert('请输入名字', placeholder='张三')
```

---

### `list_dialog(title, items, multiple=False)` → `str | list[str]`

从字符串列表中让用户选择一项或多项。

| 参数 | 类型 | 说明 |
|------|------|------|
| `title` | `str` | 对话框标题 |
| `items` | `list` | 由字符串组成的选项列表 |
| `multiple` | `bool` | `False`：单选；`True`：多选 |

**返回值：**

- `multiple=False`：返回用户选中的**单个**字符串（`str`）。
- `multiple=True`：返回用户选中的字符串**列表**（`list[str]`）。

**取消：** 抛出 `KeyboardInterrupt`。

**示例：**

```python
color = dialogs.list_dialog('选择颜色', ['红', '绿', '蓝'])
```

---

### `form_dialog(title, fields)` → `dict`

一次性展示多个字段的表单对话框，适合登录、设置等场景。

**`fields`：** 由字典组成的列表，每个字典描述一个字段：

```python
{
    'type': 'text' | 'password' | 'number' | 'email' | 'url' | 'switch',
    'key': 'field_key',        # 出现在返回 dict 中的键名
    'title': '字段标签',       # 界面上的标签文案
    'value': '默认值',         # 可选，字段初始值
    'placeholder': '占位符',   # 可选，适用于文本类输入
}
```

**字段类型说明：**

| `type` | 含义 | 返回值类型 |
|--------|------|------------|
| `text` | 普通文本 | `str` |
| `password` | 密码（遮蔽） | `str` |
| `number` | 数字键盘 / 数值输入 | `str`（内容为数字字符串） |
| `email` | 邮箱键盘 | `str` |
| `url` | URL 键盘 | `str` |
| `switch` | 开关 | `bool` |

**返回值：** `{key: value}` 字典，键为各字段的 `'key'`，值为上述类型。`switch` 为 `bool`，其余文本类字段为 `str`。

**取消：** 抛出 `KeyboardInterrupt`。

**示例：**

```python
result = dialogs.form_dialog('登录', [
    {'type': 'text', 'key': 'user', 'title': '用户名'},
    {'type': 'password', 'key': 'pwd', 'title': '密码'},
    {'type': 'switch', 'key': 'remember', 'title': '记住密码', 'value': True},
])
```

---

### `date_dialog(title='选择日期', mode='date')` → `str`

弹出系统日期/时间选择器。

| 参数 | 类型 | 说明 |
|------|------|------|
| `title` | `str` | 对话框标题，默认 `'选择日期'` |
| `mode` | `str` | `'date'`：仅日期；`'time'`：仅时间；`'datetime'`：日期与时间 |

**返回值：** ISO 8601 格式字符串，例如 `'2025-03-01T12:00:00+08:00'`（具体时区与格式以实现为准，均为 ISO 8601 语义）。

**取消：** 抛出 `KeyboardInterrupt`。

**示例：**

```python
dt = dialogs.date_dialog('选择生日', mode='date')
```

---

### `hud_alert(message, duration=1.0)` → `None`

在界面上显示短暂的 HUD（轻提示），在指定秒数后自动消失，**无需用户点击确认**；实现上仍会经 RPC 与宿主同步，调用在提示展示流程结束后返回。

| 参数 | 类型 | 说明 |
|------|------|------|
| `message` | `str` | 提示文案 |
| `duration` | `float` | 显示时长（秒），默认 `1.0` |

**返回值：** `None`。

**示例：**

```python
dialogs.hud_alert('已保存！', duration=2.0)
```

---

## `editor` 兼容 stub

`dialogs.editor` 提供与 Pythonista **`editor`** 模块名称对齐的占位接口，便于脚本在不修改导入路径的情况下运行；**不**连接真实编辑器状态。

**可用方法（均为 stub，与 Pythonista 行为不等价）：**

| 方法 | 说明 |
|------|------|
| `get_path()` | 返回空字符串 `""` |
| `get_text()` | 返回空字符串 `""` |
| `replace_text(start, end, replacement)` | 空操作（`None`） |
| `get_selection()` | 返回 `(0, 0)` |
| `set_selection(start, end=-1)` | 空操作 |
| `make_new_file(name='', text='')` | 空操作 |

以上方法仅为**兼容性**保留，不应依赖其修改工程内文件或选区。

---

## 完整示例

下面示例依次演示输入框、列表、表单、日期与 HUD；统一用 `try` / `except KeyboardInterrupt` 处理用户取消：

```python
import dialogs

try:
    name = dialogs.input_alert('欢迎', placeholder='你的名字')
    color = dialogs.list_dialog('选择主题色', ['蓝色', '绿色', '红色', '紫色'])
    info = dialogs.form_dialog('个人信息', [
        {'type': 'text', 'key': 'email', 'title': '邮箱', 'placeholder': 'xxx@example.com'},
        {'type': 'number', 'key': 'age', 'title': '年龄'},
        {'type': 'switch', 'key': 'agree', 'title': '同意协议', 'value': False},
    ])
    birthday = dialogs.date_dialog('选择生日')
    dialogs.hud_alert(f'欢迎 {name}！')
except KeyboardInterrupt:
    print('用户取消了操作')
```

---

## 注意事项

1. **阻塞：** 除 `hud_alert` 这类短时提示外，主要弹窗函数在显示期间会阻塞调用方，直到用户完成或取消。
2. **取消与 `KeyboardInterrupt`：** 用户点击「取消」、系统取消或关闭弹窗时，应抛出 `KeyboardInterrupt`；脚本中请使用 `try` / `except` 做友好处理。
3. **`alert` 索引：** 返回值为 **1-based** 按钮索引，与 Pythonista 一致，勿与 0-based 数组下标混淆。
4. **`form_dialog` 类型：** `switch` 字段在结果字典中为 **`bool`**，其余声明的文本/数字类字段为 **`str`**（数字也以字符串形式给出时，请按需 `int()` / `float()` 转换）。

---

*本文档描述 `dialogs` 模块的公开 API 与约定行为；若与具体实现有差异，以实现代码为准。*
