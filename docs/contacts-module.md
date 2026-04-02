# contacts 模块 — iOS 通讯录、分组与系统联系人界面

面向 Pythonista `contacts` API 的兼容实现，用于在嵌入式 Python 环境中访问 iOS 通讯录、分组、容器，以及调用系统联系人选择器、详情页、编辑页、vCard 导入导出与变更历史。

底层通过主程序导出的 C 符号（`ctypes.CDLL(None)`）与 Swift `Contacts` / `ContactsUI` 层通信，在保留 `Person` / `Group` / `save()` / `revert()` 经典工作流的同时，补充了 Pythonista 原版没有的现代 iOS 能力。

实现文件：`pyboot/contacts.py`。

---

## 兼容性与边界

**已兼容的 Pythonista 风格能力：**

- `Person` / `Group`
- `get_all_people()` / `get_person()` / `find()`
- `add_person()` / `remove_person()`
- `get_all_groups()` / `get_group()` / `add_group()` / `remove_group()`
- `save()` / `revert()`
- `localized_label()`

**比 Pythonista 更强的增强能力：**

- 容器（`Container`）访问
- 系统联系人选择器和属性选择器
- 系统联系人详情页 / 编辑页 / 新建页
- `find_by_phone()` / `find_by_email()`
- vCard 导入导出
- 通讯录 change history 增量变更历史
- iOS 18+ limited contacts access 管理

**当前明确限制：**

- `get_me()` 目前返回 `None`，`capabilities()['supports_me_card']` 为 `False`
- `note` 字段接口存在，但当前 `capabilities()['supports_notes']` 为 `False`
- `creation_date` / `modification_date` 当前通常为 `None`

---

## 常量

### `PERSON = 0`

个人联系人。

### `ORGANIZATION = 1`

组织联系人。

---

## 权限与能力

### `authorization_status()` → `str`

返回当前通讯录权限状态：

- `'not_determined'`
- `'restricted'`
- `'denied'`
- `'authorized'`
- `'limited'`（仅 iOS 18+）

---

### `capabilities()` → `dict`

返回模块能力表。常见键包括：

| 键 | 说明 |
|------|------|
| `authorization_status` | 当前权限状态字符串。 |
| `supports_groups` | 是否支持分组。 |
| `supports_containers` | 是否支持容器。 |
| `supports_vcards` | 是否支持 vCard 导入导出。 |
| `supports_change_history` | 是否支持通讯录变更历史。 |
| `supports_me_card` | 当前为 `False`。 |
| `supports_notes` | 当前为 `False`。 |
| `supports_contact_picker_without_authorization` | 无需整库授权即可弹系统联系人选择器。 |
| `supports_contact_property_picker` | 是否支持属性级选择器。 |
| `supports_contact_view_controller` | 是否支持系统联系人详情页。 |
| `supports_contact_editor` | 是否支持系统联系人编辑页。 |
| `supports_contact_creator` | 是否支持系统新建联系人页。 |
| `supports_limited_access` | iOS 18+ 时为 `True`。 |

---

### `is_authorized()` → `bool`

若当前状态可读取通讯录，返回 `True`。

在 iOS 18+ 上，`limited` 也会视为可读。

---

### `request_access()` → `bool`

请求通讯录权限。

- 成功授权：返回 `True`
- 用户拒绝：返回 `False`

---

### `localized_label(label)` → `str`

将原生 label（例如 `_$!<Mobile>!$_`）本地化为系统展示字符串。

---

## 联系人读取与搜索

### `get_all_people(limit=0, offset=0, container=None)` → `list[Person]`

读取联系人列表。

| 参数 | 说明 |
|------|------|
| `limit` | `0` 表示不限制。 |
| `offset` | 偏移量，用于分页。 |
| `container` | `Container` 对象、容器 `identifier`，或 `None`。 |

---

### `get_person(person_or_id, include_image_data=False, include_vcard=False)` → `Person | None`

按联系人引用读取单个联系人。

`person_or_id` 可为：

- `Person`
- 兼容整数 `id`
- 原生字符串 `identifier`

`include_image_data=True` 或 `include_vcard=True` 时，会在原生层一并取回附加数据。

