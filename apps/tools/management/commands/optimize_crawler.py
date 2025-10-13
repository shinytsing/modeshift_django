import logging
from django.core.management.base import BaseCommand
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler
import requests
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '优化爬虫性能和请求频次'

    def add_arguments(self, parser):
        parser.add_argument('--test-delay', action='store_true', help='测试优化后的延迟效果')
        parser.add_argument('--add-proxy', type=str, help='添加代理IP，格式: http://ip:port')
        parser.add_argument('--test-search', action='store_true', help='测试搜索功能')

    def handle(self, *args, **options):
        crawler = RealSocialMediaCrawler()
        
        self.stdout.write('=' * 80)
        self.stdout.write('🚀 爬虫性能优化')
        self.stdout.write('=' * 80)
        
        # 1. 显示当前配置
        self.stdout.write('\n📋 1. 当前配置:')
        self.stdout.write(f'  请求延迟层级: {len(crawler.request_delay_ranges)}')
        for i, delay_range in enumerate(crawler.request_delay_ranges, 1):
            self.stdout.write(f'    层级{i}: {delay_range[0]}-{delay_range[1]}秒')
        
        self.stdout.write(f'  代理池大小: {len(crawler.proxy_pool)}')
        self.stdout.write(f'  IP限制状态: {"被限制" if crawler.ip_blocked else "正常"}')
        
        # 2. 优化请求延迟
        self.stdout.write('\n⏰ 2. 优化请求延迟:')
        # 设置更保守的延迟策略
        crawler.request_delay_ranges = [
            (15, 30),   # 基础延迟：15-30秒
            (30, 60),   # 中等延迟：30-60秒
            (60, 120),  # 长延迟：60-120秒
            (120, 300), # 超长延迟：120-300秒（2-5分钟）
        ]
        
        self.stdout.write('  优化后的延迟设置:')
        for i, delay_range in enumerate(crawler.request_delay_ranges, 1):
            self.stdout.write(f'    层级{i}: {delay_range[0]}-{delay_range[1]}秒')
        
        self.stdout.write(self.style.SUCCESS('  ✅ 请求延迟已优化为更保守的策略'))
        
        # 3. 添加代理IP
        if options.get('add_proxy'):
            proxy_url = options['add_proxy']
            self.stdout.write(f'\n➕ 3. 添加代理IP: {proxy_url}')
            try:
                proxy_config = {'http': proxy_url, 'https': proxy_url}
                crawler._add_proxy(proxy_config)
                self.stdout.write(self.style.SUCCESS('  ✅ 代理IP添加成功'))
                
                # 测试代理IP
                if self._test_proxy(proxy_config):
                    self.stdout.write(self.style.SUCCESS('  ✅ 代理IP测试通过'))
                else:
                    self.stdout.write(self.style.WARNING('  ⚠️ 代理IP测试失败，但已添加'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ 代理IP添加失败: {e}'))
        
        # 4. 测试延迟效果
        if options.get('test_delay'):
            self.stdout.write('\n🧪 4. 测试延迟效果:')
            for i in range(3):
                delay = crawler._get_smart_delay()
                self.stdout.write(f'  测试 {i+1}: 延迟 {delay:.1f} 秒')
                time.sleep(2)  # 实际测试中只等待2秒
        
        # 5. 测试搜索功能
        if options.get('test_search'):
            self.stdout.write('\n🔍 5. 测试搜索功能:')
            test_users = ['吃定彩虹糖', '小宁姐姐']
            
            for username in test_users:
                self.stdout.write(f'  测试用户: {username}')
                try:
                    # 使用优化后的延迟进行搜索
                    delay = crawler._get_smart_delay()
                    self.stdout.write(f'    延迟: {delay:.1f} 秒')
                    
                    # 测试搜索API
                    search_url = 'https://www.xiaohongshu.com/api/sns/web/v1/search/user'
                    headers = crawler._get_xiaohongshu_headers({
                        'Accept': 'application/json, text/plain, */*',
                        'Referer': 'https://www.xiaohongshu.com/search_result'
                    })
                    params = {'keyword': username, 'page': 1, 'page_size': 10}
                    
                    response = crawler._anti_detection_request(search_url, headers=headers, params=params)
                    
                    if response and response.status_code == 200:
                        self.stdout.write(self.style.SUCCESS('    ✅ 搜索成功'))
                    else:
                        status_code = response.status_code if response else '无响应'
                        self.stdout.write(self.style.ERROR(f'    ❌ 搜索失败: {status_code}'))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    ❌ 搜索异常: {e}'))
        
        # 6. 提供解决方案建议
        self.stdout.write('\n💡 6. 解决方案建议:')
        
        if crawler.ip_blocked:
            self.stdout.write('  🚫 IP被限制时的解决方案:')
            self.stdout.write('    1. 使用代理IP:')
            self.stdout.write('       python manage.py optimize_crawler --add-proxy http://proxy_ip:port')
            self.stdout.write('    2. 等待IP解封（通常24-48小时）')
            self.stdout.write('    3. 使用已知用户映射（绕过搜索）')
            self.stdout.write('    4. 更换网络环境或服务器')
        else:
            self.stdout.write('  ✅ IP状态正常，建议：')
            self.stdout.write('    1. 使用优化后的延迟设置')
            self.stdout.write('    2. 避免频繁请求')
            self.stdout.write('    3. 定期检查IP状态')
        
        # 7. 使用指南
        self.stdout.write('\n📖 7. 使用指南:')
        self.stdout.write('  🔧 优化命令:')
        self.stdout.write('    python manage.py optimize_crawler --test-delay')
        self.stdout.write('    python manage.py optimize_crawler --add-proxy http://ip:port')
        self.stdout.write('    python manage.py optimize_crawler --test-search')
        
        self.stdout.write('  📊 检查命令:')
        self.stdout.write('    python manage.py check_ip_status')
        self.stdout.write('    python manage.py test_user_mapping 用户名 --crawl')
        
        self.stdout.write('  🎯 推荐策略:')
        self.stdout.write('    1. 优先使用已知用户映射')
        self.stdout.write('    2. 必要时使用代理IP')
        self.stdout.write('    3. 保持合理的请求间隔')
        self.stdout.write('    4. 定期监控IP状态')
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('🏁 爬虫性能优化完成')
        self.stdout.write('=' * 80)
    
    def _test_proxy(self, proxy):
        """测试代理IP是否可用"""
        try:
            test_url = 'https://httpbin.org/ip'
            response = requests.get(test_url, proxies=proxy, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
