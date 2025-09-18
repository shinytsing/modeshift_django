import requests
import os
import time
from urllib.parse import urlparse

class FinalProxySolution:
    """最终代理解决方案"""
    
    def __init__(self):
        self.session = requests.Session()
        self.proxy_nodes = [
            'ty-1.rise-fuji.com:443',
            'us-1.regentgrandvalley.com:443', 
            'nl-1.concert-geb.com:443'
        ]
        self.password = 'GUGm7DHtpSx7SuPyUD'
    
    def test_direct_access(self):
        """测试直接访问"""
        try:
            print('测试直接访问Google...')
            response = self.session.get('https://www.google.com', timeout=15)
            return response.status_code == 200
        except Exception as e:
            print(f'直接访问失败: {e}')
            return False
    
    def test_with_proxy(self, proxy_url):
        """测试使用代理访问"""
        try:
            proxies = {'http': proxy_url, 'https': proxy_url}
            response = self.session.get('https://www.google.com', proxies=proxies, timeout=15)
            return response.status_code == 200
        except Exception as e:
            print(f'代理访问失败: {e}')
            return False
    
    def make_request(self, url, method='GET', **kwargs):
        """发送请求"""
        try:
            # 首先尝试直接访问
            if self.test_direct_access():
                print('使用直接访问')
                return self.session.request(method, url, **kwargs)
            
            # 如果直接访问失败，尝试使用代理
            for node in self.proxy_nodes:
                proxy_url = f'http://{node}'
                if self.test_with_proxy(proxy_url):
                    print(f'使用代理: {proxy_url}')
                    proxies = {'http': proxy_url, 'https': proxy_url}
                    return self.session.request(method, url, proxies=proxies, **kwargs)
            
            # 如果所有方法都失败，返回错误
            raise Exception('无法访问目标URL')
            
        except Exception as e:
            print(f'请求失败: {e}')
            return None

# 创建全局实例
final_proxy_solution = FinalProxySolution()