---

### `get_me()` → `Person | None`

当前实现返回 `None`。iOS 公共 Contacts API 未提供稳定的 My Card 读取能力。

---

### `find(name)` → `list[Person]`

按姓名搜索联系人。

实现上会优先返回更接近 Pythonista 行为的前缀匹配结果；若没有前缀命中，则回退到系统搜索结果。

---

### `find_by_phone(phone)` → `list[Person]`

按手机号搜索联系人。

---

### `find_by_email(email)` → `list[Person]`

按邮箱地址搜索联系人。

---

## 写入事务

### `add_person(person=None)` → `Person`

将联系人加入待保存队列。

- `person is None`：创建一个新的空联系人
- 传入现有未保存 `Person`：直接加入事务

---

### `remove_person(person)` → `None`

将联系人标记为待删除。

若该联系人本轮事务中刚创建但尚未 `save()`，则会直接从待保存队列移除。

---

### `save()` → `bool`

提交当前所有待处理事务。

一次 `save()` 中会合并：

- 新建联系人
- 更新联系人
- 删除联系人
- 新建分组
- 更新分组
- 删除分组
- 分组成员增删

支持在**同一轮 `save()`** 中：

- 新建联系人
- 新建分组
- 再把这个新联系人加入这个新分组

提交成功返回 `True`。

---

### `revert()` → `None`

丢弃所有未保存改动，并将已跟踪的 `Person` / `Group` 对象恢复到保存前快照。

---

## 分组与容器

### `get_all_groups(container=None)` → `list[Group]`

读取所有分组。

`container` 可为：

- `Container`
- 容器 `identifier`
- `None`

---

### `get_group(group_or_id)` → `Group | None`

按 `Group` / 兼容 `id` / 原生 `identifier` 读取单个分组。

---

### `add_group(group=None)` → `Group`

新建分组或将分组加入待保存队列。

支持：

- `add_group()`
- `add_group("客户")`
- `add_group(existing_group)`

---

### `remove_group(group)` → `None`

将分组标记为待删除。

---

### `get_all_containers()` → `list[Container]`

读取所有容器，例如本地、iCloud、Exchange、CardDAV 等来源。

---

### `get_default_container()` → `Container | None`

读取默认容器。

---

### `get_people_in_group(group)` → `list[Person]`

读取某个分组下的所有联系人。

---

### `get_people_in_container(container)` → `list[Person]`

读取某个容器下的联系人。

---

### `get_groups_in_container(container)` → `list[Group]`

读取某个容器下的分组。

---

## 系统 UI 能力

### `pick_contact(multi=False)` → `Person | list[Person] | None`

弹出系统联系人选择器。

| 行为 | 说明 |
|------|------|
| `multi=False` | 返回单个 `Person` 或 `None`。 |
| `multi=True` | 返回 `list[Person]`；取消时返回 `[]`。 |

该选择器支持在没有整本通讯录读取权限时工作。

---

### `pick_contacts()` → `list[Person]`

等价于 `pick_contact(multi=True)`。

---

### `pick_property(kind='phone', multi=False)` → `PropertySelection | list[PropertySelection] | None`

弹出系统联系人属性选择器。

支持的 `kind`：

- `'phone'`
- `'email'`
- `'address'` / `'postal'`
- `'url'`
- `'relation'` / `'related_name'` / `'related_names'`
- `'social'` / `'social_profile'`
- `'im'` / `'instant_message'`

| 行为 | 说明 |
|------|------|
| `multi=False` | 返回单个 `PropertySelection` 或 `None`。 |
| `multi=True` | 返回 `list[PropertySelection]`；取消时返回 `[]`。 |

---

### `show_person(person, allows_editing=True, allows_actions=True, displayed_property_keys=None, property_key=None, property_identifier=None, should_show_linked_contacts=False)` → `Person | None`

打开系统联系人详情页。

可用于：

- 展示联系人卡片
- 高亮某个属性
- 限制显示的属性字段

若传入的是尚未保存的新 `Person`，会自动走新建联系人流程。

---

### `edit_person(person, **kwargs)` → `Person | None`

打开系统联系人编辑页。

常见可选参数：

