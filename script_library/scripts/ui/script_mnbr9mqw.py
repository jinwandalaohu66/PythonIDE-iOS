import ui
import sound
import console

# 内置音效分类和示例音效
AUDIO_CATEGORIES = {
    "游戏音效 (game)": [
        "game:Beep", "game:Hit_1", "game:Hit_2", "game:Hit_3", "game:Powerup",
        "game:Error", "game:Coin_1", "game:Coin_2", "game:Coin_3", "game:Jump_1",
        "game:Jump_2", "game:Explosion_1", "game:Explosion_2", "game:Explosion_3",
        "game:Laser_1", "game:Laser_2", "game:Laser_3", "game:Shoot_1", "game:Shoot_2",
        "game:Shoot_3", "game:Select_1", "game:Select_2", "game:Select_3"
    ],
    "街机音效 (arcade)": [
        "arcade:Coin_1", "arcade:Coin_2", "arcade:Coin_3", "arcade:Jump_1",
        "arcade:Jump_2", "arcade:Explosion_1", "arcade:Explosion_2", "arcade:Explosion_3",
        "arcade:Laser_1", "arcade:Laser_2", "arcade:Laser_3", "arcade:Shoot_1",
        "arcade:Shoot_2", "arcade:Shoot_3", "arcade:Select_1", "arcade:Select_2",
        "arcade:Select_3", "arcade:Powerup_1", "arcade:Powerup_2", "arcade:Powerup_3"
    ],
    "UI 音效 (ui)": [
        "ui:click1", "ui:click2", "ui:click3", "ui:click4", "ui:click5",
        "ui:pop1", "ui:pop2", "ui:pop3", "ui:pop4", "ui:pop5",
        "ui:alert1", "ui:alert2", "ui:alert3", "ui:alert4", "ui:alert5",
        "ui:success1", "ui:success2", "ui:success3", "ui:success4", "ui:success5"
    ],
    "数字音效 (digital)": [
        "digital:beep1", "digital:beep2", "digital:beep3", "digital:beep4", "digital:beep5",
        "digital:error1", "digital:error2", "digital:error3", "digital:error4", "digital:error5",
        "digital:success1", "digital:success2", "digital:success3", "digital:success4", "digital:success5"
    ],
    "赌场音效 (casino)": [
        "casino:chip1", "casino:chip2", "casino:chip3", "casino:chip4", "casino:chip5",
        "casino:coin1", "casino:coin2", "casino:coin3", "casino:coin4", "casino:coin5",
        "casino:slot1", "casino:slot2", "casino:slot3", "casino:slot4", "casino:slot5"
    ],
    "RPG 音效 (rpg)": [
        "rpg:DoorOpen_1", "rpg:DoorClose_1", "rpg:Footstep_1", "rpg:Footstep_2", "rpg:Footstep_3",
        "rpg:SwordSwing_1", "rpg:SwordSwing_2", "rpg:SwordSwing_3", "rpg:KnifeSlice_1", "rpg:KnifeSlice_2",
        "rpg:MagicSpell_1", "rpg:MagicSpell_2", "rpg:MagicSpell_3", "rpg:MagicSpell_4", "rpg:MagicSpell_5"
    ],
    "音乐音效 (music)": [
        "music:Victory_NES_1", "music:Victory_NES_2", "music:Victory_NES_3", "music:GameOver_NES_1",
        "music:GameOver_NES_2", "music:GameOver_NES_3", "music:LevelUp_NES_1", "music:LevelUp_NES_2",
        "music:LevelUp_NES_3", "music:Intro_NES_1", "music:Intro_NES_2", "music:Intro_NES_3"
    ]
}

