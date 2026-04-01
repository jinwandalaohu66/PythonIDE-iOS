"""
骚扰电话与异常短信检测防护工具
功能：号码识别、黑名单管理、短信内容分析、拦截记录
"""

import re
import json
import time
from datetime import datetime
from typing import List, Dict, Tuple
import ui

# ========== 数据存储 ==========
class ProtectionData:
    """防护数据管理"""
    
    def __init__(self):
        self.blacklist_file = "spam_blacklist.json"
        self.records_file = "spam_records.json"
        
        # 已知的骚扰号码段（示例数据）
        self.known_spam_prefixes = [
            "95",      # 商业服务号段（常被滥用）
            "400",     # 企业客服号段
            "1069",    # 短信通道号段
        ]
        
        # 骚扰关键词
        self.spam_keywords = [
            "贷款", "借款", "信用卡", "额度", "放款",
            "中奖", "恭喜", "领取", "红包", "优惠",
            "验证码", "动态密码", "校验码",
            "点击链接", "立即查看", "限时",
            "退订回T", "回复TD", "回N退订",
            "投资", "理财", "收益", "赚钱",
            "房产", "售楼", "首付", "楼盘"
        ]
        
        # 钓鱼链接特征
        self.phishing_patterns = [
            r'http[s]?://[^\s]+\.(xyz|top|wang|win|loan|vip|club|online|site|website|space|live|pro|work|click|link|info|biz|me|pw|cc|tk|ml|ga|cf|gq)',
            r'http[s]?://[^\s]*[0-9]{6,}[^\s]*',  # 包含长数字串的链接
            r'http[s]?://[^\s]*-[^\s]*-[^\s]*\.',  # 多级短横线域名
        ]
        
        # 加载数据（在所有属性初始化后）
        self.blacklist = self.load_blacklist()
        self.records = self.load_records()
    
    def load_blacklist(self) -> Dict:
        """加载黑名单"""
        try:
            with open(self.blacklist_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"numbers": {}, "keywords": self.spam_keywords}
    
    def save_blacklist(self):
        """保存黑名单"""
        with open(self.blacklist_file, 'w', encoding='utf-8') as f:
            json.dump(self.blacklist, f, ensure_ascii=False, indent=2)
    
    def load_records(self) -> List:
        """加载拦截记录"""
        try:
            with open(self.records_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def save_records(self):
        """保存拦截记录"""
        with open(self.records_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    def add_to_blacklist(self, number: str, reason: str = ""):
        """添加号码到黑名单"""
        self.blacklist["numbers"][number] = {
            "reason": reason,
            "add_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_blacklist()
    
    def remove_from_blacklist(self, number: str):
        """从黑名单移除号码"""
        if number in self.blacklist["numbers"]:
            del self.blacklist["numbers"][number]
            self.save_blacklist()
    
    def add_record(self, number: str, content: str, spam_type: str, risk_level: str):
        """添加拦截记录"""
        record = {
            "number": number,
            "content": content[:100],  # 只保存前100字符
            "type": spam_type,
            "risk": risk_level,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.records.insert(0, record)
        # 只保留最近100条记录
        self.records = self.records[:100]
        self.save_records()

# ========== 检测引擎 ==========
class SpamDetector:
    """骚扰检测引擎"""
    
    def __init__(self, data: ProtectionData):
        self.data = data
    
    def analyze_number(self, number: str) -> Tuple[bool, str, str]:
        """
        分析电话号码
        返回: (是否骚扰, 类型, 风险等级)
        """
        # 检查黑名单
        if number in self.data.blacklist["numbers"]:
            return True, "黑名单号码", "高危"
        
        # 检查已知骚扰号段
        for prefix in self.data.known_spam_prefixes:
            if number.startswith(prefix):
                return True, f"骚扰号段({prefix})", "中危"
        
        # 检查号码特征
        # 1. 连续重复数字
        if re.search(r'(\d)\1{5,}', number):
            return True, "异常号码(重复数字)", "中危"
        
        # 2. 顺子号码
        if re.search(r'012345|123456|234567|345678|456789|567890', number):
            return True, "异常号码(顺子)", "低危"
        
        # 3. 号码长度异常
        if len(number) < 11 and number.startswith('1'):
            return True, "异常号码(长度不足)", "中危"
        
        # 4. 虚拟运营商号段（170/171常被滥用）
        if number.startswith('170') or number.startswith('171'):
            return True, "虚拟运营商号段", "中危"
        
        return False, "正常号码", "安全"
    
    def analyze_sms(self, content: str) -> Tuple[bool, List[str], str]:
        """
        分析短信内容
        返回: (是否骚扰, 匹配关键词列表, 风险等级)
        """
        matched_keywords = []
        
        # 检查骚扰关键词
        for keyword in self.data.spam_keywords:
            if keyword in content:
                matched_keywords.append(keyword)
        
        # 检查钓鱼链接
        has_phishing_link = False
        for pattern in self.data.phishing_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                has_phishing_link = True
                matched_keywords.append("可疑链接")
                break
        
        # 判断风险等级
        if len(matched_keywords) >= 3 or has_phishing_link:
            return True, matched_keywords, "高危"
        elif len(matched_keywords) >= 1:
            return True, matched_keywords, "中危"
        
        return False, [], "安全"
    
    def analyze_frequency(self, number: str, time_window: int = 3600) -> Tuple[bool, int]:
        """
        分析发送频率
        time_window: 时间窗口（秒），默认1小时
        返回: (是否异常, 发送次数)
        """
        current_time = time.time()
        count = 0
        
        for record in self.data.records:
            if record["number"] == number:
                record_time = datetime.strptime(record["time"], "%Y-%m-%d %H:%M:%S").timestamp()
                if current_time - record_time <= time_window:
                    count += 1
        
        # 1小时内超过5次视为异常
        is_abnormal = count >= 5
        return is_abnormal, count

# ========== UI界面 ==========
class ProtectionUI:
    """防护工具UI"""
    
    def __init__(self):
        self.data = ProtectionData()
        self.detector = SpamDetector(self.data)
        self.setup_ui()
    
    def setup_ui(self):
        """创建UI界面"""
        self.view = ui.View(name="骚扰防护工具", background_color="#F5F5F5")
        self.view.present('fullscreen')
        
        # 标题
        title = ui.Label(text="🛡️ 骚扰电话与短信防护", font=("<system>", 20, "bold"), text_color="#1a1a1a")
        title.frame = (0, 60, self.view.width, 40)
        title.alignment = ui.ALIGN_CENTER
        self.view.add_subview(title)
        
        # 创建分段控制器
        self.segmented = ui.SegmentedControl(items=["号码检测", "短信分析", "黑名单", "拦截记录"])
        self.segmented.frame = (20, 110, self.view.width - 40, 35)
        self.segmented.action = self.segment_changed
        self.segmented.selected_index = 0
        self.view.add_subview(self.segmented)
        
        # 内容容器
        self.container = ui.View(frame=(0, 160, self.view.width, self.view.height - 180), 
                                  background_color="white")
        self.view.add_subview(self.container)
        
        # 初始化各页面
        self.setup_number_check_page()
        self.setup_sms_check_page()
        self.setup_blacklist_page()
        self.setup_records_page()
        
        # 默认显示第一页
        self.show_page(0)
    
    def segment_changed(self, sender):
        """分段控制器切换"""
        self.show_page(sender.selected_index)
    
    def show_page(self, index: int):
        """显示指定页面"""
        for i, page in enumerate([self.number_page, self.sms_page, self.blacklist_page, self.records_page]):
            page.hidden = (i != index)
    
    def setup_number_check_page(self):
        """号码检测页面"""
        self.number_page = ui.View(frame=self.container.bounds, background_color="white")
        self.container.add_subview(self.number_page)
        
        # 输入框
        input_label = ui.Label(text="输入电话号码:", font=("<system>", 14), text_color="#666")
        input_label.frame = (20, 20, 200, 25)
        self.number_page.add_subview(input_label)
        
        self.number_input = ui.TextField(placeholder="请输入电话号码", font=("<system>", 16))
        self.number_input.frame = (20, 50, self.number_page.width - 40, 40)
        self.number_input.border_style = 3  # BORDER_ROUNDED_RECT
        self.number_input.autocapitalization_type = 0  # AUTOCAPITALIZE_NONE
        self.number_input.autocorrection_type = False
        self.number_input.keyboard_type = 2  # KEYBOARD_NUMBER_PAD
        self.number_page.add_subview(self.number_input)
        
        # 检测按钮
        check_btn = ui.Button(title="开始检测", font=("<system>", 16, "bold"), 
                              background_color="#007AFF", tint_color="white")
        check_btn.frame = (20, 110, self.number_page.width - 40, 44)
        check_btn.corner_radius = 10
        check_btn.action = self.check_number
        self.number_page.add_subview(check_btn)
        
        # 结果显示
        self.number_result = ui.TextView(font=("<system>", 14), editable=False)
        self.number_result.frame = (20, 170, self.number_page.width - 40, 200)
        self.number_result.border_color = "#E0E0E0"
        self.number_result.border_width = 1
        self.number_result.corner_radius = 8
        self.number_result.text = "检测结果将显示在这里..."
        self.number_page.add_subview(self.number_result)
        
        # 快速添加黑名单按钮
        add_blacklist_btn = ui.Button(title="添加到黑名单", font=("<system>", 14), 
                                       background_color="#FF3B30", tint_color="white")
        add_blacklist_btn.frame = (20, 385, self.number_page.width - 40, 40)
        add_blacklist_btn.corner_radius = 10
        add_blacklist_btn.action = self.add_to_blacklist_from_input
        self.number_page.add_subview(add_blacklist_btn)
    
    def setup_sms_check_page(self):
        """短信分析页面"""
        self.sms_page = ui.View(frame=self.container.bounds, background_color="white")
        self.sms_page.hidden = True
        self.container.add_subview(self.sms_page)
        
        # 号码输入
        num_label = ui.Label(text="发送方号码:", font=("<system>", 14), text_color="#666")
        num_label.frame = (20, 20, 200, 25)
        self.sms_page.add_subview(num_label)
        
        self.sms_number_input = ui.TextField(placeholder="输入发送方号码", font=("<system>", 14))
        self.sms_number_input.frame = (20, 45, self.sms_page.width - 40, 35)
        self.sms_number_input.border_style = 3  # BORDER_ROUNDED_RECT
        self.sms_number_input.keyboard_type = 2  # KEYBOARD_NUMBER_PAD
        self.sms_page.add_subview(self.sms_number_input)
        
        # 短信内容输入
        content_label = ui.Label(text="短信内容:", font=("<system>", 14), text_color="#666")
        content_label.frame = (20, 90, 200, 25)
        self.sms_page.add_subview(content_label)
        
        self.sms_content_input = ui.TextView(font=("<system>", 14), placeholder="粘贴短信内容...")
        self.sms_content_input.frame = (20, 115, self.sms_page.width - 40, 120)
        self.sms_content_input.border_color = "#E0E0E0"
        self.sms_content_input.border_width = 1
        self.sms_content_input.corner_radius = 8
        self.sms_page.add_subview(self.sms_content_input)
        
        # 分析按钮
        analyze_btn = ui.Button(title="分析短信", font=("<system>", 16, "bold"), 
                                background_color="#007AFF", tint_color="white")
        analyze_btn.frame = (20, 250, self.sms_page.width - 40, 44)
        analyze_btn.corner_radius = 10
        analyze_btn.action = self.analyze_sms
        self.sms_page.add_subview(analyze_btn)
        
        # 结果显示
        self.sms_result = ui.TextView(font=("<system>", 14), editable=False)
        self.sms_result.frame = (20, 310, self.sms_page.width - 40, 150)
        self.sms_result.border_color = "#E0E0E0"
        self.sms_result.border_width = 1
        self.sms_result.corner_radius = 8
        self.sms_result.text = "分析结果将显示在这里..."
        self.sms_page.add_subview(self.sms_result)
    
    def setup_blacklist_page(self):
        """黑名单管理页面"""
        self.blacklist_page = ui.View(frame=self.container.bounds, background_color="white")
        self.blacklist_page.hidden = True
        self.container.add_subview(self.blacklist_page)
        
        # 标题
        title = ui.Label(text="黑名单列表", font=("<system>", 16, "bold"), text_color="#333")
        title.frame = (20, 20, 200, 25)
        self.blacklist_page.add_subview(title)
        
        # 黑名单列表 - 使用列表作为数据源
        blacklist_numbers = list(self.data.blacklist.get("numbers", {}).keys())
        self.blacklist_table = ui.TableView(frame=(20, 55, self.blacklist_page.width - 40, 
                                                    self.blacklist_page.height - 120))
        self.blacklist_table.data_source = blacklist_numbers
        self.blacklist_page.add_subview(self.blacklist_table)
        
        # 清空按钮
        clear_btn = ui.Button(title="清空黑名单", font=("<system>", 14), 
                              background_color="#FF9500", tint_color="white")
        clear_btn.frame = (20, self.blacklist_page.height - 55, self.blacklist_page.width - 40, 40)
        clear_btn.corner_radius = 10
        clear_btn.action = self.clear_blacklist
        self.blacklist_page.add_subview(clear_btn)
    
    def setup_records_page(self):
        """拦截记录页面"""
        self.records_page = ui.View(frame=self.container.bounds, background_color="white")
        self.records_page.hidden = True
        self.container.add_subview(self.records_page)
        
        # 标题
        title = ui.Label(text="拦截记录", font=("<system>", 16, "bold"), text_color="#333")
        title.frame = (20, 20, 200, 25)
        self.records_page.add_subview(title)
        
        # 记录列表 - 使用列表作为数据源
        record_texts = [f"{r.get('number', '未知')} - {r.get('type', '未知')}" for r in self.data.records]
        self.records_table = ui.TableView(frame=(20, 55, self.records_page.width - 40, 
                                                  self.records_page.height - 120))
        self.records_table.data_source = record_texts
        self.records_page.add_subview(self.records_table)
        
        # 清空按钮
        clear_btn = ui.Button(title="清空记录", font=("<system>", 14), 
                              background_color="#8E8E93", tint_color="white")
        clear_btn.frame = (20, self.records_page.height - 55, self.records_page.width - 40, 40)
        clear_btn.corner_radius = 10
        clear_btn.action = self.clear_records
        self.records_page.add_subview(clear_btn)
    
    # ========== 功能实现 ==========
    def check_number(self, sender):
        """检测号码"""
        number = self.number_input.text.strip()
        if not number:
            self.number_result.text = "❌ 请输入电话号码"
            return
        
        is_spam, spam_type, risk_level = self.detector.analyze_number(number)
        is_freq_abnormal, freq_count = self.detector.analyze_frequency(number)
        
        result = f"📱 号码: {number}\n\n"
        
        if is_spam:
            result += f"⚠️ 检测结果: 骚扰号码\n"
            result += f"📋 类型: {spam_type}\n"
            result += f"🎯 风险等级: {risk_level}\n\n"
            
            if risk_level == "高危":
                result += "🔴 建议: 立即拉黑并举报"
            elif risk_level == "中危":
                result += "🟡 建议: 谨慎接听或拉黑"
            else:
                result += "🟢 建议: 可选择性拉黑"
        else:
            result += f"✅ 检测结果: 正常号码\n"
            result += f"📋 类型: {spam_type}\n"
            result += f"🎯 风险等级: {risk_level}\n\n"
            result += "✓ 该号码未发现异常"
        
        if is_freq_abnormal:
            result += f"\n\n⚡ 频率异常: 近1小时已拦截 {freq_count} 次"
        
        self.number_result.text = result
    
    def add_to_blacklist_from_input(self, sender):
        """从输入框添加到黑名单"""
        number = self.number_input.text.strip()
        if not number:
            self.number_result.text = "❌ 请先输入电话号码"
            return
        
        if number in self.data.blacklist["numbers"]:
            self.number_result.text = "⚠️ 该号码已在黑名单中"
            return
        
        is_spam, spam_type, _ = self.detector.analyze_number(number)
        reason = spam_type if is_spam else "手动添加"
        
        self.data.add_to_blacklist(number, reason)
        self.number_result.text = f"✅ 已将 {number} 添加到黑名单\n原因: {reason}"
        self.number_input.text = ""
    
    def analyze_sms(self, sender):
        """分析短信"""
        number = self.sms_number_input.text.strip()
        content = self.sms_content_input.text.strip()
        
        if not content:
            self.sms_result.text = "❌ 请输入短信内容"
            return
        
        # 分析号码
        is_number_spam, number_type, number_risk = self.detector.analyze_number(number) if number else (False, "", "未知")
        
        # 分析内容
        is_content_spam, keywords, content_risk = self.detector.analyze_sms(content)
        
        # 综合判断
        is_spam = is_number_spam or is_content_spam
        risk_level = "高危" if (number_risk == "高危" or content_risk == "高危") else \
                     "中危" if (number_risk == "中危" or content_risk == "中危") else "低危"
        
        result = f"📱 发送方: {number if number else '未知'}\n\n"
        
        if number:
            result += f"号码状态: {'⚠️ ' + number_type if is_number_spam else '✅ 正常'}\n"
        
        result += f"内容分析: {'⚠️ 疑似骚扰短信' if is_content_spam else '✅ 未发现异常'}\n"
        
        if keywords:
            result += f"\n匹配关键词:\n"
            for kw in keywords[:5]:  # 只显示前5个
                result += f"  • {kw}\n"
        
        result += f"\n🎯 综合风险: {risk_level}\n"
        
        if is_spam:
            result += "\n💡 建议: 不要点击短信中的链接，建议拉黑该号码"
            
            # 添加到拦截记录
            if number:
                self.data.add_record(number, content, "骚扰短信", risk_level)
        else:
            result += "\n✓ 该短信未发现明显异常"
        
        self.sms_result.text = result
    
    def clear_blacklist(self, sender):
        """清空黑名单"""
        import dialogs
        if dialogs.alert("确认清空", "确定要清空所有黑名单吗？", "取消", "确定") == 1:
            self.data.blacklist["numbers"] = {}
            self.data.save_blacklist()
            self.blacklist_table.reload()
    
    def clear_records(self, sender):
        """清空记录"""
        import dialogs
        if dialogs.alert("确认清空", "确定要清空所有拦截记录吗？", "取消", "确定") == 1:
            self.data.records = []
            self.data.save_records()
            self.records_table.reload()

# ========== 主程序 ==========
if __name__ == "__main__":
    app = ProtectionUI()