- `allows_actions=True`
- `displayed_property_keys=None`
- `should_show_linked_contacts=False`

保存后返回更新后的 `Person`；取消时返回 `None`。

---

### `new_person(seed=None, container=None, group=None)` → `Person | None`

打开系统新建联系人页。

| 参数 | 说明 |
|------|------|
| `seed` | `Person`、`dict` 或 `None`，用于预填字段。 |
| `container` | 指定目标容器。 |
| `group` | 指定新建后加入的分组。 |

---

## vCard 与变更历史

### `export_vcards(people)` → `bytes | None`

将联系人导出为 vCard 二进制数据。

`people` 中每一项可为：

- `Person`
- 兼容整数 `id`
- 原生字符串 `identifier`

---

### `import_vcards(data, container=None)` → `list[Person]`

导入 vCard。

`data` 支持：

- `bytes`
- `bytearray`
- 文件路径字符串

成功时返回导入后的 `Person` 列表。

---

### `get_change_history(token=None, include_group_changes=True, excluded_transaction_authors=None)` → `dict`

读取通讯录变更历史。

返回结构：

| 键 | 说明 |
|------|------|
| `events` | 变更事件数组。 |
| `token` | 下一次增量读取所需的二进制 token；无值时为 `None`。 |

`token` 参数可传入：

- 上次返回的 `bytes`
- Base64 字符串

常见事件类型：

- `drop_everything`
- `add_contact`
- `update_contact`
- `delete_contact`
- `add_group`
- `update_group`
- `delete_group`
- `add_member_to_group`
- `remove_member_from_group`
- `add_subgroup_to_group`
- `remove_subgroup_from_group`

可选参数：

- `include_group_changes=True`
- `excluded_transaction_authors=['pythonide.contacts']`

---

### `manage_limited_access()` → `list[str]`

在 iOS 18+ 上打开 limited contacts access 管理界面，返回用户新选择的联系人 `identifier` 列表。

不支持的系统版本上会报错或无效，应先检查 `capabilities()['supports_limited_access']`。

---

## `Person` 类

`Person` 表示联系人对象。可直接读写字段，修改只会写入内存，需调用 `save()` 才会真正提交到系统通讯录。

### 标识与类型

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | `int` | Pythonista 兼容别名。 |
| `identifier` | `str | None` | iOS 原生联系人标识。 |
| `kind` | `int` | `PERSON` 或 `ORGANIZATION`。 |
| `contact_type` | `str` | `'person'` 或 `'organization'`。 |
| `deleted` | `bool` | 是否已标记删除。 |

### 姓名与组织字段

| 属性 |
|------|
| `prefix` |
| `first_name` |
| `middle_name` |
| `last_name` |
| `previous_last_name` |
| `suffix` |
| `nickname` |
| `organization` |
| `department` |
| `job_title` |
| `phonetic_first_name` |
| `phonetic_middle_name` |
| `phonetic_last_name` |
| `phonetic_organization` |
| `full_name` |

`full_name` 为模块维护的展示名称；优先使用原生格式化结果。

### 多值字段格式

#### `phone`

```python
[
    ('mobile', '13800138000'),
    ('work', '010-12345678'),
]
```

#### `email`

```python
[
    ('home', 'alice@example.com'),
    ('work', 'alice@company.com'),
]
```

#### `address`

```python
[
    ('home', {
        'street': '中山路 1 号',
        'city': '上海',
        'state': '上海',
        'zip': '200000',
        'country': '中国',
        'country_code': 'CN',
    })
]
```

#### `url`

```python
[
    ('homepage', 'https://example.com')
]
```

#### `related_names`

```python
[
    ('spouse', 'Alice'),
    ('manager', 'Bob'),
]
```

#### `social_profile`

```python
[
    ('social', {
        'service': 'Twitter',
        'username': 'alice',
        'user_identifier': '123456',
        'url': 'https://x.com/alice',
    })
]
```

#### `instant_message`

```python
[
    ('qq', {
        'username': '12345678',
        'service': 'QQ',
    })
]
```

#### `dates`

```python
[
    ('anniversary', {
        'year': 2024,
        'month': 10,
        'day': 1,
    })
]
```

### 日期字段

