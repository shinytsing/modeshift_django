#!/bin/bash

# 设置免费代理服务解决Google OAuth问题

echo "🌐 设置免费代理服务..."

# 1. 安装代理工具
echo "📦 安装代理工具..."
ssh root@47.103.143.152 "apt install -y tinyproxy"

# 2. 配置tinyproxy
echo "⚙️ 配置tinyproxy..."
ssh root@47.103.143.152 "cat > /etc/tinyproxy/tinyproxy.conf << 'EOF'
# Tinyproxy配置文件
User tinyproxy
Group tinyproxy
Port 8888
Timeout 600
DefaultErrorFile \"/usr/share/tinyproxy/default.html\"
StatFile \"/usr/share/tinyproxy/stats.html\"
Logfile \"/var/log/tinyproxy/tinyproxy.log\"
LogLevel Info
PidFile \"/var/run/tinyproxy/tinyproxy.pid\"
MaxClients 100
MinSpareServers 5
MaxSpareServers 20
StartServers 10
MaxRequestsPerChild 0
ViaProxyName \"tinyproxy\"
DisableViaHeader Yes
FilterDefaultDeny Yes
Filter \"/etc/tinyproxy/filter\"
Anonymous Yes
ConnectPort 443
ConnectPort 563
EOF"

# 3. 创建过滤器（允许所有连接）
ssh root@47.103.143.152 "echo '.*' > /etc/tinyproxy/filter"

# 4. 启动tinyproxy
echo "🚀 启动tinyproxy..."
ssh root@47.103.143.152 "systemctl enable tinyproxy && systemctl start tinyproxy"

# 5. 测试代理
echo "🧪 测试代理..."
ssh root@47.103.143.152 "curl -x http://127.0.0.1:8888 -I https://www.google.com/ | head -1"

# 6. 配置Django使用本地代理
echo "🔧 配置Django使用本地代理..."
ssh root@47.103.143.152 "cd /root/modeshift_django && cat >> config/settings/base.py << 'EOF'

# 本地代理配置
import os
import requests

# 设置本地代理
LOCAL_PROXY = 'http://127.0.0.1:8888'

# 配置requests使用代理
def configure_proxy():
    proxies = {
        'http': LOCAL_PROXY,
        'https': LOCAL_PROXY
    }
    
    # 为所有requests设置代理
    import requests
    requests.Session().proxies = proxies
    
    # 设置环境变量
    os.environ['HTTP_PROXY'] = LOCAL_PROXY
    os.environ['HTTPS_PROXY'] = LOCAL_PROXY

# 自动配置代理
configure_proxy()
EOF"

# 7. 重启Django服务
echo "🔄 重启Django服务..."
ssh root@47.103.143.152 "cd /root/modeshift_django && pkill -f gunicorn && sleep 3 && nohup gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 --preload --access-logfile logs/gunicorn_access.log --error-logfile logs/gunicorn_error.log config.wsgi:application > /dev/null 2>&1 &"

# 8. 测试服务
echo "🧪 测试服务..."
sleep 5
curl -s -o /dev/null -w '%{http_code}' https://shenyiqing.xin/ && echo " - 首页状态"

echo "✅ 免费代理服务配置完成"
echo "💡 代理服务信息："
echo "   - 代理地址: http://127.0.0.1:8888"
echo "   - 状态: $(ssh root@47.103.143.152 'systemctl is-active tinyproxy')"
echo "   - 日志: /var/log/tinyproxy/tinyproxy.log"
