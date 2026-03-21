# objc_util 模块 — Objective-C 运行时桥接

PythonIDE / Pythonista 完全兼容的 Objective-C 运行时桥接模块，通过 `ctypes` 直接调用 Objective-C 运行时，可访问 iOS 系统框架中的类与方法。

**源码位置：** `pyboot/objc_util.py`  
**公开符号：** 以模块 `__all__` 为准；下文同时说明实现中存在但未列入 `__all__` 的辅助 API。

---

## 依赖与环境

- 依赖 Python 标准库 `ctypes`；不可用时导入模块会抛出 `NotImplementedError`。
- 依赖本环境提供的 `ui` 模块（与 PythonIDE 集成相关）。
- 使用 `pyparsing` 解析部分 ObjC 类型编码。

---

## 核心类

### `ObjCClass(name)`

包装指向 Objective-C **类**的指针，作为调用**类方法**的代理。

| 参数 | 说明 |
|------|------|
| `name` | `str`（Python 3 内部会按 ASCII 编码为 `bytes`）：ObjC 类名，如 `'UIDevice'`、`'NSFileManager'`。 |

**行为要点：**

- 按类名**缓存**：同一类名多次构造得到同一 `ObjCClass` 实例（`__new__` 备忘录）。
- 若运行时中不存在该类，构造时抛出 `ValueError`。
- **下划线 → 冒号**：属性访问得到的方法名里，`_` 会替换为 `:` 构成 selector，例如 `dictionaryWithObject_forKey_(obj, key)` 对应 `[NSDictionary dictionaryWithObject:obj forKey:key]`。
- **新语法**：方法名中**不含**下划线时，得到 `ObjCClassMethodProxy`，在**调用时**根据位置参数与关键字参数解析 selector（见 `resolve_cls_method` / `get_possible_method_names`），支持形如 `cls.methodName(param=value, ...)` 的写法。
- 任意类方法若返回 ObjC 对象指针（类型编码以 `@` 开头），会被包装为 `ObjCInstance`。

**特殊方法：**

- `__str__`：形如 `<ObjCClass: ClassName>`。
- `__eq__`：仅比较是否为 `ObjCClass` 且类名相同。
- `__dir__`：沿类层次收集类方法对应的 Python 风格名（`:` → `_`），在到达 `NSObject` 的 metaclass 时用内置列表 `NSObject_class_methods` 截断，避免 category 产生过长列表。

**类方法：**

- **`ObjCClass.get_names(prefix=None)` → `list`**  
  调用 `objc_getClassList` 枚举运行时中所有类，返回类名字符串列表（已排序）。若 `prefix` 不为 `None`，只保留 `startswith(prefix)` 的项。

- **`ObjCClass.create(*args, **kwargs)`**  
  等价于 `create_objc_class(*args, **kwargs)`。

---

### `ObjCInstance(ptr)`

包装指向 Objective-C **实例**的指针，用于发送实例消息。

| 参数 | 说明 |
|------|------|
| `ptr` | 裸指针、`c_void_p`、`ObjCInstance`，或带 `_objc_ptr` 的对象；会规范为整数地址。 |

**行为要点：**

- **实例缓存**：`weakref.WeakValueDictionary`，同一指针尽量复用同一 `ObjCInstance`（若旧包装已被 GC，可能新建）。
- **内存管理**：对非 `NSAutoreleasePool` 实例，在 `__new__` 中通过 `objc_msgSend` 调用 `retain`；在 `__del__` 中调用 `release`。
- **类方法式调用**：与 `ObjCClass` 相同，支持下划线 selector 与新语法关键字解析（`ObjCInstanceMethodProxy` / `resolve_instance_method`）。
- **方法 / 属性读**：`__getattr__` 返回 `ObjCInstanceMethod` 或 `ObjCInstanceMethodProxy`；须通过 **`()`** 调用才会执行 ObjC 消息。解析阶段若无实例方法且允许 property，可按运行时属性合成 getter。
- **属性写**：`__setattr__` 对非保留字段名（`ptr`、`weakrefs`、`_cached_methods`、`_as_parameter_` 除外），尝试调用 `set` + 首字母大写 + 其余 + `_` 的 setter；失败则写入 `__dict__`（用于在包装器上挂载 `func`、`args` 等 Python 数据）。
- **`__str__`**：对对象发送 `description` 再 `UTF8String`，得到可读字符串。
- **`__repr__`**：`<类名: description字符串>`。
- **`__eq__` / `__hash__`**：按指针比较/哈希。

