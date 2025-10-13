#!/usr/bin/env python3
"""
完整的Boss直聘投递系统
基于get_jobs项目的完整功能实现
包含筛选、AI功能、黑名单等高级特性
"""
import os
import sys
import django
import time
import random
import json
import re
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

class BossDeliverySystem:
    """完整的Boss直聘投递系统"""
    
    def __init__(self):
        # Boss直聘token信息
        self.boss_tokens = {
            '__a': '20936101.1758901166..1758901166.19.1.19.19',
            '__c': '1758901166',
            '__g': '-',
            'wt2': 'D2y_BLA5FPxKjmqhFOuSX9pQDHmTd50-OQ-wS-SDxyIZ4WIDCooRN3MqRqmbDFCS6Kpch5GY66BQC1jp0WDHSTQ~~',
            'zp_at': 'e3Pvolc3amIiibtwbgYEIqmtzY-O0xZNqCzuqt7mO60~'
        }
        
        # 投递配置
        self.config = {
            "keywords": ["Python开发", "Django开发", "后端开发", "全栈开发"],
            "cities": ["北京", "上海", "深圳", "杭州", "广州"],
            "salary_range": [8000, 25000],  # 薪资范围
            "experience_range": [1, 5],  # 经验范围
            "max_applications": 10,
            "delay_between_applications": (2, 4),
            "delay_between_pages": (3, 6),
            "use_ai_greeting": True,  # 使用AI生成打招呼内容
            "enable_filters": True,  # 启用筛选功能
        }
        
        # 黑名单配置
        self.blacklist = {
            "companies": ["外包", "外派", "派遣", "第三方", "外包公司"],
            "recruiters": ["猎头", "中介", "外包"],
            "jobs": ["外包", "外派", "派遣", "第三方", "临时", "兼职"],
            "keywords": ["外包", "外派", "派遣", "第三方", "临时", "兼职", "实习"]
        }
        
        # AI打招呼模板
        self.ai_greeting_templates = [
            "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。",
            "您好，我看到这个职位与我的技能匹配度很高，希望能有机会详谈。",
            "您好，我对贵公司的这个职位很感兴趣，希望能有机会进一步了解。",
            "您好，我的经验与这个职位要求很匹配，希望能有机会进一步沟通。",
            "您好，我对这个职位很感兴趣，希望能有机会进一步交流。"
        ]
        
        # 统计信息
        self.stats = {
            "total_found": 0,
            "total_applied": 0,
            "total_filtered": 0,
            "blacklist_filtered": 0,
            "salary_filtered": 0,
            "experience_filtered": 0,
            "companies_applied": set(),
            "keywords_used": set()
        }
    
    def setup_browser(self):
        """设置浏览器"""
        print("🌐 启动Playwright浏览器...")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,  # 显示浏览器窗口
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions',
                '--disable-plugins',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-popup-blocking',
                '--disable-translate',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-client-side-phishing-detection',
                '--disable-sync',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
            ]
        )
        
        self.page = self.browser.new_page()
        
        # 设置User-Agent
        self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 设置cookies
        print("🍪 设置Boss直聘cookies...")
        for name, value in self.boss_tokens.items():
            self.page.context.add_cookies([{
                'name': name,
                'value': value,
                'domain': '.zhipin.com',
                'path': '/',
                'httpOnly': False,
                'secure': False,
                'sameSite': 'Lax'
            }])
            print(f"   ✅ 设置cookie: {name}")
    
    def close_browser(self):
        """关闭浏览器"""
        if hasattr(self, 'browser'):
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """随机延迟"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def generate_ai_greeting(self, job_title: str, company_name: str) -> str:
        """生成AI打招呼内容"""
        if not self.config["use_ai_greeting"]:
            return random.choice(self.ai_greeting_templates)
        
        # 基于职位和公司生成个性化打招呼内容
        templates = [
            f"您好，我对{company_name}的{job_title}职位很感兴趣，希望能有机会进一步沟通。",
            f"您好，我看到{company_name}的{job_title}职位与我的技能匹配度很高，希望能有机会详谈。",
            f"您好，我对贵公司的{job_title}职位很感兴趣，希望能有机会进一步了解。",
            f"您好，我的经验与{company_name}的{job_title}职位要求很匹配，希望能有机会进一步沟通。",
            f"您好，我对{company_name}的{job_title}职位很感兴趣，希望能有机会进一步交流。"
        ]
        
        return random.choice(templates)
    
    def is_blacklisted(self, job_info: Dict[str, Any]) -> bool:
        """检查是否在黑名单中"""
        company_name = job_info.get('company', '').lower()
        job_title = job_info.get('title', '').lower()
        job_description = job_info.get('description', '').lower()
        
        # 检查公司黑名单
        for black_company in self.blacklist["companies"]:
            if black_company in company_name:
                print(f"   🚫 公司黑名单过滤: {company_name} (包含: {black_company})")
                self.stats["blacklist_filtered"] += 1
                return True
        
        # 检查职位黑名单
        for black_job in self.blacklist["jobs"]:
            if black_job in job_title or black_job in job_description:
                print(f"   🚫 职位黑名单过滤: {job_title} (包含: {black_job})")
                self.stats["blacklist_filtered"] += 1
                return True
        
        # 检查关键词黑名单
        for black_keyword in self.blacklist["keywords"]:
            if black_keyword in job_title or black_keyword in job_description:
                print(f"   🚫 关键词黑名单过滤: {job_title} (包含: {black_keyword})")
                self.stats["blacklist_filtered"] += 1
                return True
        
        return False
    
    def extract_job_info(self, job_element) -> Dict[str, Any]:
        """提取职位信息"""
        try:
            # 提取职位标题
            title_element = job_element.query_selector('.job-title, .job-name, [class*="title"]')
            title = title_element.text_content().strip() if title_element else "未知职位"
            
            # 提取公司名称
            company_element = job_element.query_selector('.company-name, .company-title, [class*="company"]')
            company = company_element.text_content().strip() if company_element else "未知公司"
            
            # 提取薪资信息
            salary_element = job_element.query_selector('.salary, .job-salary, [class*="salary"]')
            salary_text = salary_element.text_content().strip() if salary_element else "面议"
            
            # 提取经验要求
            experience_element = job_element.query_selector('.experience, .job-experience, [class*="experience"]')
            experience_text = experience_element.text_content().strip() if experience_element else "不限"
            
            # 提取职位描述
            description_element = job_element.query_selector('.job-desc, .description, [class*="desc"]')
            description = description_element.text_content().strip() if description_element else ""
            
            # 解析薪资范围
            salary_range = self.parse_salary(salary_text)
            
            # 解析经验要求
            experience_years = self.parse_experience(experience_text)
            
            return {
                'title': title,
                'company': company,
                'salary_text': salary_text,
                'salary_range': salary_range,
                'experience_text': experience_text,
                'experience_years': experience_years,
                'description': description,
                'element': job_element
            }
        except Exception as e:
            print(f"   ❌ 提取职位信息失败: {str(e)}")
            return None
    
    def parse_salary(self, salary_text: str) -> List[int]:
        """解析薪资范围"""
        try:
            # 提取数字
            numbers = re.findall(r'\d+', salary_text)
            if len(numbers) >= 2:
                return [int(numbers[0]), int(numbers[1])]
            elif len(numbers) == 1:
                return [int(numbers[0]), int(numbers[0])]
            else:
                return [0, 0]
        except:
            return [0, 0]
    
    def parse_experience(self, experience_text: str) -> int:
        """解析经验要求"""
        try:
            # 提取数字
            numbers = re.findall(r'\d+', experience_text)
            if numbers:
                return int(numbers[0])
            else:
                return 0
        except:
            return 0
    
    def apply_filters(self, job_info: Dict[str, Any]) -> bool:
        """应用筛选条件"""
        if not self.config["enable_filters"]:
            return True
        
        # 薪资筛选
        if job_info['salary_range'][0] > 0:
            min_salary = self.config["salary_range"][0]
            max_salary = self.config["salary_range"][1]
            
            if job_info['salary_range'][0] < min_salary or job_info['salary_range'][1] > max_salary:
                print(f"   💰 薪资筛选过滤: {job_info['salary_text']} (要求: {min_salary}-{max_salary}k)")
                self.stats["salary_filtered"] += 1
                return False
        
        # 经验筛选
        if job_info['experience_years'] > 0:
            min_exp = self.config["experience_range"][0]
            max_exp = self.config["experience_range"][1]
            
            if job_info['experience_years'] < min_exp or job_info['experience_years'] > max_exp:
                print(f"   📅 经验筛选过滤: {job_info['experience_text']} (要求: {min_exp}-{max_exp}年)")
                self.stats["experience_filtered"] += 1
                return False
        
        return True
    
    def search_jobs(self, keyword: str) -> List[Any]:
        """搜索职位"""
        print(f"\n🔍 搜索关键词: {keyword}")
        
        try:
            # 查找搜索框
            search_input = self.page.wait_for_selector('input[placeholder*="搜索"]', timeout=5000)
            if not search_input:
                print("   ❌ 未找到搜索框")
                return []
            
            # 清空并输入关键词
            search_input.click()
            time.sleep(0.5)
            search_input.fill("")
            time.sleep(0.5)
            search_input.fill(keyword)
            print(f"   ✅ 输入关键词: {keyword}")
            time.sleep(1)
            
            # 查找搜索按钮
            search_btn = self.page.wait_for_selector('button:has-text("搜索")', timeout=5000)
            if not search_btn:
                print("   ❌ 未找到搜索按钮")
                return []
            
            # 点击搜索
            search_btn.click()
            print("   ✅ 点击搜索按钮")
            
            # 等待搜索结果加载
            delay = random.uniform(*self.config['delay_between_pages'])
            print(f"   ⏳ 等待 {delay:.1f} 秒...")
            time.sleep(delay)
            
            # 获取职位列表
            job_selectors = [
                '.job-card-wrapper',
                '.job-card',
                '.job-item',
                '.job-list-item',
                '[class*="job-card"]',
                '[class*="job-item"]'
            ]
            
            job_items = None
            for selector in job_selectors:
                try:
                    job_items = self.page.query_selector_all(selector)
                    if job_items and len(job_items) > 0:
                        print(f"   ✅ 找到职位列表: {selector}")
                        break
                except:
                    continue
            
            if not job_items or len(job_items) == 0:
                print("   ❌ 未找到职位列表")
                return []
            
            print(f"   📝 找到 {len(job_items)} 个职位")
            self.stats["total_found"] += len(job_items)
            self.stats["keywords_used"].add(keyword)
            
            return job_items
            
        except Exception as e:
            print(f"   ❌ 搜索关键词 {keyword} 失败: {str(e)}")
            return []
    
    def apply_job(self, job_info: Dict[str, Any]) -> bool:
        """投递职位"""
        try:
            print(f"\n📝 投递职位: {job_info['title']}")
            print(f"   🏢 公司: {job_info['company']}")
            print(f"   💰 薪资: {job_info['salary_text']}")
            print(f"   📅 经验: {job_info['experience_text']}")
            
            # 点击职位卡片
            job_info['element'].click()
            time.sleep(2)
            
            # 查找投递按钮
            apply_btn = self.page.wait_for_selector('a:has-text("立即沟通")', timeout=5000)
            if not apply_btn:
                print("   ❌ 未找到投递按钮")
                return False
            
            # 点击投递按钮
            apply_btn.click()
            print("   ✅ 点击投递按钮")
            time.sleep(2)
            
            # 填写打招呼内容
            greeting_input = self.page.wait_for_selector('input[type="text"]', timeout=5000)
            if not greeting_input:
                print("   ❌ 未找到打招呼输入框")
                return False
            
            # 生成AI打招呼内容
            greeting_text = self.generate_ai_greeting(job_info['title'], job_info['company'])
            greeting_input.fill(greeting_text)
            print(f"   ✅ 填写打招呼内容: {greeting_text}")
            time.sleep(1)
            
            # 查找发送按钮
            send_selectors = [
                'div:has-text("发送")',
                'span:has-text("发送")',
                'a:has-text("发送")',
                'button:has-text("发送")',
                'button:has-text("提交")',
                'button:has-text("确定")',
                '[class*="send"]',
                '[class*="submit"]',
                '[id*="send"]',
                '[id*="submit"]',
                '*:has-text("发送")',
                '*:has-text("提交")',
                '*:has-text("确定")',
            ]
            
            send_btn = None
            for selector in send_selectors:
                try:
                    element = self.page.wait_for_selector(selector, timeout=1000)
                    if element:
                        element_text = element.text_content() or '无文本'
                        if any(keyword in element_text for keyword in ['发送', '提交', '确定']):
                            print(f"   ✅ 找到发送按钮: {selector}")
                            send_btn = element
                            break
                except:
                    continue
            
            if send_btn:
                # 点击发送按钮
                send_btn.click()
                print("   ✅ 点击发送按钮")
                self.stats["total_applied"] += 1
                self.stats["companies_applied"].add(job_info['company'])
                print(f"   🎉 成功投递第 {self.stats['total_applied']} 份简历")
                time.sleep(2)
                
                # 关闭弹窗
                try:
                    self.page.keyboard.press('Escape')
                    time.sleep(1)
                except:
                    pass
                
                return True
            else:
                print("   ❌ 未找到发送按钮")
                return False
                
        except Exception as e:
            print(f"   ❌ 投递职位失败: {str(e)}")
            return False
    
    def run_delivery(self):
        """运行投递系统"""
        print("🚀 启动完整的Boss直聘投递系统")
        print("=" * 60)
        print("📚 参考项目: https://github.com/loks666/get_jobs.git")
        print("🔧 功能: 筛选、AI打招呼、黑名单、统计")
        print("=" * 60)
        
        print("🔑 Boss直聘Token信息:")
        for key, value in self.boss_tokens.items():
            print(f"   {key}: {value[:30]}...")
        
        print(f"\n📝 投递配置:")
        print(f"   关键词: {self.config['keywords']}")
        print(f"   城市: {self.config['cities']}")
        print(f"   薪资范围: {self.config['salary_range'][0]}-{self.config['salary_range'][1]}k")
        print(f"   经验范围: {self.config['experience_range'][0]}-{self.config['experience_range'][1]}年")
        print(f"   最大投递数: {self.config['max_applications']}")
        print(f"   AI打招呼: {'启用' if self.config['use_ai_greeting'] else '禁用'}")
        print(f"   筛选功能: {'启用' if self.config['enable_filters'] else '禁用'}")
        
        try:
            self.setup_browser()
            
            # 访问Boss直聘主页
            print("\n🔍 访问Boss直聘主页...")
            main_url = "https://www.zhipin.com"
            
            self.page.goto(main_url, wait_until="domcontentloaded", timeout=30000)
            print("✅ 成功访问主页")
            time.sleep(3)
            
            # 开始搜索和投递
            for keyword in self.config['keywords']:
                if self.stats["total_applied"] >= self.config['max_applications']:
                    break
                
                # 搜索职位
                job_items = self.search_jobs(keyword)
                if not job_items:
                    continue
                
                # 处理职位
                for job_item in job_items:
                    if self.stats["total_applied"] >= self.config['max_applications']:
                        break
                    
                    # 提取职位信息
                    job_info = self.extract_job_info(job_item)
                    if not job_info:
                        continue
                    
                    # 应用筛选
                    if not self.apply_filters(job_info):
                        self.stats["total_filtered"] += 1
                        continue
                    
                    # 检查黑名单
                    if self.is_blacklisted(job_info):
                        continue
                    
                    # 投递职位
                    if self.apply_job(job_info):
                        # 随机延迟
                        delay = random.uniform(*self.config['delay_between_applications'])
                        print(f"   ⏳ 延迟 {delay:.1f} 秒...")
                        time.sleep(delay)
                
                # 页面间延迟
                delay = random.uniform(*self.config['delay_between_pages'])
                print(f"\n⏳ 页面间延迟 {delay:.1f} 秒...")
                time.sleep(delay)
            
            # 输出最终统计
            self.print_stats()
            
            # 等待用户观察
            print("\n👀 浏览器窗口已打开，请观察页面...")
            print("   按回车键关闭浏览器...")
            input()
            
        except Exception as e:
            print(f"❌ 投递过程失败: {str(e)}")
        finally:
            self.close_browser()
    
    def print_stats(self):
        """打印统计信息"""
        print(f"\n📊 投递统计:")
        print(f"   🔍 找到职位: {self.stats['total_found']} 个")
        print(f"   ✅ 成功投递: {self.stats['total_applied']} 份简历")
        print(f"   🚫 黑名单过滤: {self.stats['blacklist_filtered']} 个")
        print(f"   💰 薪资过滤: {self.stats['salary_filtered']} 个")
        print(f"   📅 经验过滤: {self.stats['experience_filtered']} 个")
        print(f"   🔄 总过滤: {self.stats['total_filtered']} 个")
        print(f"   🏢 投递公司: {len(self.stats['companies_applied'])} 家")
        print(f"   📝 使用关键词: {len(self.stats['keywords_used'])} 个")
        
        if self.stats['companies_applied']:
            print(f"   🏢 投递公司列表: {', '.join(list(self.stats['companies_applied'])[:5])}")
        
        if self.stats['total_applied'] > 0:
            print("\n🎉 投递成功完成!")
            print("📚 感谢get_jobs项目的启发: https://github.com/loks666/get_jobs.git")
        else:
            print("\n⚠️  未成功投递任何简历")
            print("💡 建议检查网络连接和token有效性")

if __name__ == "__main__":
    delivery_system = BossDeliverySystem()
    delivery_system.run_delivery()
