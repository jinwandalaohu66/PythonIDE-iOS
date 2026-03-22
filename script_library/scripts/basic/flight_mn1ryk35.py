import random
import time
words = {
    "prep": ['在', '于', '从', '自', '往', '向', '朝', '沿', '顺', '对', '为', '给', '替', '跟', '和', '同', '以', '用', '凭', '靠', '因', '除', '比'],
    "noun":[
    "猫", "狗", "鱼", "鸟", "兔子", "仓鼠",
    "手机", "电脑", "键盘", "鼠标", "耳机", "充电器",
    "咖啡", "奶茶", "可乐", "面包", "泡面", "火锅",
    "床", "沙发", "桌子", "椅子", "灯", "窗帘",
    "书", "笔", "本子", "试卷", "书包", "文件夹",
    "太阳", "月亮", "星星", "云", "雨", "风",
    "山", "河", "海", "树", "花", "草",
    "朋友", "老师", "同学", "老板", "同事", "家人",
    "游戏", "电影", "音乐", "小说", "漫画", "动画",
    "代码", "bug", "服务器", "数据库", "接口", "前端"
],
    "verb": ['走', '跑', '跳', '飞', '爬', '游', '看', '听', '说', '读', '写', '吃', '喝', '穿', '戴', '拿', '放', '打', '骂', '推', '拉', '提', '扛', '想', '爱', '恨', '怕', '愁', '盼', '愿', '喜', '怒', '哀', '乐', '在', '有', '存', '留', '住', '停', '坐', '站', '躺', '卧', '变', '改', '换', '成', '长', '生', '死', '灭', '兴', '衰'],
    "pron": ['我', '我们', '咱们', '你', '您', '你们', '他', '她', '它', '他们', '她们', '它们', '大家', '大伙儿', '别人', '人家'],
    "adv": ['都', '就', '才', '只', '也', '再', '又', '还', '正', '刚', '先', '老', '总', '常', '已', '早', '晚', '快', '慢', '好', '真', '最', '更', '越', '极', '偏', '竟'],
    "adj": [
    "大", "小", "多", "少", "好", "坏",
    "高", "低", "快", "慢", "新", "旧",
    "红", "绿", "黑", "白", "美", "丑",
    "长", "短", "冷", "热", "轻", "重"],
    "other":["是","很","太"],
    "ve":["的"],
    "sound":["吧","啊","啊"],
    "func":[",","。","?","!"],
    
}
collocation = {
    "prep": ["pron", "noun", "verb","ve"],
    "verb": ["noun", "prep", 
    "adv","noun","noun","noun","pron","other","ve"],
    "adj": ["ve","sound"],
    "adv": ["verb"],
    "noun": ['prep',"other","ve"],
    "pron": ["verb","other"],
    "other":["adj"],
    "ve":["noun","sound"]
}
word=["prep","verb","adj","adv","noun","pron","other","ve","sound"]
now="pron"
text=""
def wordrand():
    global now
    global text
    now_word=words.get(now)
    rand_word=random.randint(1,len(now_word))-1
    text+=now_word[rand_word]
    now_list=collocation.get(now)
    if not now_list:return ""
    #print(now_list)#这行没*用
    rand_type=random.randint(1,len(now_list))-1
    now=now_list[rand_type]
    #¯\_(ツ)_/¯oiia
for t in range(random.randint(5,5)):
    now="pron"
    text=""
    for i in range(random.randint(5,8)):
        #print(now)
        if now != "sound":
            wordrand()
        else:
            wordrand()
            now="pron"
            break
    text+=words["func"][random.randint(0,3)]
    print(text)