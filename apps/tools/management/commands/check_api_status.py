import logging
from django.core.management.base import BaseCommand
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler
import requests
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '检查小红书API服务状态'

    def add_arguments(self, parser):
        parser.add_argument('--retry', type=int, default=3, help='重试次数')
        parser.add_argument('--interval', type=int, default=30, help='检查间隔（秒）')

    def handle(self, *args, **options):
        retry_count = options['retry']
        interval = options['interval']
        
        crawler = RealSocialMediaCrawler()
        
        self.stdout.write('=' * 80)
        self.stdout.write('🔍 小红书API服务状态检查')
        self.stdout.write('=' * 80)
        
        # 测试的API端点
        test_endpoints = [
            {
                'name': '首页API',
                'url': 'https://www.xiaohongshu.com/api/sns/web/v1/homefeed',
                'method': 'GET'
            },
            {
                'name': '搜索用户API',
                'url': 'https://www.xiaohongshu.com/api/sns/web/v1/search/user',
                'method': 'GET',
                'params': {'keyword': 'test', 'page': 1, 'page_size': 10}
            },
            {
                'name': '搜索笔记API',
                'url': 'https://www.xiaohongshu.com/api/sns/web/v1/search/notes',
                'method': 'GET',
                'params': {'keyword': 'test', 'page': 1, 'page_size': 10}
            }
        ]
        
        headers = crawler._get_xiaohongshu_headers({
            'Accept': 'application/json, text/plain, */*'
        })
        
        for attempt in range(retry_count):
            self.stdout.write(f'\n🔄 第 {attempt + 1} 次检查:')
            self.stdout.write('-' * 50)
            
            all_working = True
            
            for endpoint in test_endpoints:
                try:
                    if endpoint['method'] == 'GET':
                        response = requests.get(
                            endpoint['url'], 
                            headers=headers, 
                            params=endpoint.get('params', {}),
                            timeout=10
                        )
                    else:
                        response = requests.post(
                            endpoint['url'], 
                            headers=headers, 
                            json=endpoint.get('params', {}),
                            timeout=10
                        )
                    
                    if response.status_code == 200:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ {endpoint["name"]}: 正常')
                        )
                    elif response.status_code == 500:
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ {endpoint["name"]}: 服务故障 (500)')
                        )
                        all_working = False
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠️ {endpoint["name"]}: 其他错误 ({response.status_code})')
                        )
                        all_working = False
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ {endpoint["name"]}: 异常 - {e}')
                    )
                    all_working = False
            
            if all_working:
                self.stdout.write(
                    self.style.SUCCESS('\n🎉 所有API服务正常！搜索功能可以正常使用。')
                )
                break
            else:
                if attempt < retry_count - 1:
                    self.stdout.write(
                        self.style.WARNING(f'\n⏰ 等待 {interval} 秒后重试...')
                    )
                    time.sleep(interval)
                else:
                    self.stdout.write(
                        self.style.ERROR('\n❌ API服务仍然不可用')
                    )
                    self.stdout.write('💡 建议：')
                    self.stdout.write('  1. 等待服务恢复')
                    self.stdout.write('  2. 使用已知用户映射')
                    self.stdout.write('  3. 使用网页搜索功能')
        
        # 测试网页访问
        self.stdout.write('\n🌐 网页访问测试:')
        try:
            response = requests.get('https://www.xiaohongshu.com/', headers=headers, timeout=10)
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('  ✅ 网页访问正常'))
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ 网页访问异常: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 网页访问异常: {e}'))
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('🏁 API服务状态检查完成')
        self.stdout.write('=' * 80)
