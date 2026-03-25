# Python IDE — UI Module Complete Documentation

> Pythonista-compatible native iOS UI module. Create UIKit interfaces with Python on iPhone and iPad without installing any additional libraries.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Quick Start](#3-quick-start)
4. [View Basics](#4-view-basics)
5. [present and Display](#5-present-and-display)
6. [Button](#6-button)
7. [Label](#7-label)
8. [TextField](#8-textfield)
9. [TextView](#9-textview)
10. [ImageView](#10-imageview)
11. [Switch](#11-switch)
12. [Slider](#12-slider)
13. [SegmentedControl](#13-segmentedcontrol)
14. [DatePicker](#14-datepicker)
15. [ScrollView](#15-scrollview)
16. [TableView](#16-tableview)
17. [WebView](#17-webview)
18. [ActivityIndicator](#18-activityindicator)
18b. [ProgressView](#18b-progressview)
18c. [Stepper](#18c-stepper)
19. [NavigationView](#19-navigationview)
20. [Custom View and Drawing](#20-custom-view-and-drawing) (incl. Path, Image, ImageContext updates)
21. [load_view and load_view_str](#21-load_view-and-load_view_str)
22. [animate and Utility Functions](#22-animate-and-utility-functions)
23. [Constants and Enums](#23-constants-and-enums)
24. [Troubleshooting](#24-troubleshooting)

---

## 1. Overview

The built-in `ui` module in Python IDE provides native iOS UI capabilities that are highly compatible with [Pythonista](https://omz-software.com/pythonista/). You can create views, buttons, labels, text fields, images, lists, and more in Python scripts, and display them in fullscreen, half-screen sheet, or popover using `present()`. All controls are real UIKit components — no WebView or cross-platform framework required.

### Key Features

- **Pythonista compatible**: Common APIs match Pythonista, making script migration straightforward
- **Native UIKit rendering**: All controls are native iOS components with the same performance as system apps
- **No installation**: Use `import ui` directly, built into Python IDE
- **Custom drawing**: Use `draw()`, `ImageContext`, `Path`, and related APIs for custom graphics
- **`.pyui` file support**: Build interfaces from JSON or plist layout files

### Supported Controls

| Control | Class | Description |
|---------|-------|-------------|
| Base view | `ui.View` | Base class for all views; supports frame, background color, corner radius, etc. |
| Button | `ui.Button` | Supports title, color, and tap callback |
| Label | `ui.Label` | Single- or multi-line text; font, alignment |
| Text field | `ui.TextField` | Single-line text input |
| Text view | `ui.TextView` | Multi-line editable text; delegate support |
| Image | `ui.ImageView` | Displays images; supports network loading |
| Switch | `ui.Switch` | Boolean toggle |
| Slider | `ui.Slider` | Continuous value from 0 to 1 |
| Segmented control | `ui.SegmentedControl` | Multiple option segments |
| Date picker | `ui.DatePicker` | Date / time / datetime picker |
| Scroll view | `ui.ScrollView` | Scrollable content area; delegate support |
| Table view | `ui.TableView` | List display; data_source, action, delegate |
| Web view | `ui.WebView` | Load URL or HTML; supports eval_js |
| Activity indicator | `ui.ActivityIndicator` | Loading spinner |
| Progress view | `ui.ProgressView` | Linear progress bar (0–1) |
| Stepper | `ui.Stepper` | +/- buttons with range and step |
| Navigation view | `ui.NavigationView` | Stack-based navigation with navigation bar |
| Canvas view | `ui.CanvasView` | Custom drawing; override draw |

---

## 2. Architecture

### Call Flow

```
Python (ui.py)
    ↓ ctypes C function calls
Swift (UIBridge.swift) — exports @_cdecl C interfaces
    ↓
Swift (UIModule.swift) — UIViewWrapper, UICallbackManager
    ↓
UIKit (UIView, UIButton, UILabel, ...)
```

- **Python side**: `pyboot/ui.py` loads the main app’s symbols via `ctypes.CDLL(None)` and calls C functions like `ui_create_view`, `ui_set_frame`, etc.
- **Swift side**: `UIBridge.swift` exports all `ui_*` C functions and delegates to `UIBridge.shared`.
- **Callbacks**: On user actions (button tap, table row selection, etc.), Swift invokes Python code via `UICallbackManager.triggerCallback`; Python looks up the handler in `ui._callbacks[callbackID]` and runs it.

### View IDs

Each view has a unique `view_id` string in Swift. Python holds it in `_view_id`. All property setters and methods pass this ID to C so Swift can locate the corresponding native view.

---

## 3. Quick Start

### Minimal Example: A View with a Button

```python
import ui

# Create root view
v = ui.View()
v.background_color = 'white'
v.frame = (0, 0, 300, 400)

# Create button
btn = ui.Button(title='Tap Me')
btn.frame = (50, 150, 200, 50)
btn.action = lambda sender: print('Button tapped')

# Add button to root view
v.add_subview(btn)

# Present as sheet (bottom half-screen modal)
v.present('sheet')
```

**How to run**: Open this script in the Python IDE editor and tap the run button. The native UI appears.

### With a Title

```python
import ui

v = ui.View()
v.background_color = 'white'
v.frame = (0, 0, 320, 480)
v.title = 'My Screen'  # Navigation bar title when presented

btn = ui.Button(title='Close')
btn.frame = (110, 200, 100, 44)
def on_close(sender):
    v.close()
btn.action = on_close
v.add_subview(btn)

v.present('sheet')
```

---

## 4. View Basics

Base class for all controls. Provides frame, colors, and subview management.

### Creation

```python
v = ui.View()
v = ui.View(frame=(0, 0, 320, 480))
```

### Properties (Full List)

| Property | Type | Description |
|----------|------|-------------|
| `frame` | `(x, y, width, height)` | Position and size in parent; points (pt) |
| `bounds` | `(x, y, width, height)` | Bounds in own coordinate system; read-only |
| `center` | `(x, y)` | Center point in parent |
| `x` | `float` | frame x (left) |
| `y` | `float` | frame y (top) |
| `width` | `float` | frame width |
| `height` | `float` | frame height |
| `background_color` | `str` or `tuple` | Background color; see color formats below |
| `bg_color` | same | Alias for `background_color` |
| `alpha` | `float` | Opacity, 0.0 (transparent) to 1.0 (opaque) |
| `hidden` | `bool` | Whether the view is hidden |
| `corner_radius` | `float` | Corner radius; 0 = square |
| `border_width` | `float` | Border width |
| `border_color` | `str` or `tuple` | Border color |
| `content_mode` | `int` | Content scaling mode; see `CONTENT_*` constants |
| `tint_color` | `str` or `tuple` | Tint color |
| `flex` | `str` | Autoresizing rules, e.g. `'W'`, `'H'`, `'WH'`, `'TRBL'` |
| `name` | `str` | View name for load_view binding and `view['name']` lookup |
| `touch_enabled` | `bool` | Whether view receives touches; default True |
| `multitouch_enabled` | `bool` | Multi-touch; default False |
| `transform` | `ui.Transform` or `None` | Affine transform |
| `clips_to_bounds` | `bool` | Clip subviews to view bounds |
| `accessibility_label` | `str` | VoiceOver label |
| `accessibility_value` | `str` | VoiceOver value |
| `accessibility_hint` | `str` | VoiceOver hint |
| `title` | `str` | Navigation bar title when presented |
| `left_button_items` | `tuple` | Left bar button items |
| `right_button_items` | `tuple` | Right bar button items |

### Color Formats

```python
v.background_color = 'white'           # Named
v.background_color = 'red'
v.background_color = (1, 0, 0, 1)     # RGBA, 0–1 per channel
v.background_color = (1, 0, 0, 0.5)   # Semi-transparent red
v.background_color = '#ff0000'        # Hex, 6 or 8 digits
v.background_color = '#ff000080'      # With alpha
```

### Methods

| Method | Description |
|--------|-------------|
| `add_subview(v)` | Add view `v` as subview |
| `remove_subview(v)` | Remove subview `v` |
| `remove_from_superview()` | Remove self from parent |
| `bring_to_front()` | Move to front of siblings |
| `send_to_back()` | Move to back of siblings |
| `bring_subview_to_front(subview)` | Bring specific subview to front |
| `send_subview_to_back(subview)` | Send specific subview to back |
| `set_needs_display()` | Mark as needing redraw |
| `set_needs_layout()` | Request layout update |
| `size_to_fit()` | Resize to fit content |
| `point_from_window(point)` | Convert window coords to view coords |
| `point_to_window(point)` | Convert view coords to window coords |

### Read-Only Properties

| Property | Type | Description |
|----------|------|-------------|
| `subviews` | `tuple` | All subviews |
| `superview` | `View` or `None` | Parent view |

### Lookup by Name

```python
btn.name = 'submit_btn'
found = v['submit_btn']
```

### Example: Card with Corners and Border

```python
import ui

card = ui.View()
card.frame = (20, 100, 280, 150)
card.background_color = 'white'
card.corner_radius = 12
card.border_width = 1
card.border_color = (0.8, 0.8, 0.8, 1)

label = ui.Label(text='Card content')
label.frame = (20, 20, 240, 30)
card.add_subview(label)
```

---

## 5. present and Display

### present

```python
v.present(style='fullscreen', animated=True, hide_title_bar=False)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `style` | `str` | `'fullscreen'`, `'full_screen'`, `'sheet'`, `'popover'` |
| `animated` | `bool` | Use transition animation; default True |
| `hide_title_bar` | `bool` | Hide navigation bar; default False |

### Styles

- **fullscreen**: Full-screen modal
- **sheet**: Half-screen from bottom; swipe down to dismiss
- **popover**: Popover style (common on iPad)

### Dismissing

```python
v.close()              # Close this view
ui.close_all()         # Close all presented views
ui.close_all(animated=False)
```

### Block Until Dismissed

```python
v.present('sheet')
v.wait_modal()  # Blocks until user dismisses
```

### NavigationView: Stack Navigation

```python
import ui

root = ui.View()
root.background_color = 'white'
root.frame = (0, 0, 320, 480)

nv = ui.NavigationView(root)
nv.navigation_bar_hidden = False
nv.bar_tint_color = 'white'

def go_next(sender):
    next_view = ui.View()
    next_view.background_color = 'white'
    next_view.frame = (0, 0, 320, 480)
    nv.push_view(next_view, animated=True)

btn = ui.Button(title='Next')
btn.frame = (110, 200, 100, 44)
btn.action = go_next
root.add_subview(btn)

nv.present('sheet')
```

| Method | Description |
|--------|-------------|
| `push_view(view, animated=True)` | Push a new view onto the stack |
| `pop_view(animated=True)` | Pop current view |

---

## 6. Button

### Creation

```python
btn = ui.Button()
btn = ui.Button(title='OK')
btn = ui.Button(frame=(50, 100, 200, 44))
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `title` | `str` | Button title |
| `title_color` | `str` or `tuple` | Title color |
| `font` | `tuple` or `str` | Font, e.g. `('Helvetica-Bold', 18)` |
| `image` | `ui.Image` | Foreground image |
| `background_image` | `ui.Image` | Background image |
| `enabled` | `bool` | Whether tap is enabled; default True |

### action Callback

Called on tap; receives `sender` (the button):

```python
def on_tap(sender):
    print('Tapped:', sender.title)

btn.action = on_tap
# or
btn.action = lambda s: print(s.title)
```

### Full Example

```python
btn = ui.Button(title='Submit')
btn.frame = (50, 150, 200, 44)
btn.title_color = 'blue'
btn.enabled = True
btn.action = lambda s: print('Submit')
```

---

## 7. Label

### Creation

```python
lbl = ui.Label()
lbl = ui.Label(text='Hello')
lbl = ui.Label(frame=(10, 10, 300, 40))
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `text` | `str` | Display text |
| `text_color` | `str` or `tuple` | Text color |
| `font` | `(name, size)` | Font, e.g. `('Helvetica', 17)`; `(' ', 17)` = system font |
| `alignment` | `int` | 0 left, 1 center, 2 right |
| `number_of_lines` | `int` | Max lines; 0 = unlimited |
| `line_break_mode` | `int` | Line break mode |
| `adjusts_font_size_to_fit` | `bool` | Shrink font to fit |
| `minimum_scale_factor` | `float` | Min scale when shrinking |

### Example

```python
lbl = ui.Label(text='Title')
lbl.frame = (20, 20, 280, 40)
lbl.font = ('Helvetica', 24)
lbl.alignment = 1
lbl.text_color = 'black'
```

---

## 8. TextField

### Creation

```python
tf = ui.TextField()
tf = ui.TextField(placeholder='Enter text')
tf = ui.TextField(text='Initial value')
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `text` | `str` | Current text |
| `placeholder` | `str` | Placeholder |
| `text_color` | `str` or `tuple` | Text color |
| `font` | `tuple` | Font, e.g. `('Helvetica', 16)` |
| `alignment` | `int` | Alignment |
| `secure` | `bool` | Password input (masked) |
| `keyboard_type` | `int` | Keyboard type |
| `autocapitalization_type` | `int` | Auto-caps (`0` none / `1` words / `2` sentences / `3` all) |
| `autocorrection_type` | `int` | Auto-correct (`0` default / `1` off / `2` on) |
| `spellchecking_type` | `int` | Spellcheck (`0` default / `1` off / `2` on) |
| `clear_button_mode` | `int` | Clear button (`0` never / `1` while editing / `3` always) |
| `return_key_type` | `int` | Return key (`0` default / `4` Search / `9` Done, etc.) |
| `bordered` | `bool` | Show border style |

### Callbacks

```python
tf.action = lambda sender: print('Input:', sender.text)           # Return / blur
tf.began_editing = lambda sender: print('Editing started')        # Focus gained
tf.ended_editing = lambda sender: print('Editing ended')          # Focus lost
```

---

## 9. TextView

### Creation

```python
tv = ui.TextView()
tv = ui.TextView(text='Multi-line content')
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `text` | `str` | Text content |
| `editable` | `bool` | Whether editable |
| `selectable` | `bool` | Whether selectable |
| `text_color` | `str` or `tuple` | Text color |
| `font` | `(name, size)` | Font |
| `alignment` | `int` | Text alignment `ui.ALIGN_*` |
| `selected_range` | `(start, length)` | Current selection range |
| `content_size` | `(w, h)` | Read-only, text content size |
| `content_offset` | `(x, y)` | Scroll offset |
| `auto_content_inset` | `bool` | Auto-adjust inset for keyboard |

### Callbacks

```python
tv.began_editing = lambda sender: print('Editing started')
tv.ended_editing = lambda sender: print('Editing ended')
```

### delegate

Set an object implementing:

| Method | Description |
|--------|-------------|
| `textview_did_begin_editing(textview)` | Fired when editing starts |
| `textview_did_change(textview)` | Fired when content changes |
| `textview_did_end_editing(textview)` | Fired when editing ends |

```python
class MyDelegate:
    def textview_did_begin_editing(self, tv):
        print('Editing started')
    def textview_did_end_editing(self, tv):
        print('Editing ended')

tv = ui.TextView(text='')
tv.delegate = MyDelegate()
```

---

## 10. ImageView

### Creation

```python
iv = ui.ImageView()
iv = ui.ImageView(frame=(0, 0, 200, 200))
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `image` | `PIL.Image` or `ui.Image` | Image to display |
| `content_mode` | `int` | Scaling mode |

### Methods

| Method | Description |
|--------|-------------|
| `load_from_url(url)` | Load image asynchronously from URL |

### Example

```python
iv = ui.ImageView()
iv.frame = (20, 20, 280, 200)
iv.load_from_url('https://example.com/image.png')
```

---

## 11. Switch

### Creation

```python
sw = ui.Switch()
sw = ui.Switch(value=True)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `value` | `bool` | On/off state |
| `enabled` | `bool` | Whether enabled |

### action Callback

```python
sw.action = lambda sender: print('Value:', sender.value)
```

---

## 12. Slider

### Creation

```python
sl = ui.Slider()
sl = ui.Slider(frame=(20, 100, 280, 30))
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `value` | `float` | Current value, 0.0–1.0 |
| `continuous` | `bool` | Fire action continuously while dragging |

### action Callback

```python
sl.action = lambda sender: print('Value:', sender.value)
```

---

## 13. SegmentedControl

### Creation

```python
seg = ui.SegmentedControl()
seg.frame = (20, 100, 280, 32)
seg.segments = ['Option A', 'Option B', 'Option C']
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `segments` | `list` or `str` | Segment titles (list or newline-separated) |
| `selected_index` | `int` | Selected segment index |

### action Callback

```python
seg.action = lambda sender: print('Selected:', sender.selected_index)
```

---

## 14. DatePicker

### Creation

```python
dp = ui.DatePicker()
dp.frame = (20, 100, 280, 200)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `date` | `float` | Selected date as timestamp |
| `mode` | `str` | `'date'`, `'time'`, `'datetime'` |
| `enabled` | `bool` | Whether enabled |

### action Callback

```python
dp.action = lambda sender: print('Date:', sender.date)
```

---

## 15. ScrollView

### Creation

```python
sv = ui.ScrollView()
sv.frame = (0, 0, 320, 400)
sv.content_size = (320, 800)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `content_size` | `(width, height)` | Content size |
| `content_offset` | `(x, y)` | Current scroll offset |
| `content_inset` | `(top, left, bottom, right)` | Content insets |
| `bounces` | `bool` | Bounce effect |
| `always_bounce_horizontal` | `bool` | Always bounce horizontally |
| `always_bounce_vertical` | `bool` | Always bounce vertically |
| `scroll_enabled` | `bool` | Whether scrolling is enabled |
| `paging_enabled` | `bool` | Paging mode |
| `shows_vertical_scroll_indicator` | `bool` | Show vertical scroll indicator |
| `shows_horizontal_scroll_indicator` | `bool` | Show horizontal scroll indicator |
| `zoom_scale` | `float` | Current zoom scale |
| `min_zoom_scale` | `float` | Minimum zoom scale |
| `max_zoom_scale` | `float` | Maximum zoom scale |

### Methods

| Method | Description |
|--------|-------------|
| `scroll_to(x, y, animated=True)` | Scroll to offset |

### delegate

```python
class MyDelegate:
    def scrollview_did_scroll(self, x, y):
        print('Scrolled to:', x, y)

sv = ui.ScrollView()
sv.content_size = (300, 800)
sv.delegate = MyDelegate()
```

### Example: Long Content

```python
sv = ui.ScrollView()
sv.frame = (0, 0, 320, 400)
sv.content_size = (320, 1200)
sv.bounces = True
sv.always_bounce_vertical = True

lbl = ui.Label(text='Very long text...')
lbl.frame = (10, 10, 300, 1180)
sv.add_subview(lbl)
```

---

## 16. TableView

### Creation

```python
tv = ui.TableView()
tv.frame = (0, 0, 320, 400)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `data_source` | `list` | Data; see format below |
| `action` | `callable` | Row selection callback |
| `delegate` | `object` | Delegate object |
| `row_height` | `float` | Default row height |
| `editing` | `bool` | Whether in editing mode |
| `selected_row` | `tuple` | Currently selected row `(section, row)` |
| `separator_color` | `str` or `tuple` | Separator line color |
| `allows_selection` | `bool` | Whether selection is enabled |
| `allows_multiple_selection` | `bool` | Whether multi-selection is enabled |
| `delete_enabled` | `bool` | Whether swipe-to-delete is enabled |
| `move_enabled` | `bool` | Whether drag-to-reorder is enabled |

### data_source Format

- Flat list: `[{'title': 'A', 'subtitle': 'a'}, {'title': 'B'}]`
- Nested (sections): `[[{...}, {...}], [{...}]]`
- Each item needs `title`; `subtitle` is optional

### action Callback

```python
tv.action = lambda sender, section, row: print('Selected', section, row)
```

### delegate

Implement `tableview_did_select(tableview, section, row)`.

### Methods

| Method | Description |
|--------|-------------|
| `reload_data()` | Refresh the table |

### Example

```python
tv = ui.TableView()
tv.frame = (0, 0, 320, 400)
tv.data_source = [
    {'title': 'Row 1', 'subtitle': 'Detail'},
    {'title': 'Row 2'},
    {'title': 'Row 3', 'subtitle': 'More detail'},
]
tv.action = lambda s, sec, r: print(f'Section {sec}, Row {r}')
tv.reload_data()
```

---

## 17. WebView

### Creation

```python
wv = ui.WebView()
wv.frame = (0, 0, 320, 400)
```

### Methods

| Method | Description |
|--------|-------------|
| `load_url(url)` | Load URL |
| `load_html(html, base_url=None)` | Load HTML string |
| `go_back()` | Go back |
| `go_forward()` | Go forward |
| `reload()` | Reload |
| `stop()` | Stop loading |
| `eval_js(code, callback=None)` | Run JavaScript; callback receives result |

### Example

```python
wv = ui.WebView()
wv.frame = (0, 0, 320, 400)
wv.load_url('https://www.apple.com')
wv.eval_js('document.title', lambda result: print('Title:', result))
```

---

## 18. ActivityIndicator

### Creation

```python
ai = ui.ActivityIndicator()
ai.frame = (140, 200, 37, 37)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `animating` | `bool` | Whether spinning |
| `style` | `int` | GRAY, WHITE, WHITE_LARGE |
| `hides_when_stopped` | `bool` | Hide when stopped |

### Methods

```python
ai.start()   # or ai.start_animating()
ai.stop()    # or ai.stop_animating()
```

---

## 18b. ProgressView

### Creation

```python
pv = ui.ProgressView()
pv.frame = (20, 100, 280, 10)
pv.progress = 0.5  # 50%
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `progress` | `float` | Progress value, 0.0 to 1.0 |
| `progress_tint_color` | `str` or `tuple` | Completed portion color |
| `track_tint_color` | `str` or `tuple` | Track (remaining) color |

---

## 18c. Stepper

### Creation

```python
st = ui.Stepper()
st.frame = (100, 100, 94, 29)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `value` | `float` | Current value |
| `minimum_value` | `float` | Minimum (default 0) |
| `maximum_value` | `float` | Maximum (default 100) |
| `step_value` | `float` | Step increment (default 1) |
| `continuous` | `bool` | Continuous change on long press |
| `wraps` | `bool` | Wrap around when exceeding range |
| `tint_color` | `str` or `tuple` | Tint color |
| `enabled` | `bool` | Whether enabled |

### Callback

```python
st.action = lambda sender: print('Value:', sender.value)
```

---

## 19. NavigationView

See [5. present and Display](#5-present-and-display).

---

## 20. Custom View and Drawing

### Subclass View and Override draw

```python
class MyView(ui.View):
    def draw(self):
        pass
```

### Touch Callbacks

| Method | Description |
|--------|-------------|
| `touch_began(touch)` | Finger down |
| `touch_moved(touch)` | Finger moved |
| `touch_ended(touch)` | Finger up |

`touch` has `location`, `prev_location`, etc.

### CanvasView and ImageContext

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
cv.render = draw_canvas
```

### Drawing APIs (Summary)

| API | Description |
|-----|-------------|
| `ui.set_color(color)` | Set drawing color |
| `ui.fill_rect(x, y, w, h)` | Fill rectangle |
| `ui.stroke_rect(x, y, w, h)` | Stroke rectangle |
| `ui.draw_string(text, rect=(x,y,w,h))` | Draw text |
| `Path.rect(x, y, w, h)` | Rectangle path |
| `Path.oval(x, y, w, h)` | Oval path |
| `Path.round_rect(x, y, w, h, r)` | Rounded rect |
| `path.fill()` / `path.stroke()` | Fill / stroke path |
| `path.move_to(x, y)` / `path.line_to(x, y)` | Line path |
| `path.add_arc(...)` | Arc |
| `path.add_curve(...)` | Bezier curve |
| `path.add_rect(x, y, w, h)` | Rectangle sub-path |
| `path.add_oval(x, y, w, h)` | Oval sub-path |
| `path.copy()` | Deep copy of path |
| `path.hit_test(x, y)` | Test if point is inside path |
| `path.get_bounding_box()` | Bounding rect `(x, y, w, h)` |
| `GState()` | Save / restore state |
| `ui.set_blend_mode(mode)` | Blend mode |
| `ui.set_shadow(...)` | Shadow |

### ImageContext

**Method 1: Context manager (recommended)**

```python
with ui.ImageContext(200, 200) as ctx:
    ui.set_color('blue')
    ui.fill_rect(0, 0, 200, 200)
    img = ctx.get_image()  # ui.Image
```

**Method 2: Functional API**

```python
ui.begin_image_context(200, 200)
ui.set_color('red')
ui.fill_rect(0, 0, 200, 200)
img = ui.get_image_from_current_context()  # ui.Image
ui.end_image_context()
```

### Image Class

| Entry | Description |
|-------|-------------|
| `ui.Image.named(name)` | Built-in or bundled resource |
| `ui.Image.from_data(data)` | From bytes |
| `ui.Image.from_image_context()` | From current offscreen context |
| `ui.Image(name)` | Equivalent to `Image.named(name)` |

| Property / Method | Description |
|-------------------|-------------|
| `size` | `(w, h)` |
| `to_png()` | PNG `bytes` |
| `resized(size)` | Resized copy |
| `cropped(rect)` | Cropped copy |
| `crop(rect)` | Crop `(x, y, w, h)`; native implementation |
| `clip_to_mask(mask)` | Clip using another Image's alpha channel |
| `with_rendering_mode(mode)` | Template / original rendering mode |

---

## 21. load_view and load_view_str

### load_view(name, bindings=None, ...)

Load layout from file. `name` is the filename (`.pyui` added if omitted). Supports JSON and plist. Searches current working directory and user home.

```python
v = ui.load_view('MyView')
v = ui.load_view('MyView', bindings={'submit': on_submit})
```

### load_view_str(json_str, bindings=None, ...)

Load from JSON string:

```python
json_str = '''
{
  "UIView": {
    "frame": "{{0,0},{320,400}}",
    "subviews": [
      {"UIButton": {"frame": "{{50,100},{200,44}}", "title": "OK"}}
    ]
  }
}
'''
v = ui.load_view_str(json_str, bindings={'submit': on_submit})
```

### frame Format

In `.pyui`, frame uses `{{x,y},{width,height}}`, e.g. `{{0,0},{320,480}}`.

### bindings

Maps names to callables for actions. If JSON has `"action": "submit"`, the binding `submit` is used as the action.

---

## 22. animate and Utility Functions

### animate

```python
ui.animate(animation, duration=0.25, delay_sec=0.0, completion=None)
```

- `animation`: Callable (no args), runs after `delay_sec`
- `duration`: Seconds; completion runs after this
- `delay_sec`: Delay before animation
- `completion`: Callable, runs after `duration` seconds

**Note**: The animation callback runs asynchronously; view property changes take effect immediately and do not participate in UIKit transitions.

### Utility Functions

| Function | Description |
|----------|-------------|
| `ui.get_screen_size()` | Returns `(width, height)` |
| `ui.get_window_size()` | Window size |
| `ui.get_ui_style()` | `'light'` or `'dark'` |
| `ui.convert_point(point, from_view, to_view)` | Convert point |
| `ui.convert_rect(rect, from_view, to_view)` | Convert rect |
| `ui.measure_string(text, font, max_width)` | Measure text; returns `(width, height)` |
| `ui.close_all(animated=False)` | Close all presented views |
| `ui.dump_view(view)` | Debug: print view hierarchy |
| `ui.delay(sec, fn)` | Run function after delay |
| `ui.in_background(fn)` | Run in background thread |

---

## 23. Constants and Enums

### Content Mode (CONTENT_*)

| Constant | Description |
|----------|-------------|
| `ui.CONTENT_SCALE_TO_FILL` | Scale to fill |
| `ui.CONTENT_SCALE_ASPECT_FIT` | Aspect fit |
| `ui.CONTENT_SCALE_ASPECT_FILL` | Aspect fill |
| `ui.CONTENT_REDRAW` | Redraw |
| etc. | Maps to UIView.ContentMode |

### ActivityIndicator Styles

| Constant | Description |
|----------|-------------|
| `ui.ACTIVITY_INDICATOR_STYLE_GRAY` | Gray |
| `ui.ACTIVITY_INDICATOR_STYLE_WHITE` | White |
| `ui.ACTIVITY_INDICATOR_STYLE_WHITE_LARGE` | Large white |

---

## 24. Troubleshooting

### AttributeError: Attribute does not exist

- Check property name (e.g. `background_color`, not `backgroundColor`)
- Ensure the control supports the attribute

### Callbacks not firing (action, delegate)

- Ensure `action` or `delegate` is set correctly
- Check `enabled` is True
- For delegate, use correct method names (e.g. `scrollview_did_scroll`)

### White screen or crash after present

- Give root view a valid `frame` (width and height > 0)
- Avoid nesting present calls (e.g. present inside sheet)

### load_view parse error

- Ensure valid JSON or plist
- Use frame format `{{x,y},{w,h}}`
- Complex nesting or custom classes may not be fully supported

### Drawing not visible

- Call `set_needs_display()` to trigger redraw
- Call `ImageContext.get_image()` inside the `with` block

---

*Document version: 2026-03 · For Python IDE iOS app*