class AudioTester:
    def __init__(self):
        self.current_sound = None
        self.current_volume = 0.5
        self.current_pitch = 1.0
        self.current_pan = 0.0
        
        # 创建主视图
        self.view = ui.View(frame=(0, 0, 400, 700))
        self.view.name = '音频测试器'
        self.view.background_color = '#f5f5f5'
        
        # 标题
        title_label = ui.Label(frame=(20, 20, 360, 40))
        title_label.text = '🎵 内置音频测试器'
        title_label.font = ('System-Bold', 24)
        title_label.alignment = ui.ALIGN_CENTER
        title_label.text_color = '#333'
        title_label.flex = 'W'
        self.view.add_subview(title_label)
        
        # 统计标签
        total_sounds = sum(len(sounds) for sounds in AUDIO_CATEGORIES.values())
        stats_label = ui.Label(frame=(20, 70, 360, 20))
        stats_label.text = f'共 {total_sounds} 个内置音效，7 大分类'
        stats_label.font = ('System', 14)
        stats_label.alignment = ui.ALIGN_CENTER
        stats_label.text_color = '#666'
        stats_label.flex = 'W'
        self.view.add_subview(stats_label)
        
        # 控制面板
        control_view = ui.View(frame=(20, 100, 360, 120))
        control_view.background_color = '#ffffff'
        control_view.corner_radius = 10
        control_view.border_width = 1
        control_view.border_color = '#e0e0e0'
        control_view.flex = 'W'
        self.view.add_subview(control_view)
        
        # 音量控制
        volume_label = ui.Label(frame=(20, 15, 80, 30))
        volume_label.text = '音量:'
        volume_label.font = ('System', 14)
        control_view.add_subview(volume_label)
        
        self.volume_slider = ui.Slider(frame=(100, 15, 200, 30))
        self.volume_slider.value = self.current_volume
        self.volume_slider.continuous = True
        self.volume_slider.action = self.volume_changed
        control_view.add_subview(self.volume_slider)
        
        self.volume_value_label = ui.Label(frame=(310, 15, 40, 30))
        self.volume_value_label.text = f'{int(self.current_volume * 100)}%'
        self.volume_value_label.font = ('System', 14)
        self.volume_value_label.alignment = ui.ALIGN_RIGHT
        control_view.add_subview(self.volume_value_label)
        
        # 音高控制
        pitch_label = ui.Label(frame=(20, 55, 80, 30))
        pitch_label.text = '音高:'
        pitch_label.font = ('System', 14)
        control_view.add_subview(pitch_label)
        
        self.pitch_slider = ui.Slider(frame=(100, 55, 200, 30))
        self.pitch_slider.value = 0.5  # 映射到 0.5-2.0
        self.pitch_slider.continuous = True
        self.pitch_slider.action = self.pitch_changed
        control_view.add_subview(self.pitch_slider)
        
        self.pitch_value_label = ui.Label(frame=(310, 55, 40, 30))
        self.pitch_value_label.text = f'{self.current_pitch:.1f}x'
        self.pitch_value_label.font = ('System', 14)
        self.pitch_value_label.alignment = ui.ALIGN_RIGHT
        control_view.add_subview(self.pitch_value_label)
        
        # 声像控制
        pan_label = ui.Label(frame=(20, 95, 80, 30))
        pan_label.text = '声像:'
        pan_label.font = ('System', 14)
        control_view.add_subview(pan_label)
        
        self.pan_slider = ui.Slider(frame=(100, 95, 200, 30))
        self.pan_slider.value = 0.5  # 映射到 -1.0到1.0
        self.pan_slider.continuous = True
        self.pan_slider.action = self.pan_changed
        control_view.add_subview(self.pan_slider)
        
        self.pan_value_label = ui.Label(frame=(310, 95, 40, 30))
        self.pan_value_label.text = f'{self.current_pan:.1f}'
        self.pan_value_label.font = ('System', 14)
        self.pan_value_label.alignment = ui.ALIGN_RIGHT
        control_view.add_subview(self.pan_value_label)
        
        # 控制按钮
        button_y = 230
        self.play_button = ui.Button(frame=(20, button_y, 160, 44))
        self.play_button.title = '▶️ 播放选中音效'
        self.play_button.background_color = '#4CAF50'
        self.play_button.title_color = 'white'
        self.play_button.corner_radius = 8
        self.play_button.action = self.play_sound
        self.play_button.flex = 'LRTB'
        self.view.add_subview(self.play_button)
        
        self.stop_button = ui.Button(frame=(200, button_y, 160, 44))
        self.stop_button.title = '⏹️ 停止所有音效'
        self.stop_button.background_color = '#F44336'
        self.stop_button.title_color = 'white'
        self.stop_button.corner_radius = 8
        self.stop_button.action = self.stop_all_sounds
        self.stop_button.flex = 'LRTB'
        self.view.add_subview(self.stop_button)
        
        # 当前播放标签
        self.current_label = ui.Label(frame=(20, 290, 360, 30))
        self.current_label.text = '当前播放: 无'
        self.current_label.font = ('System', 14)
        self.current_label.text_color = '#666'
        self.current_label.flex = 'W'
        self.view.add_subview(self.current_label)
        
        # 创建分段控件用于切换分类
        self.segmented_control = ui.SegmentedControl(frame=(20, 330, 360, 32))
        self.segmented_control.segments = list(AUDIO_CATEGORIES.keys())
        self.segmented_control.selected_index = 0
        self.segmented_control.action = self.category_changed
        self.segmented_control.flex = 'W'
        self.view.add_subview(self.segmented_control)
        
        # 创建表格视图显示音效列表
        self.table_view = ui.TableView(frame=(20, 380, 360, 280))
        self.table_view.row_height = 44
        self.table_view.flex = 'WH'
        self.table_view.corner_radius = 8
        self.table_view.border_width = 1
        self.table_view.border_color = '#e0e0e0'
        self.table_view.delegate = self
        self.view.add_subview(self.table_view)
        
        # 初始化数据
        self.current_category = list(AUDIO_CATEGORIES.keys())[0]
        self.current_sounds = AUDIO_CATEGORIES[self.current_category]
        self.selected_sound = None
        
        # 设置 TableView 数据源
        self.update_table_data()
        
    def volume_changed(self, sender):
        self.current_volume = sender.value
        self.volume_value_label.text = f'{int(self.current_volume * 100)}%'
        
    def pitch_changed(self, sender):
        # 将 0-1 映射到 0.5-2.0
        self.current_pitch = 0.5 + sender.value * 1.5
        self.pitch_value_label.text = f'{self.current_pitch:.1f}x'
        
    def pan_changed(self, sender):
        # 将 0-1 映射到 -1.0到1.0
        self.current_pan = (sender.value - 0.5) * 2
        self.pan_value_label.text = f'{self.current_pan:.1f}'
        
    def category_changed(self, sender):
        self.current_category = sender.segments[sender.selected_index]
        self.current_sounds = AUDIO_CATEGORIES[self.current_category]
        self.update_table_data()
        self.selected_sound = None
        self.current_label.text = '当前播放: 无'
        
    def update_table_data(self):
        # 将音效列表转换为 TableView 可用的数据格式
        table_data = []
        for sound_name in self.current_sounds:
            table_data.append({
                'title': sound_name,
                'accessory_type': 'disclosure_indicator'
            })
        self.table_view.data_source = table_data
        self.table_view.reload_data()
        
    def play_sound(self, sender):
        if self.selected_sound:
            try:
                # 播放音效
                self.current_sound = sound.play_effect(
                    self.selected_sound,
                    volume=self.current_volume,
                    pitch=self.current_pitch,
                    pan=self.current_pan
                )
                self.current_label.text = f'当前播放: {self.selected_sound}'
                console.hud_alert(f'播放: {self.selected_sound}', duration=1.0)
            except Exception as e:
                console.hud_alert(f'播放失败: {str(e)}', duration=2.0)
        else:
            console.hud_alert('请先选择一个音效', duration=1.5)
            
    def stop_all_sounds(self, sender):
        sound.stop_all_effects()
        self.current_label.text = '当前播放: 已停止'
        console.hud_alert('已停止所有音效', duration=1.0)
        
    def tableview_did_select(self, tableview, section, row):
        self.selected_sound = self.current_sounds[row]
        self.current_label.text = f'已选择: {self.selected_sound}'
        # 自动播放选中的音效
        self.play_sound(None)
        

        
    def run(self):
        self.view.present('sheet')

# 创建并运行音频测试器
if __name__ == '__main__':
    tester = AudioTester()
    tester.run()