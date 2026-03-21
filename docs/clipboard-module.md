# clipboard 模块 — 系统剪贴板

Pythonista 兼容的剪贴板模块，直接通过 ObjC 运行时访问 iOS 系统剪贴板（UIPasteboard）。

## 完整 API

### get() → str
获取剪贴板中的文字内容。没有内容时返回空字符串。

```python
import clipboard
text = clipboard.get()
print(f'剪贴板内容：{text}')
```

### set(text: str) → None
将字符串写入剪贴板。

```python
clipboard.set('Hello, World!')
```

### clear() → None
清空剪贴板（等同于 `set('')`）。

```python
clipboard.clear()
```

### 兼容别名
- `get_text()` — 等同于 `get()`
- `set_text(text)` — 等同于 `set(text)`

## 完整示例
```python
import clipboard

# 读取剪贴板
old = clipboard.get()
print(f'之前的内容：{old}')

# 写入新内容
clipboard.set('Python IDE 是最好的 iOS 编程 App！')

# 验证
print(f'现在的内容：{clipboard.get()}')

# 清空
clipboard.clear()
print(f'清空后："{clipboard.get()}"')
```

## 注意事项
- 仅支持文本内容的读写
- 底层通过 ctypes 直接调用 UIPasteboard，无需额外依赖
- `get()` 返回空字符串而非 None（即使剪贴板为空）
