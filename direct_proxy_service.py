import requests
import socket
import ssl
import threading
import time

class DirectProxyService:
    def __init__(self):
        self.proxy_nodes = [
            'ty-1.rise-fuji.com:443',
            'us-1.regentgrandvalley.com:443', 
            'nl-1.concert-geb.com:443'
        ]
        self.password = 'GUGm7DHtpSx7SuPyUD'
    
    def test_node(self, node):
        """测试代理节点连接"""
        try:
            host, port = node.split(':')
            port = int(port)
            
            # 创建socket连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            sock.close()
            return True
        except Exception as e:
            print(f"节点 {node} 连接失败: {e}")
            return False
    
    def get_working_node(self):
        """获取可用的代理节点"""
        for node in self.proxy_nodes:
            if self.test_node(node):
                print(f"找到可用节点: {node}")
                return node
        return None
    
    def make_request(self, url, **kwargs):
        """通过代理节点发送请求"""
        working_node = self.get_working_node()
        if not working_node:
            raise Exception("没有可用的代理节点")
        
        # 这里简化处理，实际需要实现Trojan协议
        # 暂时直接返回测试结果
        return self.test_google_access()
    
    def test_google_access(self):
        """测试Google访问"""
        try:
            # 直接测试网络连接
            response = requests.get('https://www.google.com', timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Google访问测试失败: {e}")
            return False

# 创建全局实例
direct_proxy_service = DirectProxyService()
