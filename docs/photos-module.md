# photos 模块 — iOS 相册与相机

面向 Pythonista API 的兼容实现，用于在嵌入式 Python 环境中访问 iOS 照片库、调用系统相机拍照、将图片写回相册。通过主程序导出的 C 符号（`ctypes.CDLL(None)`）与 Swift/Photos 层通信。

在默认配置下，**选取/拍照得到的像素数据会经 Pillow 解析为 `PIL.Image`**；若未安装 PIL，可选用 `raw_data=True`（仅 `pick_image`）或依赖 `base64_to_image` 在无 PIL 时返回 `bytes`。

实现文件：`pyboot/photos.py`。

---

## 核心函数

### `pick_image(show_albums=False, include_metadata=False, original=True, raw_data=False, multi=False, **kwargs)` → `PIL.Image | bytes | None`

从系统照片选择器选取一张图片。

| 行为 | 说明 |
|------|------|
| 成功 | `raw_data=False` 且已安装 Pillow：返回 `PIL.Image`；`raw_data=True`：返回 `bytes`（含长度前缀剥离后的纯图像文件数据）。 |
| 取消 | 返回 `None`。 |
| 无 PIL | 若 `raw_data=False`，打印错误并返回 `None`；若 `raw_data=True`，不依赖 PIL。 |

**参数（兼容 Pythonista，多数忽略）：**

- `show_albums`、`include_metadata`、`original`、`multi`：接受但**不使用**。
- `**kwargs`：全部忽略。

底层调用：`photos_pick_image_data()`，返回内存由 `photos_free_data` 释放。

---

### `capture_image(camera='back', show_preview=True, flash='auto', **kwargs)` → `PIL.Image | None`

使用系统相机界面拍照（iOS 侧为 `UIImagePickerController` 一类流程）。

| 行为 | 说明 |
|------|------|
| 成功 | 返回 `PIL.Image`（经 `Image.open(BytesIO(...))`）。 |
| 取消 | 返回 `None`。 |
| 无 PIL | 打印错误并返回 `None`（**不支持** `raw_data`，与 `pick_image` 不同）。 |

**参数（均忽略，仅兼容签名）：**

- `camera`：如 `'back'`、`'front'`、`'rear'` 等。
- `show_preview`、`flash`：如 `'auto'`、`'on'`、`'off'`。
- `**kwargs`：忽略。

底层调用：`photos_capture_image_data()`。

---

### `save_image(image, format='JPEG', quality=0.85, album_name=None, **kwargs)` → `bool`

将图片保存到系统照片库。

| 参数 | 说明 |
|------|------|
| `image` | `PIL.Image.Image` 或 `bytes`（原始图像文件数据）。其它类型会报错并返回 `False`。 |
| `format` | 字符串，`'JPEG'` 或 `'PNG'`（传入 `PIL.Image.save` 时使用 `format.upper()`）。 |
| `quality` | `0.0`–`1.0`，JPEG 时传给 Pillow 为 `int(quality * 100)`；同时作为 `float` 传给原生 `photos_save_image`。 |
| `album_name` | **忽略**，实际保存位置由系统决定（相当于写入「最近项目」类行为，与 Pythonista 兼容占位）。 |
| `**kwargs` | 忽略。 |

返回：原生层成功为 `True`，否则 `False`。

---

### `get_assets(media_type='photo', limit=0, **kwargs)` → `list[Asset]`

枚举照片库资源元数据列表。

| 参数 | 说明 |
|------|------|
| `media_type` | `'photo'`、`'video'` 或 `'all'`（传入原生 JSON API）。 |
| `limit` | `0` 表示不限制；否则为最大条数。 |
| `**kwargs` | 忽略。 |

失败或未初始化时返回 `[]`。底层：`photos_get_assets_json`，JSON 中 `assets` 数组逐项构造 `Asset`。

---

### `pick_asset(assets=None, title=None, multi=False, **kwargs)` → `Asset | None`

弹出资源选择器，选中后返回带元数据的 `Asset`。

| 参数 | 说明 |
|------|------|
| `assets`、`title`、`multi` | **忽略**（兼容 Pythonista）。 |
| `**kwargs` | 忽略。 |

取消或失败返回 `None`。底层：`photos_pick_asset_json()`，解析为单个资源字典后包装为 `Asset`。若 JSON 中含 `image_data_base64`，可供 `Asset.get_image` 使用。

---

### `get_image(asset, original=True)` → `PIL.Image | bytes | None`

