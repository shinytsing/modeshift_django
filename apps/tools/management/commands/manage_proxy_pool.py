"""
代理IP池管理命令
用于管理小红书爬虫的代理IP池
"""

from django.core.management.base import BaseCommand, CommandError
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler


class Command(BaseCommand):
    help = '管理小红书爬虫的代理IP池'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['list', 'add', 'clear', 'test'],
            help='操作类型: list(列出), add(添加), clear(清空), test(测试)'
        )
        parser.add_argument(
            '--proxy',
            type=str,
            help='代理IP地址，格式: http://ip:port 或 https://ip:port'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='测试请求次数 (默认: 5)'
        )

    def handle(self, *args, **options):
        action = options['action']
        crawler = RealSocialMediaCrawler()

        if action == 'list':
            self.list_proxies(crawler)
        elif action == 'add':
            self.add_proxy(crawler, options['proxy'])
        elif action == 'clear':
            self.clear_proxies(crawler)
        elif action == 'test':
            self.test_proxies(crawler, options['count'])

    def list_proxies(self, crawler):
        """列出所有代理IP"""
        self.stdout.write('🌐 代理IP池状态:')
        self.stdout.write(f'  - 代理池大小: {len(crawler.proxy_pool)}')
        self.stdout.write(f'  - 当前代理索引: {crawler.current_proxy_index}')
        
        if crawler.proxy_pool:
            self.stdout.write('  - 代理IP列表:')
            for i, proxy in enumerate(crawler.proxy_pool):
                self.stdout.write(f'    {i+1}. {proxy}')
        else:
            self.stdout.write('  - 代理池为空')

    def add_proxy(self, crawler, proxy_str):
        """添加代理IP"""
        if not proxy_str:
            raise CommandError('请提供代理IP地址')
        
        # 解析代理IP格式
        if proxy_str.startswith('http://'):
            proxy_config = {
                'http': proxy_str,
                'https': proxy_str.replace('http://', 'https://')
            }
        elif proxy_str.startswith('https://'):
            proxy_config = {
                'http': proxy_str.replace('https://', 'http://'),
                'https': proxy_str
            }
        else:
            # 默认使用http
            proxy_config = {
                'http': f'http://{proxy_str}',
                'https': f'https://{proxy_str}'
            }
        
        crawler._add_proxy(proxy_config)
        self.stdout.write(
            self.style.SUCCESS(f'✅ 成功添加代理IP: {proxy_config}')
        )

    def clear_proxies(self, crawler):
        """清空代理IP池"""
        crawler._clear_proxy_pool()
        self.stdout.write(
            self.style.SUCCESS('✅ 代理IP池已清空')
        )

    def test_proxies(self, crawler, count):
        """测试代理IP池"""
        self.stdout.write(f'🧪 测试代理IP池 (请求次数: {count})')
        
        if not crawler.proxy_pool:
            self.stdout.write(
                self.style.WARNING('⚠️ 代理池为空，将使用直接连接')
            )
        
        test_url = 'https://www.xiaohongshu.com/'
        
        for i in range(count):
            self.stdout.write(f'📡 测试请求 {i+1}/{count}...')
            
            try:
                response = crawler._anti_detection_request(test_url)
                if response and response.status_code == 200:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ 请求成功')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  ❌ 请求失败: {response.status_code if response else "无响应"}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ 请求异常: {e}')
                )
        
        self.stdout.write('🏁 代理IP测试完成')