**集合协议（NSArray / NSDictionary / NSSet）：**

- **`for x in instance`**：通过 `ObjCIterator` 使用 `objectEnumerator()` / `nextObject()`。
- **`len(instance)`**：`count()`。
- **`instance[key]`**：`NSArray` 为整数下标（支持负数索引）；`NSDictionary` 的 key 会经 `ns(key)` 转为 `NSString`。不存在的 key 返回 `None`（ObjC `nil`）。
- **`instance[key] = value`**：仅 `NSMutableArray` / `NSMutableDictionary`。
- **`del instance[key]`**：仅 `NSMutableArray` / `NSMutableDictionary`。

**布尔值：** 若实现 `len` 则用 `len != 0`，否则指针非空为真。

**`__dir__`**：沿实例的真实类（`object_getClass`）收集实例方法名，在 `NSObject` 处用 `NSObject_instance_methods` 截断。

**32 位与结构体返回值：** 当非 LP64 且返回类型为 `ctypes.Structure` 子类时，使用 `objc_msgSend_stret` 传递返回缓冲区。

---

### `ObjCClassMethod(cls, method_name)`

类方法的底层包装（一般由 `ObjCClass` 自动创建）。`method_name` 为带下划线的 Python 风格名；若直接映射无对应类方法，会尝试下划线/冒号位置的所有组合以兼容 selector 中含下划线的情况。

**调用：**

- 默认根据 `method_getTypeEncoding` 解析参数/返回类型并调用 `objc_msgSend`。
- 可显式传入 **`restype`**、**`argtypes`**（keyword）覆盖解析结果；此时 `argtypes` 应为**除** `self` 与 `_cmd` 外的参数类型列表（实现中会前置 `[c_void_p, c_void_p]`）。
- 参数会自动经 `_auto_wrap`：`@` 或 `^{...}` 与 Python 对象互转时走 `ns()`；selector 参数允许传 `str` 并转为 `sel()`；`Structure` 子类允许传 `tuple` 并用 `struct_from_tuple` 构造。

---

### `ObjCInstanceMethod(obj, method_name, allow_property=True)`

实例方法的底层包装。除上述类方法逻辑外，若未找到方法且 `allow_property=True`，可能按 **属性** 合成 encoding 与 selector（getter/setter）。

---

### `ObjCClassMethodProxy` / `ObjCInstanceMethodProxy`

实现「无下划线方法名 + 调用时按 kwargs 解析」的代理类，通常无需直接使用。解析结果按 `(位置参数个数, 排序后的 kw 键)` 缓存。

**说明（与下划线语法对比）：** 访问 `instance.foo`（名中无 `_`）得到的是**可调用代理**，一般需写成 **`instance.foo()`** 才会发送消息；带下划线的方法名则直接绑定 `ObjCInstanceMethod`，同样以 `()` 调用。无对应实例方法时，`ObjCInstanceMethod` 在 `allow_property=True` 时可回退到 **ObjC 属性**的 getter/setter 编码。**赋值** `instance.name = value` 由 `__setattr__` 尝试调用 `setName_`，不经过上述代理。

---

### `ObjCBlock(func, restype=None, argtypes=None)`

将 Python 可调用对象包装为 ObjC Block 字面量结构，供 ctypes 调用链使用。

| 参数 | 说明 |
|------|------|
| `func` | 必须 `callable`。 |
| `restype` | ctypes 返回类型，默认 `None`。 |
| `argtypes` | ctypes 参数类型序列，默认 `[]`。 |

**实现细节：**

- 使用 `ctypes.CFUNCTYPE(restype, *argtypes)` 生成 `invoke` 函数指针；`isa` 指向 `__NSGlobalBlock__`。
- **`_as_parameter_`**：LP64 为结构体本身，32 位为 `byref(block)`。
- **`from_param(cls, param)`**（classmethod）：`ObjCBlock` 或 `None` 原样返回；普通 `callable` 会新建 `ObjCBlock` 并挂在 `param._block` 上以防过早释放；否则抛 `TypeError`。
- **`__call__(*args)`**：直接调用底层 Python `func`。

类型表 `type_encodings` 中含 `'@?'` → `ObjCBlock`，用于 Block 对象参数编码。

---

### `ObjCIterator(obj)`（内部用于迭代）

包装集合的 `objectEnumerator()`，实现迭代器协议；`next` / `__next__` 在 `nextObject()` 为 `nil` 时抛出 `StopIteration`。未在 `__all__` 中导出，但为 `ObjCInstance.__iter__` 所使用。