模块级快捷方式：等价于在 `asset` 为 `Asset` 时调用 `asset.get_image(original=original)`（默认不传 `raw_data`，故一般为 `PIL.Image` 或 `None`）。非 `Asset` 返回 `None`。

---

## `Asset` 类

表示一条照片库资源，内部持有 `_info` 字典（来自 Swift 侧 JSON）。

### 只读属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `local_identifier` | `str` | 本地唯一标识，缺省 `''`。 |
| `media_type` | `int` | `0` 未知，`1` 图片，`2` 视频。 |
| `pixel_width` | `int` | 像素宽（JSON 键 `width`）。 |
| `pixel_height` | `int` | 像素高（JSON 键 `height`）。 |
| `creation_date` | 任意 / `None` | 创建时间戳（由 JSON `creation_date`）。 |
| `modification_date` | 任意 / `None` | 修改时间戳。 |
| `location` | `(lat, lon) \| None` | 当 `latitude` 与 `longitude` 均存在时为元组，否则 `None`。 |
| `duration` | `float` | 视频时长（秒）；图片一般为 `0`。 |
| `is_favorite` | `bool` | 是否标记为喜欢，缺省 `False`。 |

### 方法

#### `get_image(original=True, raw_data=False)` → `PIL.Image | bytes | None`

- 若 `_info` 中含 `image_data_base64`：先 Base64 解码为字节；`raw_data=True` 时直接返回 `bytes`；否则用 Pillow 打开为 `PIL.Image`。
- 若无嵌入图像数据：打印 `⚠️ [Asset.get_image] 图片数据不可用` 并返回 `None`（源码中标注 TODO：未实现按标识符重新拉取）。

`original` 参数为 API 兼容保留；当前实现**不区分**是否原始图。

#### `get_ui_image(original=True)` → `PIL.Image | bytes | None`

文档说明在 Python 中等价于返回 PIL 图像；实现上直接调用 `self.get_image(original=original)`，故返回值与 `get_image` 相同（非 UIKit 的 `UIImage` 对象）。

#### `__repr__`

形如 `<Asset: Image 1920×1080>`（媒体类型英文枚举字符串）。

---

## `AssetCollection` 类

表示相册、智能相册或「时刻」集合。

### 属性

| 属性 | 说明 |
|------|------|
| `title` | `str`，展示标题。 |
| `local_identifier` | `str`，标识符；构造时可为 `None`，内部回退为 `title`。 |
| `count` | `int`，资源数量（只读 property，底层 `_count`）。 |
| `collection_type` | `str`：`'album'`、`'smart_album'`、`'moment'` 等（由 JSON 的 `type` 字段填入）。 |

### 方法

#### `get_assets()` → `list[Asset]`

**当前实现恒返回 `[]`**，并打印 `⚠️ [AssetCollection.get_assets] 暂不支持`。预留与 Pythonista 一致的方法名，待原生层支持按相册拉取列表后可扩展。

#### `__repr__`

形如 `<AssetCollection: '相册名' (42 items)>`。

---

## 相册管理函数

### `get_albums()` → `list[AssetCollection]`

用户相册列表。JSON 键 `albums`，每项含 `title`、`identifier`、`count`、`type`。

### `get_smart_albums()` → `list[AssetCollection]`

系统智能相册。结构同上，`collection_type` 来自 JSON `type`。

### `get_moments()` → `list[AssetCollection]`

按时间/地点分组的「时刻」。JSON 键 `moments`，字段映射与相册类似。

### `create_album(title)` → `AssetCollection | None`

创建相册。成功时返回 `AssetCollection(title=..., identifier=..., count=0, collection_type='album')`，字段以 JSON 为准（`title`、`identifier`）。

### `get_screenshots_album()` → `AssetCollection | None`

截图智能相册；失败 `None`。默认标题占位 `'屏幕截图'`。

### `get_recently_added_album()` → `AssetCollection | None`

「最近添加」智能相册；标题占位 `'最近添加'`。

### `get_selfies_album()` → `AssetCollection | None`

自拍相册；标题占位 `'自拍'`。

上述函数在未初始化或异常时分别返回 `[]` 或 `None`，并可能打印以 `❌ [photos....]` 开头的错误信息。

---

## 便捷函数

### `pick_image_base64(format='JPEG', quality=0.85)` → `str | None`

