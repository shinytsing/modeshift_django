import logging
from django.core.management.base import BaseCommand
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler
import requests
import random
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '设置代理IP和优化请求频次'

    def add_arguments(self, parser):
        parser.add_argument('--add-proxy', type=str, help='添加代理IP，格式: http://ip:port')
        parser.add_argument('--auto-proxy', action='store_true', help='自动获取免费代理IP')
        parser.add_argument('--optimize-delay', action='store_true', help='优化请求延迟设置')
        parser.add_argument('--test-all', action='store_true', help='测试所有代理IP')

    def handle(self, *args, **options):
        crawler = RealSocialMediaCrawler()
        
        self.stdout.write('=' * 80)
        self.stdout.write('🔧 代理IP和请求频次优化设置')
        self.stdout.write('=' * 80)
        
        # 1. 优化请求延迟设置
        if options.get('optimize_delay'):
            self.stdout.write('\n⏰ 1. 优化请求延迟设置:')
            self.stdout.write('  当前延迟设置:')
            for i, delay_range in enumerate(crawler.request_delay_ranges, 1):
                self.stdout.write(f'    层级{i}: {delay_range[0]}-{delay_range[1]}秒')
            
            # 设置更保守的延迟
            crawler.request_delay_ranges = [
                (10, 20),   # 基础延迟：10-20秒
                (20, 40),   # 中等延迟：20-40秒
                (40, 60),   # 长延迟：40-60秒
                (60, 120),  # 超长延迟：60-120秒
            ]
            
            self.stdout.write('  优化后的延迟设置:')
            for i, delay_range in enumerate(crawler.request_delay_ranges, 1):
                self.stdout.write(f'    层级{i}: {delay_range[0]}-{delay_range[1]}秒')
            
            self.stdout.write(self.style.SUCCESS('  ✅ 请求延迟已优化'))
        
        # 2. 添加代理IP
        if options.get('add_proxy'):
            proxy_url = options['add_proxy']
            self.stdout.write(f'\n➕ 2. 添加代理IP: {proxy_url}')
            try:
                proxy_config = {'http': proxy_url, 'https': proxy_url}
                crawler._add_proxy(proxy_config)
                self.stdout.write(self.style.SUCCESS('  ✅ 代理IP添加成功'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ 代理IP添加失败: {e}'))
        
        # 3. 自动获取免费代理IP
        if options.get('auto_proxy'):
            self.stdout.write('\n🌐 3. 自动获取免费代理IP:')
            free_proxies = self._get_free_proxies()
            
            if free_proxies:
                self.stdout.write(f'  找到 {len(free_proxies)} 个免费代理IP')
                for proxy in free_proxies[:5]:  # 只添加前5个
                    try:
                        crawler._add_proxy(proxy)
                        self.stdout.write(f'  ✅ 添加代理: {proxy}')
                    except Exception as e:
                        self.stdout.write(f'  ❌ 添加代理失败: {e}')
            else:
                self.stdout.write('  ❌ 未找到可用的免费代理IP')
        
        # 4. 测试所有代理IP
        if options.get('test_all') or crawler.proxy_pool:
            self.stdout.write('\n🧪 4. 测试代理IP:')
            if crawler.proxy_pool:
                working_proxies = []
                for i, proxy in enumerate(crawler.proxy_pool, 1):
                    self.stdout.write(f'  测试代理 {i}: {proxy}')
                    if self._test_proxy(proxy):
                        self.stdout.write(self.style.SUCCESS('    ✅ 代理工作正常'))
                        working_proxies.append(proxy)
                    else:
                        self.stdout.write(self.style.ERROR('    ❌ 代理不可用'))
                
                self.stdout.write(f'\n📊 代理测试结果: {len(working_proxies)}/{len(crawler.proxy_pool)} 个代理可用')
                
                # 移除不可用的代理
                crawler.proxy_pool = working_proxies
                if working_proxies:
                    self.stdout.write(self.style.SUCCESS('  ✅ 已清理不可用的代理IP'))
            else:
                self.stdout.write('  代理池为空')
        
        # 5. 显示当前状态
        self.stdout.write('\n📋 5. 当前状态:')
        self.stdout.write(f'  代理池大小: {len(crawler.proxy_pool)}')
        self.stdout.write(f'  请求延迟层级: {len(crawler.request_delay_ranges)}')
        ip_status = "被限制" if crawler.ip_blocked else "正常"
        self.stdout.write(f'  IP限制状态: {ip_status}')
        
        # 6. 使用建议
        self.stdout.write('\n💡 6. 使用建议:')
        if crawler.proxy_pool:
            self.stdout.write('  ✅ 有可用代理IP，搜索功能应该可以正常工作')
            self.stdout.write('  📝 建议：定期测试代理IP有效性')
        else:
            self.stdout.write('  ⚠️ 无可用代理IP，建议：')
            self.stdout.write('    1. 添加代理IP: --add-proxy http://ip:port')
            self.stdout.write('    2. 自动获取免费代理: --auto-proxy')
            self.stdout.write('    3. 使用已知用户映射（绕过搜索）')
        
        self.stdout.write('\n🔧 7. 常用命令:')
        self.stdout.write('  python manage.py setup_proxy --optimize-delay')
        self.stdout.write('  python manage.py setup_proxy --add-proxy http://ip:port')
        self.stdout.write('  python manage.py setup_proxy --auto-proxy')
        self.stdout.write('  python manage.py setup_proxy --test-all')
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('🏁 代理IP和请求频次优化完成')
        self.stdout.write('=' * 80)
    
    def _get_free_proxies(self):
        """获取免费代理IP"""
        proxies = []
        
        # 免费代理IP源（示例）
        free_proxy_sources = [
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
        ]
        
        for source in free_proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxy_list = response.text.strip().split('\n')
                    for proxy in proxy_list[:10]:  # 只取前10个
                        if ':' in proxy:
                            ip, port = proxy.strip().split(':')
                            proxy_config = {
                                'http': f'http://{ip}:{port}',
                                'https': f'http://{ip}:{port}'
                            }
                            proxies.append(proxy_config)
                break  # 成功获取一个源就停止
            except Exception as e:
                logger.debug(f'获取免费代理失败: {e}')
                continue
        
        return proxies
    
    def _test_proxy(self, proxy):
        """测试代理IP是否可用"""
        try:
            test_url = 'https://httpbin.org/ip'
            response = requests.get(test_url, proxies=proxy, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