---

## 结构体类型

均为 `ctypes.Structure` 子类，字段与 Apple 定义一致：

| 类型 | `_fields_` |
|------|------------|
| `CGPoint` | `x` (`CGFloat`), `y` (`CGFloat`) |
| `CGSize` | `width`, `height` (`CGFloat`) |
| `CGVector` | `dx`, `dy` (`CGFloat`) |
| `CGRect` | `origin` (`CGPoint`), `size` (`CGSize`) |
| `CGAffineTransform` | `a`, `b`, `c`, `d`, `tx`, `ty` (`CGFloat`) |
| `UIEdgeInsets` | `top`, `left`, `bottom`, `right` (`CGFloat`) |
| `NSRange` | `location`, `length` (`NSUInteger`) |

**辅助（模块内，非 `__all__`）：**

- `struct_from_tuple(cls, t)`：递归把元组填进嵌套 `Structure`。
- 未知 `{StructName=...}` 编码时可通过 `parse_struct` 动态生成匿名 `Structure` 子类（供 `parse_types` 使用）。

---

## 类型常量

| 名称 | 定义（与源码一致） |
|------|-------------------|
| `LP64` | `sizeof(c_void_p) == 8` |
| `CGFloat` | LP64 为 `c_double`，否则 `c_float` |
| `NSInteger` | LP64 为 `c_long`，否则 `c_int` |
| `NSUInteger` | LP64 为 `c_ulong`，否则 `c_uint` |
| `NSNotFound` | Python 3：`sys.maxsize`；Python 2：`sys.maxint` |
| `NSUTF8StringEncoding` | `4` |
| `NS_UTF8` | `NSUTF8StringEncoding` 的别名 |

---

## 模块级变量与句柄

### `c`

`ctypes.cdll.LoadLibrary(None)` 返回的库句柄，已绑定大量 ObjC 运行时符号（如 `objc_msgSend`、`class_getName` 等），也可用于 `c['objc_msgSend']` 等形式避免并发修改模块级 `argtypes`/`restype` 时的竞态（实例方法路径中有类似用法）。

---

## 模块级函数

### `sel(sel_name)` → selector

将字符串注册为 selector（`sel_registerName`）。Python 3 下会将 `str` 编码为 ASCII `bytes`。

```python
from objc_util import sel
s = sel('viewDidLoad')
```

---

### `ns(py_obj)` → `ObjCInstance`

将常见 Python 值转为 Foundation 对象；已是 `ObjCInstance` 则原样返回。`c_void_p` 或带 `_objc_ptr` 会包装为 `ObjCInstance`。

| Python | ObjC |
|--------|------|
| `str` | `NSString.stringWithUTF8String_`（UTF-8 字节） |
| `bytes`（Py3） | `NSData.dataWithBytes_length_` |
| `str`（Py2） | 同上直接 C 字符串 |
| `unicode`（Py2） | UTF-8 编码后同上 |
| `bytearray`（Py2） | `NSData` |
| `int` | `NSNumber.numberWithInt_` |
| `float` | `NSNumber.numberWithDouble_` |
| `bool` | `NSNumber.numberWithBool_` |
| `list` | `NSMutableArray`，元素递归 `ns()` |
| `dict` | `NSMutableDictionary`，键值递归 `ns()` |
| `set` | `NSMutableSet`，元素递归 `ns()` |

---

### `nsurl(url_or_path)` → `ObjCInstance`（`NSURL`）

- 参数必须为字符串（`basestring`）；否则 `TypeError`。
- 若字符串 **包含** `':'`：`NSURL.URLWithString_(ns(url_or_path))`。
- 否则：`NSURL.fileURLWithPath_(ns(url_or_path))`。

---

### `nsdata_to_bytes(data)` → `bytes`

要求 `data` 为 `ObjCInstance` 且 `isKindOfClass_(NSData)`。通过 `length()`、`getBytes_length_` 拷贝为 Python `bytes`。长度为 0 时返回 `b''`。

---

### `uiimage_to_png(img)` → `bytes`

要求 `img` 为 `UIImage` 实例。调用 C 函数 `UIImagePNGRepresentation`，再经 `nsdata_to_bytes` 返回 PNG 数据。

---

### `retain_global(obj)` / `release_global(obj)`

