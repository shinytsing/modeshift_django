#!/bin/bash
# 修复服务器Clash配置

echo "=== 修复服务器Clash配置 ==="

# 连接到服务器修复Clash
ssh root@47.103.143.152 << 'EOF'
echo "1. 停止现有服务..."
systemctl stop clash 2>/dev/null || true

echo "2. 下载Clash (使用镜像站)..."
cd /opt
# 使用镜像站下载
wget -O clash.gz "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-linux-amd64-v1.18.0.gz" || \
wget -O clash.gz "https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-linux-amd64-v1.18.0.gz"

if [ -f "clash.gz" ]; then
    gunzip clash.gz
    chmod +x clash
    echo "Clash下载成功"
else
    echo "下载失败，尝试其他方法..."
    # 备用方案：使用预编译的Clash
    curl -L -o clash "https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-linux-amd64-v1.18.0" || \
    wget -O clash "https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-linux-amd64-v1.18.0"
    chmod +x clash
fi

echo "3. 验证Clash文件..."
ls -la /opt/clash
file /opt/clash

echo "4. 启动Clash服务..."
systemctl start clash
sleep 3

echo "5. 检查服务状态..."
systemctl status clash --no-pager

echo "6. 测试代理连接..."
sleep 5
curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 10 || echo "代理测试失败"

echo "7. 检查端口监听..."
netstat -tlnp | grep -E "(7890|7891|9090)"

echo "=== 修复完成 ==="
EOF

echo "修复脚本执行完成"