内部 `pick_image(raw_data=True)` 取得字节；若 `format.upper()=='JPEG'` 且 Pillow 可用，则尝试用 PIL 打开并转码为 JPEG（`quality` 映射为 `int(quality * 100)`），失败则保留原始字节；最后返回 **标准 Base64 字符串**。取消返回 `None`。

### `capture_image_base64(format='JPEG', quality=0.85)` → `str | None`

依赖 `capture_image()`（**需要 PIL**）。将得到的 `PIL.Image` 按 `JPEG`/`PNG` 写入缓冲区后 Base64 编码。取消返回 `None`。

### `image_to_base64(image, format='JPEG', quality=0.85)` → `str`

`PIL.Image`：JPEG 会先 `convert('RGB')`；PNG 用 `format.upper()`。`bytes`：原样编码。其它类型抛出 `ValueError("Unsupported image type")`。

### `base64_to_image(b64_string)` → `PIL.Image | bytes`

解码后：有 Pillow 则 `Image.open(BytesIO(...))`，否则返回原始 `bytes`。

### `get_favorites()` → `list[Asset]`

对 `get_assets(media_type='photo', limit=0)` 全量结果过滤 `asset.is_favorite`。库很大时性能取决于原生返回规模。

### `get_count(media_type='photo')` → `int`

`len(get_assets(media_type=media_type, limit=0))`。异常时返回 `0`。

### `get_recent_images(count=10)` → `list[Asset]`

等价 `get_assets(media_type='photo', limit=count)`。

### `get_image_size(image)` → `tuple[int, int]`

若 `image` 为 `PIL.Image.Image`，返回 `image.size`（`(width, height)`）；否则返回 `(0, 0)`。**不**支持直接传入 `bytes`。

### `get_metadata(image)` → `dict`

仅当参数为 `PIL.Image.Image` 时，尝试 `image._getexif()`（Pillow 旧式 EXIF API）；有则转为普通 `dict`，否则 `{}`。无 EXIF 或异常时返回 `{}`。

### `is_available()` → `bool`

若 `_init_lib()` 成功得到非空库指针则 `True`，否则 `False`。导入模块时会执行一次 `_init_lib()`。

---

## 模块导出 `__all__`

`pick_image`, `capture_image`, `save_image`, `get_assets`, `pick_asset`, `get_image`, `Asset`, `AssetCollection`, `get_albums`, `get_smart_albums`, `get_moments`, `create_album`, `get_screenshots_album`, `get_recently_added_album`, `get_selfies_album`, `pick_image_base64`, `capture_image_base64`, `image_to_base64`, `base64_to_image`, `get_favorites`, `get_count`, `get_recent_images`, `get_image_size`, `get_metadata`, `is_available`。

---

## 完整示例

```python
import photos
from PIL import Image, ImageFilter

# 选择图片并应用滤镜
img = photos.pick_image()
if img:
    filtered = img.filter(ImageFilter.GaussianBlur(radius=5))
    photos.save_image(filtered)
    print(f"已保存 {img.size[0]}x{img.size[1]} 图片")

# 获取最近照片的元数据
assets = photos.get_recent_images(5)
for a in assets:
    print(f"{a.pixel_width}x{a.pixel_height} fav={a.is_favorite}")
```

### 无 Pillow 时读取原始字节

```python
import photos

data = photos.pick_image(raw_data=True)
if data:
    # 自行写入文件或上传
    open("picked.bin", "wb").write(data)
```

---

## 注意事项

1. **权限**：首次访问照片库或相机时，系统会弹出授权对话框；用户拒绝则相关调用可能失败或返回空/`None`。
2. **Pillow**：多数图像路径依赖内置 PIL/Pillow；`pick_image(raw_data=True)` 与 `base64_to_image` 可在无 PIL 时部分工作。
3. **阻塞**：`pick_image`、`capture_image`、`pick_asset` 等会阻塞当前 Python 线程，直到用户完成或取消界面操作。
4. **Pythonista 兼容**：大量参数仅接受以保持签名兼容，**不参与**本机实现逻辑。
5. **Asset 图像数据**：通过 `get_assets` 得到的 `Asset` 可能**没有**内嵌 `image_data_base64`，此时 `get_image` 会返回 `None`，需结合后续原生扩展或改用 `pick_asset` 等流程。
6. **`get_metadata`**：依赖 Pillow 的 `_getexif()`，不同版本/Pillow 2.x 行为可能略有差异；新代码可考虑在将来迁移到 `getexif()`。
7. **相册枚举与 `AssetCollection.get_assets`**：可列出相册元信息，但**按相册列出资源**尚未在 Python 层实现。
