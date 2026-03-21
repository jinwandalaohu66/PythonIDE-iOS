# console 模块 — 控制台样式控制

Pythonista 兼容的控制台模块，通过 ANSI 转义序列控制输出颜色和样式。

## 完整 API

### clear() → None
清除控制台所有输出。

```python
import console
console.clear()
```

### set_color(r=-1, g=-1, b=-1) → None
设置后续 `print()` 输出的前景色。参数为 0.0~1.0 的 RGB 值。不传参数或 r<0 时重置为默认颜色。

```python
console.set_color(1, 0, 0)    # 红色
print('这是红色文字')
console.set_color(0, 1, 0)    # 绿色
print('这是绿色文字')
console.set_color()            # 重置
print('这是默认颜色')
```

### set_bold(flag=True) → None
开启或关闭粗体输出。

```python
console.set_bold(True)
print('粗体文字')
console.set_bold(False)
```

### set_font(name='', size=0) → None
设置控制台字体（兼容接口，本 App 固定等宽字体，无实际效果）。

### reset_style() → None
重置所有样式（颜色、粗体），等同于 `set_color()` + `set_bold(False)`。

### hud_alert(message, duration=1.0) → None
显示短暂的 HUD 提示（委托给 dialogs.hud_alert 实现）。

```python
console.hud_alert('操作成功！')
```

### alert(title, message='', *button_titles, hide_cancel_button=False)
弹出确认框（委托给 dialogs.alert，兼容接口）。

### input_alert(title, message='', input_text='', ok_button_title='OK', hide_cancel_button=False) → str
弹出输入框（委托给 dialogs.input_alert，兼容接口）。

### print_raw(text) → None
直接输出文本（不带换行），等同于 `sys.stdout.write(text)`。

## 完整示例
```python
import console

console.clear()

# 彩色输出
console.set_color(0.2, 0.6, 1.0)
print('=== 天气预报 ===')

console.set_bold(True)
console.set_color(1, 0.3, 0)
print('🌡️ 温度：28°C')

console.set_color(0, 0.8, 0.4)
print('💧 湿度：65%')

console.reset_style()
print('数据更新于 2025-01-01')

console.hud_alert('数据已刷新')
```

## 注意事项
- set_color 使用 0.0~1.0 的 RGB 浮点值（与 Pythonista 一致）
- 颜色通过 ANSI 256 色转义序列实现
- App 控制台支持完整 ANSI 彩色（16/256/RGB）
- set_font 为兼容接口，无实际效果
- hud_alert 和 alert 内部委托给 dialogs 模块
