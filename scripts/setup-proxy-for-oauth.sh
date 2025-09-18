#!/bin/bash

# 为Google OAuth配置代理服务器

echo "🌐 配置代理服务器解决Google OAuth问题..."

# 1. 安装代理工具
echo "📦 安装代理工具..."
ssh root@47.103.143.152 "apt update && apt install -y proxychains4"

# 2. 配置代理
echo "⚙️ 配置代理..."
ssh root@47.103.143.152 "cat > /etc/proxychains4.conf << 'EOF'
# proxychains.conf  VER 4.x
strict_chain
proxy_dns 
remote_dns_subnet 224
tcp_read_time_out 15000
tcp_connect_time_out 8000
localnet 127.0.0.0/255.0.0.0
quiet_mode

[ProxyList]
# 添加可用的代理服务器
# http 127.0.0.1 8080
# socks5 127.0.0.1 1080
EOF"

# 3. 测试代理连接
echo "🧪 测试代理连接..."
ssh root@47.103.143.152 "proxychains4 curl -I https://www.google.com/ | head -1"

echo "✅ 代理配置完成"
