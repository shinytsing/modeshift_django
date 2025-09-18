import requests
import os
import time
from django.conf import settings

class SimpleGoogleAccess:
    """简单的Google访问解决方案"""
    
    def __init__(self):
        self.session = requests.Session()
        self.max_retries = 3
        self.retry_delay = 5
    
    def test_google_access(self):
        """测试Google访问"""
        for attempt in range(self.max_retries):
            try:
                print(f'尝试访问Google (第 {attempt + 1} 次)...')
                
                # 尝试直接访问
                response = self.session.get('https://www.google.com', timeout=15)
                if response.status_code == 200:
                    print('✅ 直接访问Google成功!')
                    return True
                
                # 如果直接访问失败，尝试使用环境变量中的代理
                http_proxy = os.getenv('http_proxy')
                https_proxy = os.getenv('https_proxy')
                
                if http_proxy or https_proxy:
                    proxies = {
                        'http': http_proxy,
                        'https': https_proxy
                    }
                    response = self.session.get('https://www.google.com', proxies=proxies, timeout=15)
                    if response.status_code == 200:
                        print('✅ 通过环境变量代理访问Google成功!')
                        return True
                
                print(f'第 {attempt + 1} 次尝试失败')
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                print(f'第 {attempt + 1} 次尝试错误: {e}')
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return False
    
    def make_request(self, url, method='GET', **kwargs):
        """发送请求"""
        try:
            # 首先尝试直接访问
            response = self.session.request(method, url, timeout=15, **kwargs)
            if response.status_code == 200:
                return response
            
            # 如果直接访问失败，尝试使用代理
            http_proxy = os.getenv('http_proxy')
            https_proxy = os.getenv('https_proxy')
            
            if http_proxy or https_proxy:
                proxies = {
                    'http': http_proxy,
                    'https': https_proxy
                }
                response = self.session.request(method, url, proxies=proxies, timeout=15, **kwargs)
                if response.status_code == 200:
                    return response
            
            return response
            
        except Exception as e:
            print(f'请求失败: {e}')
            return None

# 创建全局实例
simple_google_access = SimpleGoogleAccess()
