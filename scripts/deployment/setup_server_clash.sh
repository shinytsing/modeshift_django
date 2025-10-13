#!/bin/bash

# 服务器Clash代理设置脚本
# 服务器IP: 47.103.143.152
# 用户: root
# 密码: GJc9d5&b5z

set -e

echo "=== 服务器Clash代理设置脚本 ==="
echo "目标服务器: 47.103.143.152"
echo "开始设置..."

# 服务器连接信息
SERVER_IP="47.103.143.152"
SERVER_USER="root"
SERVER_PASSWORD="GJc9d5&b5z"

# 检查是否安装了sshpass
if ! command -v sshpass &> /dev/null; then
    echo "安装sshpass..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install sshpass
        else
            echo "请先安装Homebrew: https://brew.sh/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update && sudo apt-get install -y sshpass
    else
        echo "不支持的操作系统: $OSTYPE"
        exit 1
    fi
fi

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "临时目录: $TEMP_DIR"

# 复制Clash配置文件
cp clash_embedded/config.yaml "$TEMP_DIR/clash_config.yaml"

# 创建Clash安装脚本
cat > "$TEMP_DIR/install_clash.sh" << 'EOF'
#!/bin/bash

set -e

echo "=== 在服务器上安装Clash ==="

# 更新系统包
echo "更新系统包..."
apt-get update

# 安装必要的依赖
echo "安装依赖..."
apt-get install -y wget curl unzip

# 创建clash目录
mkdir -p /opt/clash
cd /opt/clash

# 下载Clash
echo "下载Clash..."
CLASH_VERSION="v1.18.0"
wget -O clash.gz "https://github.com/Dreamacro/clash/releases/download/${CLASH_VERSION}/clash-linux-amd64-${CLASH_VERSION}.gz"
gunzip clash.gz
chmod +x clash

# 创建systemd服务文件
cat > /etc/systemd/system/clash.service << 'SERVICE_EOF'
[Unit]
Description=Clash daemon
After=network.target

[Service]
Type=simple
Restart=always
ExecStart=/opt/clash/clash -f /opt/clash/config.yaml
WorkingDirectory=/opt/clash
User=root
Group=root

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# 重新加载systemd
systemctl daemon-reload

echo "Clash安装完成！"
EOF

# 创建启动脚本
cat > "$TEMP_DIR/start_clash.sh" << 'EOF'
#!/bin/bash

echo "=== 启动Clash服务 ==="

# 复制配置文件
cp /tmp/clash_config.yaml /opt/clash/config.yaml

# 启动服务
systemctl enable clash
systemctl start clash

# 检查状态
sleep 3
systemctl status clash --no-pager

echo "Clash服务已启动！"
echo "HTTP代理端口: 7890"
echo "SOCKS代理端口: 7891"
echo "管理界面: http://127.0.0.1:9090"
EOF

# 创建测试脚本
cat > "$TEMP_DIR/test_proxy.sh" << 'EOF'
#!/bin/bash

echo "=== 测试代理连接 ==="

# 测试Google连接
echo "测试Google连接..."
curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 10

echo "测试YouTube连接..."
curl -x http://127.0.0.1:7890 -I https://www.youtube.com --connect-timeout 10

echo "测试GitHub连接..."
curl -x http://127.0.0.1:7890 -I https://www.github.com --connect-timeout 10

echo "代理测试完成！"
EOF

# 设置脚本权限
chmod +x "$TEMP_DIR/install_clash.sh"
chmod +x "$TEMP_DIR/start_clash.sh"
chmod +x "$TEMP_DIR/test_proxy.sh"

echo "=== 上传文件到服务器 ==="

# 上传文件到服务器
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no "$TEMP_DIR/clash_config.yaml" "$SERVER_USER@$SERVER_IP:/tmp/"
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no "$TEMP_DIR/install_clash.sh" "$SERVER_USER@$SERVER_IP:/tmp/"
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no "$TEMP_DIR/start_clash.sh" "$SERVER_USER@$SERVER_IP:/tmp/"
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no "$TEMP_DIR/test_proxy.sh" "$SERVER_USER@$SERVER_IP:/tmp/"

echo "=== 在服务器上执行安装 ==="

# 执行安装
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "chmod +x /tmp/install_clash.sh && /tmp/install_clash.sh"

echo "=== 启动Clash服务 ==="

# 启动服务
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "chmod +x /tmp/start_clash.sh && /tmp/start_clash.sh"

echo "=== 测试代理连接 ==="

# 测试代理
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "chmod +x /tmp/test_proxy.sh && /tmp/test_proxy.sh"

echo "=== 设置完成 ==="
echo "Clash代理已成功安装在服务器上！"
echo ""
echo "使用方法："
echo "1. 在服务器上设置代理环境变量："
echo "   export http_proxy=http://127.0.0.1:7890"
echo "   export https_proxy=http://127.0.0.1:7890"
echo "   export HTTP_PROXY=http://127.0.0.1:7890"
echo "   export HTTPS_PROXY=http://127.0.0.1:7890"
echo ""
echo "2. 测试访问Google："
echo "   curl -I https://www.google.com"
echo ""
echo "3. 管理Clash服务："
echo "   systemctl status clash    # 查看状态"
echo "   systemctl restart clash   # 重启服务"
echo "   systemctl stop clash      # 停止服务"
echo ""
echo "4. 查看Clash日志："
echo "   journalctl -u clash -f"
echo ""
echo "5. 访问管理界面："
echo "   http://47.103.143.152:9090"

# 清理临时文件
rm -rf "$TEMP_DIR"

echo "临时文件已清理完成！"