将对象追加到模块级列表 `_retained_globals`，防止被 Python GC 回收（用于 IMP、Block 等需长期存活的对象）。`release_global` 尝试从列表移除，不存在则静默忽略。

---

### `on_main_thread(func)` → 包装函数

装饰器：若当前已在主线程（`NSThread.isMainThread`，显式 `restype=c_bool, argtypes=[]`），直接调用；否则构造运行时类 `OMMainThreadDispatcher`（或 `OMMainThreadDispatcher_3`）的实例，把 `func`、`args`、`kwargs` 存到实例上，在主线程 `performSelectorOnMainThread_withObject_waitUntilDone_` 执行 `invoke`，**同步等待**完成后 `release` 分发器并返回 `retval`。

非可调用对象会 `TypeError`。

```python
@on_main_thread
def update_ui():
    label.text = '更新完成'
```

---

### `settrace(func)`（未列入 `__all__`）

设置模块全局 `_tracefunc`；主线程分发器 `invoke` 实现中若其非空会 `sys.settrace(_tracefunc)`。用于调试。

---

### `create_objc_class(name, superclass=NSObject, methods=[], classmethods=[], protocols=[], debug=True)` → `ObjCClass`

动态注册 ObjC 类并返回 `ObjCClass`。

| 参数 | 说明 |
|------|------|
| `name` | 类名字符串（Py3 会编码为 ASCII bytes 再交给运行时）。 |
| `superclass` | `ObjCClass`，默认 `NSObject`。 |
| `methods` | 实例方法：Python 函数列表。 |
| `classmethods` | 类方法：在 `objc_registerClassPair` **之后** 加到 **metaclass** 上；注册类方法时**不会**传入 `protocols`（源码中固定为 `[]`），编码主要从父类 metaclass 或默认规则推断。 |
| `protocols` | 协议名字符串列表：仅用于**实例方法**在无法从父类得到 encoding 时的协议查询。 |
| `debug` | `True`（默认）：若 `ObjCClass(name)` 已存在则递增后缀 `name_2`、`name_3`… 直到可用名（文档字符串说明可能泄漏少量内存但便于开发）。`False`：若已有同名类则**直接返回该类**，**忽略**本次其余参数（用于稳定版本避免重复注册泄漏）。 |

**方法元数据（可选属性）：**

- `method.selector`：显式 selector 字符串（覆盖由函数名推导的规则）。
- `method.encoding`：显式类型编码字符串。
- `method.restype` + `method.argtypes`：与 `_add_method` 中 ctypes 签名一致时，可跳过 `parse_types` 的解析（`argtypes` 仍为不含 `self`/`_cmd` 的部分）。

签名与 Python 函数参数个数不一致会 `ValueError`。IMP 会通过 `retain_global` 保留。

```python
def my_method(self, cmd, arg):
    pass
my_method.selector = 'myMethod:'
my_method.encoding = 'v@:@'
```

---

### `load_framework(name)` → 返回值由 `NSBundle.load()` 决定

等价于：

`NSBundle.bundleWithPath_('/System/Library/Frameworks/%s.framework' % name).load()`

成功与否取决于系统是否提供该路径与 bundle。示例：

```python
from objc_util import load_framework
load_framework('Vision')
load_framework('AVFoundation')
```

---

### `autoreleasepool()`（上下文管理器，未列入 `__all__`）

```python
with autoreleasepool():
    # ObjC 操作...
    pass
```

实现：`NSAutoreleasePool.new()`，`yield` 后 `drain()`。

---

## 预定义类常量

模块加载时已执行 `ObjCClass(...)` 的变量（与 `__all__` 一致）：

**Foundation：** `NSObject`, `NSArray`, `NSMutableArray`, `NSDictionary`, `NSMutableDictionary`, `NSSet`, `NSMutableSet`, `NSString`, `NSMutableString`, `NSData`, `NSMutableData`, `NSNumber`, `NSURL`, `NSEnumerator`, `NSThread`, `NSBundle`

**UIKit：** `UIColor`, `UIImage`, `UIBezierPath`, `UIApplication`, `UIView`

---

## ctypes 重新导出

模块从 `ctypes` 重新导出以下名称，可直接 `from objc_util import ...` 使用：

`Structure`, `sizeof`, `byref`, `c_void_p`, `c_char`, `c_byte`, `c_char_p`, `c_double`, `c_float`, `c_int`, `c_longlong`, `c_short`, `c_bool`, `c_long`, `c_int32`, `c_ubyte`, `c_uint`, `c_ushort`, `c_ulong`, `c_ulonglong`, `POINTER`, `pointer`

