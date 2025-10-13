import logging
from django.core.management.base import BaseCommand
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler
import requests
import json

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '检查IP限制状态和提供解决方案'

    def add_arguments(self, parser):
        parser.add_argument('--add-proxy', type=str, help='添加代理IP，格式: http://ip:port')
        parser.add_argument('--test-proxy', action='store_true', help='测试代理IP')

    def handle(self, *args, **options):
        crawler = RealSocialMediaCrawler()
        
        self.stdout.write('=' * 80)
        self.stdout.write('🔍 IP限制状态检查')
        self.stdout.write('=' * 80)
        
        # 1. 检查当前IP信息
        self.stdout.write('\n🌍 1. 当前IP信息:')
        try:
            response = requests.get('https://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                ip_info = response.json()
                current_ip = ip_info.get('origin', '未知')
                self.stdout.write(f'  当前IP: {current_ip}')
                
                # 获取IP地理位置
                try:
                    geo_response = requests.get(f'https://ipapi.co/{current_ip}/json/', timeout=10)
                    if geo_response.status_code == 200:
                        geo_info = geo_response.json()
                        self.stdout.write(f'  国家: {geo_info.get("country_name", "未知")}')
                        self.stdout.write(f'  地区: {geo_info.get("region", "未知")}')
                        self.stdout.write(f'  城市: {geo_info.get("city", "未知")}')
                        self.stdout.write(f'  ISP: {geo_info.get("org", "未知")}')
                except Exception as e:
                    self.stdout.write(f'  地理位置获取失败: {e}')
            else:
                self.stdout.write('  无法获取IP信息')
        except Exception as e:
            self.stdout.write(f'  IP检查失败: {e}')
        
        # 2. 检查IP是否被限制
        self.stdout.write('\n🚫 2. IP限制检查:')
        is_blocked = crawler._check_ip_blocked()
        
        if is_blocked:
            self.stdout.write(self.style.ERROR('  ❌ IP被限制'))
            self.stdout.write('  所有小红书API返回500错误')
            self.stdout.write('  错误信息: create invoker failed, service: jarvis-gateway-default...')
        else:
            self.stdout.write(self.style.SUCCESS('  ✅ IP状态正常'))
        
        # 3. 测试API访问
        self.stdout.write('\n🌐 3. API访问测试:')
        test_apis = [
            'https://www.xiaohongshu.com/api/sns/web/v1/homefeed',
            'https://www.xiaohongshu.com/api/sns/web/v1/search/user'
        ]
        
        for api in test_apis:
            try:
                headers = crawler._get_xiaohongshu_headers()
                response = requests.get(api, headers=headers, timeout=10)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f'  ✅ {api}: 正常'))
                elif response.status_code == 500:
                    self.stdout.write(self.style.ERROR(f'  ❌ {api}: 被限制 (500)'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠️ {api}: 其他错误 ({response.status_code})'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ {api}: 异常 - {e}'))
        
        # 4. 代理IP状态
        self.stdout.write('\n🌐 4. 代理IP状态:')
        if crawler.proxy_pool:
            self.stdout.write(f'  代理池大小: {len(crawler.proxy_pool)}')
            for i, proxy in enumerate(crawler.proxy_pool, 1):
                self.stdout.write(f'  {i}. {proxy}')
        else:
            self.stdout.write('  代理池为空')
        
        # 5. 添加代理IP
        if options.get('add_proxy'):
            proxy_url = options['add_proxy']
            self.stdout.write(f'\n➕ 添加代理IP: {proxy_url}')
            try:
                proxy_config = {'http': proxy_url, 'https': proxy_url}
                crawler._add_proxy(proxy_config)
                self.stdout.write(self.style.SUCCESS('  ✅ 代理IP添加成功'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ 代理IP添加失败: {e}'))
        
        # 6. 测试代理IP
        if options.get('test_proxy') and crawler.proxy_pool:
            self.stdout.write('\n🧪 6. 代理IP测试:')
            for i, proxy in enumerate(crawler.proxy_pool, 1):
                self.stdout.write(f'  测试代理 {i}: {proxy}')
                try:
                    test_url = 'https://www.xiaohongshu.com/api/sns/web/v1/homefeed'
                    headers = crawler._get_xiaohongshu_headers()
                    response = requests.get(test_url, headers=headers, proxies=proxy, timeout=10)
                    if response.status_code == 200:
                        self.stdout.write(self.style.SUCCESS('    ✅ 代理工作正常'))
                    else:
                        self.stdout.write(self.style.ERROR(f'    ❌ 代理失败: {response.status_code}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    ❌ 代理异常: {e}'))
        
        # 7. 解决方案建议
        self.stdout.write('\n💡 7. 解决方案建议:')
        if is_blocked:
            self.stdout.write('  🚫 IP被限制时的解决方案:')
            self.stdout.write('    1. 使用代理IP:')
            self.stdout.write('       python manage.py check_ip_status --add-proxy http://proxy_ip:port')
            self.stdout.write('    2. 使用VPN或更换网络环境')
            self.stdout.write('    3. 等待IP自动解封（通常24-48小时）')
            self.stdout.write('    4. 联系网络服务提供商')
            self.stdout.write('    5. 使用已知用户映射（绕过搜索功能）')
        else:
            self.stdout.write('  ✅ IP状态正常，可以正常使用搜索功能')
        
        self.stdout.write('\n📋 8. 使用建议:')
        self.stdout.write('  - 定期检查IP状态: python manage.py check_ip_status')
        self.stdout.write('  - 添加代理IP: python manage.py check_ip_status --add-proxy http://ip:port')
        self.stdout.write('  - 测试代理IP: python manage.py check_ip_status --test-proxy')
        self.stdout.write('  - 管理代理池: python manage.py manage_proxy_pool list')
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('🏁 IP状态检查完成')
        self.stdout.write('=' * 80)
