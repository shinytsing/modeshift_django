#!/bin/bash

# 配置Django使用代理访问Google OAuth

echo "🔧 配置Django使用代理访问Google OAuth..."

# 1. 安装requests[socks]支持
echo "📦 安装代理支持库..."
ssh root@47.103.143.152 "cd /root/modeshift_django && source venv/bin/activate && pip install requests[socks]"

# 2. 创建代理配置
echo "⚙️ 创建代理配置..."
ssh root@47.103.143.152 "cd /root/modeshift_django && cat > proxy_config.py << 'EOF'
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 代理配置
PROXY_CONFIG = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}

# 创建带代理的session
def create_proxy_session():
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # 设置代理
    session.proxies.update(PROXY_CONFIG)
    
    return session

# 测试代理连接
def test_proxy_connection():
    try:
        session = create_proxy_session()
        response = session.get('https://www.google.com', timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f'代理连接测试失败: {e}')
        return False
EOF"

# 3. 修改Django设置以使用代理
echo "🔧 修改Django设置..."
ssh root@47.103.143.152 "cd /root/modeshift_django && cat >> config/settings/base.py << 'EOF'

# 代理配置
import os
import requests

# 设置代理环境变量
if os.getenv('USE_PROXY', 'False').lower() == 'true':
    PROXY_URL = os.getenv('PROXY_URL', 'socks5://127.0.0.1:1080')
    os.environ['HTTP_PROXY'] = PROXY_URL
    os.environ['HTTPS_PROXY'] = PROXY_URL
    
    # 配置requests使用代理
    import requests
    requests.Session().proxies = {
        'http': PROXY_URL,
        'https': PROXY_URL
    }
EOF"

# 4. 创建代理启动脚本
echo "🚀 创建代理启动脚本..."
ssh root@47.103.143.152 "cd /root/modeshift_django && cat > start-with-proxy.sh << 'EOF'
#!/bin/bash

# 设置代理环境变量
export USE_PROXY=true
export PROXY_URL=socks5://127.0.0.1:1080

# 启动Django服务
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
EOF"

ssh root@47.103.143.152 "chmod +x /root/modeshift_django/start-with-proxy.sh"

# 5. 测试配置
echo "🧪 测试配置..."
ssh root@47.103.143.152 "cd /root/modeshift_django && source venv/bin/activate && python -c \"
import proxy_config
if proxy_config.test_proxy_connection():
    print('✅ 代理连接测试成功')
else:
    print('❌ 代理连接测试失败')
\""

echo "✅ Django代理配置完成"
echo "💡 使用方法："
echo "   1. 启动代理服务器 (如shadowsocks)"
echo "   2. 运行: ./start-with-proxy.sh"
echo "   3. 或者设置环境变量: export USE_PROXY=true"