另见上文 **`c`**（`cdll.LoadLibrary(None)`）。

---

## 异常与全局钩子

模块导入时会：

- 注册 `NSSetUncaughtExceptionHandler`，将未捕获 ObjC 异常写入 `~/Documents/_objc_exception.txt`（含时间与 `description`）。

---

## 完整示例

```python
from objc_util import *

# 获取设备信息
UIDevice = ObjCClass('UIDevice')
device = UIDevice.currentDevice()
print(f'系统版本: {device.systemVersion()}')
print(f'设备名称: {device.name()}')
print(f'设备型号: {device.model()}')

# 加载 Vision 框架进行文字识别
load_framework('Vision')

# 在主线程执行 UI 操作
@on_main_thread
def show_alert():
    UIAlertController = ObjCClass('UIAlertController')
    alert = UIAlertController.alertControllerWithTitle_message_preferredStyle_(
        ns('提示'), ns('Hello from objc_util!'), 1
    )
    UIAlertAction = ObjCClass('UIAlertAction')
    ok = UIAlertAction.actionWithTitle_style_handler_(ns('OK'), 0, None)
    alert.addAction_(ok)
    app = UIApplication.sharedApplication()
    vc = app.keyWindow().rootViewController()
    while vc.presentedViewController():
        vc = vc.presentedViewController()
    vc.presentViewController_animated_completion_(alert, True, None)

show_alert()
```

---

## `__all__` 一览（官方公开导出）

`c`, `LP64`, `CGFloat`, `NSInteger`, `NSUInteger`, `NSNotFound`, `NSUTF8StringEncoding`, `NS_UTF8`, `CGPoint`, `CGSize`, `CGVector`, `CGRect`, `CGAffineTransform`, `UIEdgeInsets`, `NSRange`, `sel`, `ObjCClass`, `ObjCInstance`, `ObjCClassMethod`, `ObjCInstanceMethod`, `NSObject`, `NSArray`, `NSMutableArray`, `NSDictionary`, `NSMutableDictionary`, `NSSet`, `NSMutableSet`, `NSString`, `NSMutableString`, `NSData`, `NSMutableData`, `NSNumber`, `NSURL`, `NSEnumerator`, `NSThread`, `NSBundle`, `UIColor`, `UIImage`, `UIBezierPath`, `UIApplication`, `UIView`, `ObjCBlock`, `ns`, `nsurl`, `retain_global`, `release_global`, `on_main_thread`, `create_objc_class`, `Structure`, `sizeof`, `byref`, `c_void_p`, `c_char`, `c_byte`, `c_char_p`, `c_double`, `c_float`, `c_int`, `c_longlong`, `c_short`, `c_bool`, `c_long`, `c_int32`, `c_ubyte`, `c_uint`, `c_ushort`, `c_ulong`, `c_ulonglong`, `POINTER`, `pointer`, `load_framework`, `nsdata_to_bytes`, `uiimage_to_png`

---

## 注意事项

1. **下划线与冒号**：默认将方法名中的 `_` 替换为 `:`；selector 本身含下划线时，实现会尝试多种 `_`/`:` 组合以消歧义。
2. **自动装箱**：调用方法时，对对象/指针类参数会经 `_auto_wrap` 调用 `ns()` 等；元组可自动转为已知的 `Structure` 类型。
3. **主线程**：UI 相关调用应通过 `@on_main_thread` 或等价机制保证在主线程执行。
4. **内存**：`ObjCInstance` 对普通对象 retain/release；传入 ObjC 的 **回调 IMP、Block** 等需用 `retain_global`（或由 `ObjCBlock.from_param` 挂在 callable 上）避免 Python 侧先释放。
5. **`create_objc_class` 与 `debug`**：`debug=True` 时类名冲突会自动加后缀，返回值类名可能与传入 `name` 不同，应使用返回的 `ObjCClass`；`debug=False` 时重复定义会直接返回已存在类且忽略新定义。
6. **新语法多义性**：关键字参数可能对应多种 selector 排列；若匹配多个或零个方法，会 `AttributeError`（`Method name is ambiguous` / `No method found`）。
7. **`dir()`**：`ObjCClass` / `ObjCInstance` 的 `__dir__` 在 `NSObject` 层用人肉列表截断，并非运行时全部方法。
8. **`parse_types`**：未支持的类型编码会 `NotImplementedError`；复杂方法可改用 `restype`/`argtypes` 显式指定。
