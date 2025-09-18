import requests
import socket
import ssl

class ProxyConfig:
    def __init__(self):
        self.proxy_hosts = [
            'iplc-hk-1.trojanwheel.com',
            'ty-1.rise-fuji.com', 
            'us-1.regentgrandvalley.com',
            'sg-1.victoriamitrepeak.com',
            'nl-1.concert-geb.com'
        ]
        self.proxy_port = 443
        self.proxy_password = 'GUGm7DHtpSx7SuPyUD'
    
    def test_proxy_connection(self, host):
        """测试代理节点连接"""
        try:
            # 创建socket连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, self.proxy_port))
            
            # 发送Trojan协议握手
            # 这里简化处理，实际需要完整的Trojan协议实现
            sock.close()
            return True
        except Exception as e:
            print(f"代理节点 {host} 连接失败: {e}")
            return False
    
    def get_working_proxy(self):
        """获取可用的代理节点"""
        for host in self.proxy_hosts:
            if self.test_proxy_connection(host):
                return host
        return None
    
    def make_request_with_proxy(self, url):
        """使用代理发送请求"""
        proxy_host = self.get_working_proxy()
        if not proxy_host:
            print("没有可用的代理节点")
            return None
        
        try:
            # 这里需要实现Trojan协议或使用其他方法
            # 暂时直接尝试访问
            response = requests.get(url, timeout=15)
            return response
        except Exception as e:
            print(f"请求失败: {e}")
            return None

# 测试代理配置
if __name__ == "__main__":
    proxy_config = ProxyConfig()
    print("测试代理节点连接...")
    
    for host in proxy_config.proxy_hosts:
        print(f"测试 {host}...")
        if proxy_config.test_proxy_connection(host):
            print(f"✅ {host} 连接成功")
        else:
            print(f"❌ {host} 连接失败")
