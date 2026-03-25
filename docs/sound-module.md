# sound 模块 — 完整 API 参考

> Pythonista 兼容音频播放模块，基于 AVAudioPlayer 后端。  
> 支持短音效、长音频/音乐播放、音量/音高/声像控制、循环、静音开关。

---

## 目录

- [快速开始](#快速开始)
- [音效播放](#音效播放)
  - [play_effect()](#play_effect)
  - [stop_effect()](#stop_effect)
  - [stop_all_effects()](#stop_all_effects)
- [Player 类](#player-类)
- [MIDIPlayer 类](#midiplayer-类)
- [全局设置](#全局设置)
  - [set_volume()](#set_volume)
  - [get_volume()](#get_volume)
  - [set_honors_silent_switch()](#set_honors_silent_switch)
- [音效文件名规则](#音效文件名规则)
- [游戏中使用 sound](#游戏中使用-sound)
- [完整示例](#完整示例)

---

## 快速开始

```python
import sound

# 播放一个短音效
sound.play_effect('game:Beep')

# 播放背景音乐（循环）
bgm = sound.Player('background.mp3')
bgm.number_of_loops = -1
bgm.play()
```

---

## 音效播放

### play_effect()

```python
sound.play_effect(name, volume=1.0, pitch=1.0, pan=0.0, looping=False)
```

播放短音效，立即返回一个 handle，可用于稍后停止。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `name` | str | 必填 | 音频文件名或 Pythonista 风格名（如 `'game:Beep'`） |
| `volume` | float | 1.0 | 音量 0.0–1.0 |
| `pitch` | float | 1.0 | 播放速率倍数 0.5–2.0（影响音高和速度） |
| `pan` | float | 0.0 | 声像：-1.0 最左，0.0 居中，1.0 最右 |
| `looping` | bool | False | 是否循环播放 |

**返回值**：`EffectHandle` 对象（传给 `stop_effect()`），失败返回 `None`。

```python
handle = sound.play_effect('arcade:Coin_1', volume=0.5)
```

### stop_effect()

```python
sound.stop_effect(effect_handle)
```

停止指定的音效。

| 参数 | 类型 | 说明 |
|------|------|------|
| `effect_handle` | EffectHandle | `play_effect()` 返回的 handle |

```python
h = sound.play_effect('game:Beep', looping=True)
# ... 稍后
sound.stop_effect(h)
```

### stop_all_effects()

```python
sound.stop_all_effects()
```

停止所有正在播放的音效。

---

## Player 类

用于播放较长的音频文件（音乐、播客等），支持完整播放控制。

### 创建

```python
p = sound.Player('music.mp3')
```

### 方法

| 方法 | 说明 |
|------|------|
| `p.play()` | 开始或恢复播放 |
| `p.pause()` | 暂停（可用 `play()` 恢复） |
| `p.stop()` | 停止并重置到开头 |

### 属性

| 属性 | 类型 | 读/写 | 说明 |
|------|------|-------|------|
| `playing` | bool | 只读 | 是否正在播放 |
| `duration` | float | 只读 | 总时长（秒） |
| `current_time` | float | 读写 | 当前播放位置（秒） |
| `volume` | float | 读写 | 播放音量 0.0–1.0 |
| `rate` | float | 读写 | 播放速率 0.5–2.0（1.0 为正常速度） |
| `number_of_loops` | int | 读写 | 循环次数：0=不循环，-1=无限，N=循环 N 次 |
| `file_path` | str | 只读 | 文件路径 |

```python
import sound

p = sound.Player('epic_music.mp3')
p.volume = 0.7
p.number_of_loops = -1  # 无限循环
p.play()

print(f'时长: {p.duration:.1f}秒')
print(f'当前: {p.current_time:.1f}秒')

p.current_time = 30.0  # 跳到 30 秒
p.rate = 1.5           # 1.5 倍速
p.pause()
p.play()               # 恢复
p.stop()               # 停止并回到开头
```

---

## MIDIPlayer 类

MIDI 播放器兼容占位。iOS 无原生简单 MIDI API，接口保留以兼容 Pythonista。

```python
mp = sound.MIDIPlayer('song.mid')
mp.play()
mp.stop()
mp.playing  # bool
```

---

## 全局设置

### set_volume()

```python
sound.set_volume(volume)
```

设置全局主音量（0.0–1.0），影响所有音效和 Player。

### get_volume()

```python
vol = sound.get_volume()  # → float
```

获取当前全局主音量。

### set_honors_silent_switch()

```python
sound.set_honors_silent_switch(flag)
```

| 参数 | 行为 |
|------|------|
| `True`（默认） | 静音开关打开时静音 |
| `False` | 忽略静音开关，始终播放 |

---

## 音效文件名规则

`play_effect()` 和 `Player()` 支持多种文件名格式，按以下优先级解析：

| 格式 | 示例 | 说明 |
|------|------|------|
| 绝对路径 | `/var/.../.../sound.wav` | 直接使用 |
| Pythonista 风格 | `'game:Beep'` | 在 Bundle `Sounds/<category>/` 中查找 |
| Bundle 文件名 | `'click.caf'` | 在 app bundle 中查找 |
| 相对路径 | `'sounds/bgm.mp3'` | 先找当前目录，再找 Documents |

**内置 149 个音效（CC0 来源 Kenney.nl），7 大分类**：

| 分类 | 数量 | 完整列表 |
|------|------|------|
| `game:` | 34 | `Beep` `Error` `Error_2` `Error_3` `Powerup` `Ding_1`~`Ding_3` `Clock_1`~`Clock_3` `Hit_1`~`Hit_4` `Drop_1` `Drop_2` `Pluck_1` `Pluck_2` `Glass_1` `Glass_2` `Swoosh_1`~`Swoosh_3` `Open_1` `Open_2` `Close_1` `Close_2` `Select_1` `Select_2` `Glitch_1` `Glitch_2` `Question_1` `Scratch_1` |
| `arcade:` | 13 | `Coin_1` `Coin_2` `Jump_1`~`Jump_3` `Explosion_1`~`Explosion_3` `Laser_1`~`Laser_3` `Zap_1` `Zap_2` |
| `ui:` | 12 | `click1`~`click5` `switch1`~`switch3` `rollover1` `rollover2` `mouseclick1` `mouserelease1` |
| `digital:` | 34 | `PowerUp1`~`PowerUp12` `Laser1`~`Laser9` `Zap1` `Zap2` `HighUp` `HighDown` `LowDown` `LowRandom` `PepSound1` `PepSound2` `Tone1` `TwoTone1` `TwoTone2` `ThreeTone1` `ThreeTone2` |
| `casino:` | 15 | `DiceThrow1`~`DiceThrow3` `DiceShake1` `DiceShake2` `CardPlace1` `CardPlace2` `CardSlide1` `CardSlide2` `CardShuffle` `ChipsCollide1` `ChipsCollide2` `ChipsHandle1` `ChipLay1` `ChipLay2` |
| `rpg:` | 25 | `DoorOpen_1` `DoorOpen_2` `DoorClose_1` `DoorClose_2` `BookOpen` `BookClose` `BookFlip_1` `BookFlip_2` `Chop` `KnifeSlice_1` `KnifeSlice_2` `DrawKnife_1` `MetalClick` `MetalLatch` `Creak_1` `Creak_2` `Cloth_1` `DropLeather` `Footstep_1`~`Footstep_3` `FootstepGrass_1` `FootstepGrass_2` `FootstepWood_1` `FootstepWood_2` |
| `music:` | 16 | `Victory_NES_1` `Victory_NES_2` `GameOver_NES_1` `LevelUp_NES_1` `Start_NES_1` `Bonus_NES_1` `Victory_Pizzi_1` `GameOver_Pizzi_1` `LevelUp_Pizzi_1` `Victory_Steel_1` `GameOver_Steel_1` `LevelUp_Steel_1` `Victory_Sax_1` `GameOver_Sax_1` `Victory_Hit_1` `GameOver_Hit_1` |

**支持的音频格式**：`.caf` `.wav` `.mp3` `.aiff` `.m4a`

---

## 游戏中使用 sound

每个游戏都应添加音效以提升体验。推荐在以下场景使用：

| 场景 | 建议 |
|------|------|
| 碰撞/反弹 | `sound.play_effect('game:Hit_1', volume=0.3)` |
| 得分 | `sound.play_effect('arcade:Coin_1')` |
| 玩家点击 | `sound.play_effect('ui:click1', volume=0.5)` |
| 升级/奖励 | `sound.play_effect('game:Powerup')` |
| 失败/错误 | `sound.play_effect('game:Error')` |
| 跳跃 | `sound.play_effect('arcade:Jump_1')` |
| 爆炸 | `sound.play_effect('arcade:Explosion_1')` |
| 挥动/呼啸 | `sound.play_effect('game:Swoosh_1')` |
| 胜利过关 | `sound.play_effect('music:Victory_NES_1')` |
| 游戏结束 | `sound.play_effect('music:GameOver_NES_1')` |
| 开门 | `sound.play_effect('rpg:DoorOpen_1')` |
| 脚步声 | `sound.play_effect('rpg:Footstep_1')` |
| 背景音乐 | `bgm = sound.Player('music.mp3'); bgm.number_of_loops = -1; bgm.play()` |

---

## 完整示例

### 带音效的 scene 游戏

```python
from scene import *
import sound

class MyGame(Scene):
    def setup(self):
        w, h = self.size.w, self.size.h
        self.bg = SpriteNode(color='#1a1a2e', size=(w, h),
                             position=(w/2, h/2), parent=self)
        self.ball = SpriteNode(color='#e94560', size=(40, 40),
                               position=(w/2, h/2), parent=self)
        self.ball.z_position = 1
        self.vx, self.vy = 200, 250
        self.score = 0
        self.label = LabelNode('0', font=('Menlo-Bold', 36),
                               position=(w/2, h - 60), parent=self)
        self.label.z_position = 2

    def update(self):
        dt = self.dt
        w, h = self.size.w, self.size.h
        r = 20
        bx = self.ball.position.x + self.vx * dt
        by = self.ball.position.y + self.vy * dt
        bounced = False
        if bx - r < 0:
            bx = r; self.vx = abs(self.vx); bounced = True
        elif bx + r > w:
            bx = w - r; self.vx = -abs(self.vx); bounced = True
        if by - r < 0:
            by = r; self.vy = abs(self.vy); bounced = True
        elif by + r > h:
            by = h - r; self.vy = -abs(self.vy); bounced = True
        if bounced:
            self.score += 1
            sound.play_effect('game:Beep', volume=0.3)
        self.ball.position = (bx, by)
        self.label.text = str(self.score)

    def touch_began(self, touch):
        sound.play_effect('ui:click1', volume=0.5)

run(MyGame(), _mode='main')
```

### 音乐播放器

```python
import sound
import console

p = sound.Player('favorite_song.mp3')
p.volume = 0.8

console.hud_alert('开始播放 🎵')
p.play()

import time
while p.playing:
    pct = p.current_time / p.duration * 100
    print(f'\r进度: {pct:.0f}%', end='')
    time.sleep(1)

console.hud_alert('播放结束')
```
