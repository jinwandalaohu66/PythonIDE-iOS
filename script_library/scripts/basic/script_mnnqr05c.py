#!/usr/bin/env python3
"""
通讯录统计脚本
功能：统计和分析iOS通讯录数据
"""

import contacts
import json
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys

class ContactsStatistics:
    """通讯录统计分析器"""
    
    def __init__(self):
        self.people = []
        self.stats = {}
        
    def load_contacts(self) -> bool:
        """加载通讯录数据"""
        try:
            # 检查权限
            status = contacts.authorization_status()
            print(f"通讯录权限状态: {status}")
            
            if status not in ['authorized', 'limited']:
                print("请求通讯录访问权限...")
                if not contacts.request_access():
                    print("错误：用户拒绝了通讯录访问权限")
                    return False
            
            # 获取所有联系人
            self.people = contacts.get_all_people()
            print(f"成功加载 {len(self.people)} 个联系人")
            return True
            
        except Exception as e:
            print(f"加载通讯录时出错: {e}")
            return False
    
    def analyze_basic_stats(self) -> Dict[str, Any]:
        """分析基础统计信息"""
        stats = {
            'total_contacts': len(self.people),
            'with_phone': 0,
            'with_email': 0,
            'with_address': 0,
            'with_birthday': 0,
            'with_image': 0,
            'by_type': {'person': 0, 'organization': 0},
            'by_gender': {'male': 0, 'female': 0, 'unknown': 0}
        }
        
        for person in self.people:
            # 统计联系人类型
            if person.kind == contacts.PERSON:
                stats['by_type']['person'] += 1
            elif person.kind == contacts.ORGANIZATION:
                stats['by_type']['organization'] += 1
            
            # 统计是否有各种信息
            if person.phone:
                stats['with_phone'] += 1
            if person.email:
                stats['with_email'] += 1
            if person.address:
                stats['with_address'] += 1
            if person.birthday:
                stats['with_birthday'] += 1
            if person.has_image:
                stats['with_image'] += 1
            
            # 尝试从名字推断性别（简单规则）
            first_name = (person.first_name or '').lower()
            if any(name in first_name for name in ['先生', '男', 'mr', 'mister']):
                stats['by_gender']['male'] += 1
            elif any(name in first_name for name in ['女士', '女', 'ms', 'miss', 'mrs']):
                stats['by_gender']['female'] += 1
            else:
                stats['by_gender']['unknown'] += 1
        
        return stats
    
    def analyze_phone_numbers(self) -> Dict[str, Any]:
        """分析电话号码"""
        phone_stats = {
            'total_numbers': 0,
            'numbers_per_contact': [],
            'area_codes': Counter(),
            'phone_types': Counter(),
            'countries': Counter()
        }
        
        for person in self.people:
            if person.phone:
                phone_count = len(person.phone)
                phone_stats['total_numbers'] += phone_count
                phone_stats['numbers_per_contact'].append(phone_count)
                
                for label, number in person.phone:
                    # 统计电话类型
                    phone_type = label.lower() if label else 'unknown'
                    phone_stats['phone_types'][phone_type] += 1
                    
                    # 尝试提取区号和国家
                    if number:
                        # 简单判断国家代码
                        if number.startswith('+86'):
                            phone_stats['countries']['中国'] += 1
                        elif number.startswith('+1'):
                            phone_stats['countries']['美国/加拿大'] += 1
                        elif number.startswith('+44'):
                            phone_stats['countries']['英国'] += 1
                        elif number.startswith('+81'):
                            phone_stats['countries']['日本'] += 1
                        elif number.startswith('+82'):
                            phone_stats['countries']['韩国'] += 1
                        else:
                            phone_stats['countries']['其他'] += 1
        
        # 计算平均每个联系人的电话号码数
        if phone_stats['numbers_per_contact']:
            avg_numbers = sum(phone_stats['numbers_per_contact']) / len(phone_stats['numbers_per_contact'])
            phone_stats['avg_numbers_per_contact'] = round(avg_numbers, 2)
        else:
            phone_stats['avg_numbers_per_contact'] = 0
        
        return phone_stats
    
    def analyze_email_addresses(self) -> Dict[str, Any]:
        """分析电子邮件地址"""
        email_stats = {
            'total_emails': 0,
            'emails_per_contact': [],
            'email_domains': Counter(),
            'email_types': Counter()
        }
        
        for person in self.people:
            if person.email:
                email_count = len(person.email)
                email_stats['total_emails'] += email_count
                email_stats['emails_per_contact'].append(email_count)
                
                for label, email in person.email:
                    # 统计邮箱类型
                    email_type = label.lower() if label else 'unknown'
                    email_stats['email_types'][email_type] += 1
                    
                    # 提取域名
                    if '@' in email:
                        domain = email.split('@')[1].lower()
                        email_stats['email_domains'][domain] += 1
        
        # 计算平均每个联系人的邮箱数
        if email_stats['emails_per_contact']:
            avg_emails = sum(email_stats['emails_per_contact']) / len(email_stats['emails_per_contact'])
            email_stats['avg_emails_per_contact'] = round(avg_emails, 2)
        else:
            email_stats['avg_emails_per_contact'] = 0
        
        return email_stats
    
    def analyze_names(self) -> Dict[str, Any]:
        """分析姓名信息"""
        name_stats = {
            'total_names': 0,
            'first_names': Counter(),
            'last_names': Counter(),
            'full_names': [],
            'name_lengths': []
        }
        
        for person in self.people:
            full_name = person.full_name or ''
            if full_name:
                name_stats['full_names'].append(full_name)
                name_stats['name_lengths'].append(len(full_name))
                name_stats['total_names'] += 1
            
            if person.first_name:
                name_stats['first_names'][person.first_name] += 1
            if person.last_name:
                name_stats['last_names'][person.last_name] += 1
        
        # 计算平均姓名长度
        if name_stats['name_lengths']:
            avg_length = sum(name_stats['name_lengths']) / len(name_stats['name_lengths'])
            name_stats['avg_name_length'] = round(avg_length, 2)
        else:
            name_stats['avg_name_length'] = 0
        
        return name_stats
    
    def analyze_organizations(self) -> Dict[str, Any]:
        """分析组织信息"""
        org_stats = {
            'total_organizations': 0,
            'companies': Counter(),
            'departments': Counter(),
            'job_titles': Counter(),
            'company_sizes': defaultdict(int)
        }
        
        for person in self.people:
            if person.organization:
                org_stats['total_organizations'] += 1
                org_stats['companies'][person.organization] += 1
            
            if person.department:
                org_stats['departments'][person.department] += 1
            
            if person.job_title:
                org_stats['job_titles'][person.job_title] += 1
        
        return org_stats
    
    def analyze_groups(self) -> Dict[str, Any]:
        """分析分组信息"""
        group_stats = {
            'total_groups': 0,
            'group_names': [],
            'contacts_per_group': defaultdict(int)
        }
        
        try:
            groups = contacts.get_all_groups()
            group_stats['total_groups'] = len(groups)
            group_stats['group_names'] = [group.name for group in groups if group.name]
            
            # 统计每个分组的人数
            for group in groups:
                people_in_group = contacts.get_people_in_group(group)
                group_stats['contacts_per_group'][group.name or f"未命名分组{group.id}"] = len(people_in_group)
                
        except Exception as e:
            print(f"分析分组时出错: {e}")
        
        return group_stats
    
    def analyze_creation_dates(self) -> Dict[str, Any]:
        """分析创建时间分布"""
        date_stats = {
            'by_year': Counter(),
            'by_month': Counter(),
            'recent_contacts': 0
        }
        
        current_year = datetime.now().year
        
        for person in self.people:
            if person.creation_date:
                try:
                    # 尝试解析日期
                    if isinstance(person.creation_date, (int, float)):
                        # 可能是时间戳
                        dt = datetime.fromtimestamp(person.creation_date)
                    else:
                        # 尝试其他格式
                        continue
                    
                    year = dt.year
                    month = dt.month
                    
                    date_stats['by_year'][year] += 1
                    date_stats['by_month'][month] += 1
                    
                    # 统计最近一年添加的联系人
                    if year == current_year:
                        date_stats['recent_contacts'] += 1
                        
                except Exception:
                    continue
        
        return date_stats
    
    def generate_report(self) -> Dict[str, Any]:
        """生成完整统计报告"""
        print("开始分析通讯录数据...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'basic_stats': self.analyze_basic_stats(),
            'phone_stats': self.analyze_phone_numbers(),
            'email_stats': self.analyze_email_addresses(),
            'name_stats': self.analyze_names(),
            'org_stats': self.analyze_organizations(),
            'group_stats': self.analyze_groups(),
            'date_stats': self.analyze_creation_dates()
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """打印统计报告"""
        print("\n" + "="*60)
        print("通讯录统计报告")
        print("="*60)
        
        basic = report['basic_stats']
        print(f"\n📊 基础统计:")
        print(f"  总联系人: {basic['total_contacts']}")
        print(f"  个人联系人: {basic['by_type']['person']}")
        print(f"  组织联系人: {basic['by_type']['organization']}")
        print(f"  有电话号码: {basic['with_phone']} ({basic['with_phone']/basic['total_contacts']*100:.1f}%)")
        print(f"  有电子邮件: {basic['with_email']} ({basic['with_email']/basic['total_contacts']*100:.1f}%)")
        print(f"  有地址信息: {basic['with_address']} ({basic['with_address']/basic['total_contacts']*100:.1f}%)")
        print(f"  有生日信息: {basic['with_birthday']} ({basic['with_birthday']/basic['total_contacts']*100:.1f}%)")
        print(f"  有头像图片: {basic['with_image']} ({basic['with_image']/basic['total_contacts']*100:.1f}%)")
        
        phone = report['phone_stats']
        print(f"\n📱 电话统计:")
        print(f"  总电话号码: {phone['total_numbers']}")
        print(f"  平均每人电话数: {phone['avg_numbers_per_contact']}")
        if phone['phone_types']:
            print(f"  电话类型分布:")
            for type_name, count in phone['phone_types'].most_common(5):
                print(f"    {type_name}: {count}")
        if phone['countries']:
            print(f"  国家/地区分布:")
            for country, count in phone['countries'].most_common():
                print(f"    {country}: {count}")
        
        email = report['email_stats']
        print(f"\n📧 邮箱统计:")
        print(f"  总邮箱地址: {email['total_emails']}")
        print(f"  平均每人邮箱数: {email['avg_emails_per_contact']}")
        if email['email_domains']:
            print(f"  热门邮箱域名:")
            for domain, count in email['email_domains'].most_common(5):
                print(f"    {domain}: {count}")
        
        names = report['name_stats']
        print(f"\n👤 姓名统计:")
        print(f"  有完整姓名: {names['total_names']}")
        print(f"  平均姓名长度: {names['avg_name_length']} 字符")
        if names['first_names']:
            print(f"  热门名字:")
            for name, count in names['first_names'].most_common(5):
                print(f"    {name}: {count}")
        
        org = report['org_stats']
        if org['total_organizations'] > 0:
            print(f"\n🏢 组织统计:")
            print(f"  有组织信息: {org['total_organizations']}")
            if org['companies']:
                print(f"  热门公司:")
                for company, count in org['companies'].most_common(5):
                    print(f"    {company}: {count}")
        
        groups = report['group_stats']
        if groups['total_groups'] > 0:
            print(f"\n📂 分组统计:")
            print(f"  总分组数: {groups['total_groups']}")
            if groups['contacts_per_group']:
                print(f"  分组人数分布:")
                for group_name, count in sorted(groups['contacts_per_group'].items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"    {group_name}: {count} 人")
        
        dates = report['date_stats']
        if dates['by_year']:
            print(f"\n📅 时间统计:")
            print(f"  最近一年添加: {dates['recent_contacts']} 人")
            if dates['by_year']:
                print(f"  按年分布:")
                for year, count in sorted(dates['by_year'].items(), reverse=True)[:5]:
                    print(f"    {year}年: {count} 人")
        
        print("\n" + "="*60)
        print("分析完成！")
        print("="*60)
    
    def save_report_to_file(self, report: Dict[str, Any], filename: str = "contacts_report.json"):
        """保存报告到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n报告已保存到: {filename}")
            return True
        except Exception as e:
            print(f"保存报告时出错: {e}")
            return False


def main():
    """主函数"""
    print("通讯录统计工具 v1.0")
    print("正在加载通讯录数据...")
    
    analyzer = ContactsStatistics()
    
    # 加载通讯录
    if not analyzer.load_contacts():
        print("无法加载通讯录数据，请检查权限设置")
        return
    
    if not analyzer.people:
        print("通讯录为空或没有联系人")
        return
    
    # 生成报告
    report = analyzer.generate_report()
    
    # 打印报告
    analyzer.print_report(report)
    
    # 自动保存报告（避免交互式input问题）
    try:
        analyzer.save_report_to_file(report)
        print("报告已自动保存到 contacts_report.json")
    except Exception as e:
        print(f"保存报告时出错: {e}")
    
    print("\n感谢使用通讯录统计工具！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback
        traceback.print_exc()