| 属性 | 说明 |
|------|------|
| `birthday` | `dict | None`，如 `{'year': 1990, 'month': 8, 'day': 12}` |
| `non_gregorian_birthday` | 非公历生日 `dict | None` |
| `dates` | 多值日期字段列表 |
| `creation_date` | 当前通常为 `None` |
| `modification_date` | 当前通常为 `None` |

日期字典可能包含：

- `era`
- `year`
- `month`
- `day`
- `hour`
- `minute`
- `second`
- `is_leap_month`
- `calendar_identifier`
- `time_zone`

### 图片与 vCard

| 属性 | 类型 | 说明 |
|------|------|------|
| `has_image` | `bool` | 是否有头像。 |
| `image_data_available` | `bool` | 当前是否可读取头像数据。 |
| `image_data` | `bytes | None` | 原图数据，懒加载，可写入。 |
| `thumbnail_image_data` | `bytes | None` | 缩略图数据，懒加载，只读。 |
| `vcard` | `bytes | None` | vCard 数据，懒加载，只读。 |

### 其他字段

| 属性 | 说明 |
|------|------|
| `note` | 当前 capability 为关闭状态，不应依赖。 |

---

## `Group` 类

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | `int` | Pythonista 兼容别名。 |
| `identifier` | `str | None` | iOS 原生分组标识。 |
| `name` | `str` | 分组名。 |
| `container_identifier` | `str | None` | 所属容器。 |

### 方法

#### `members()` → `list[Person]`

返回分组内联系人。

#### `add_member(person)` → `None`

将联系人加入分组待保存队列。

#### `remove_member(person)` → `None`

将联系人从分组移除；需要后续 `save()`。

---

## `Container` 类

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `identifier` | `str` | 容器标识。 |
| `name` | `str` | 容器显示名。 |
| `type` | `str` | 容器类型，如 `local`、`exchange`、`carddav` 等。 |
| `is_default` | `bool` | 是否默认容器。 |

### 方法

#### `people()` → `list[Person]`

返回该容器下联系人。

#### `groups()` → `list[Group]`

返回该容器下分组。

---

## `PropertySelection` 类

表示属性选择器返回的一条结果。

### 属性

| 属性 | 说明 |
|------|------|
| `contact` | 对应 `Person`，可能为 `None` |
| `contact_identifier` | 联系人 `identifier` |
| `property_identifier` | 属性标识 |
| `key` | 原生属性 key，例如电话、邮箱、地址 |
| `label` | 原始 label |
| `localized_label` | 本地化 label |
| `value` | 该属性的值 |

---

## 完整示例

```python
import contacts

print('能力表:', contacts.capabilities())

if not contacts.is_authorized():
    granted = contacts.request_access()
    print('授权结果:', granted)

people = contacts.get_all_people(limit=20)
print('联系人数量:', len(people))

for person in people[:3]:
    print(person.full_name, person.phone)

hits = contacts.find('张')
print('姓名搜索命中:', [p.full_name for p in hits[:5]])

phone_hits = contacts.find_by_phone('13800138000')
print('手机号命中:', [p.full_name for p in phone_hits])

group = contacts.add_group('测试客户')
person = contacts.add_person()
person.first_name = '测试'
person.last_name = '联系人'
person.phone = [('mobile', '13800138000')]
group.add_member(person)
contacts.save()

print('新联系人 ID:', person.id, person.identifier)
print('新分组 ID:', group.id, group.identifier)

vcf = contacts.export_vcards([person])
print('vCard 字节数:', len(vcf or b''))

history = contacts.get_change_history()
print('change history events:', len(history['events']))

# 清理测试数据
contacts.remove_person(person)
contacts.remove_group(group)
contacts.save()
```

---

## 建议用法

- 读整本通讯录前先检查 `authorization_status()` / `is_authorized()`
- 只想让用户选一个手机号或邮箱时，优先用 `pick_property()`，无需整库读取
- 批量改动统一走 `save()`，不要每改一个字段就提交一次
- 对头像、vCard 等大字段按需访问，避免无意义读取
- 对 `note`、`get_me()`、`creation_date`、`modification_date` 等边界能力先看 `capabilities()`
