#!/bin/bash
# 部署服务器代理中转站

echo "=== 部署服务器代理中转站 ==="
echo "服务器: 47.103.143.152"
echo "目标: 配置服务器作为代理中转站"
echo ""

# 检查脚本是否存在
if [ ! -f "setup_server_clash_proxy.sh" ]; then
    echo "错误: setup_server_clash_proxy.sh 不存在"
    exit 1
fi

echo "1. 上传配置脚本到服务器..."
scp setup_server_clash_proxy.sh root@47.103.143.152:/root/

echo "2. 连接到服务器执行配置..."
ssh root@47.103.143.152 << 'EOF'
cd /root
chmod +x setup_server_clash_proxy.sh
./setup_server_clash_proxy.sh
EOF

echo ""
echo "=== 部署完成 ==="
echo "服务器代理中转站已配置完成"
echo ""
echo "使用方法:"
echo "HTTP代理: http://47.103.143.152:7890"
echo "SOCKS5代理: socks5://47.103.143.152:7891"
echo "管理界面: http://47.103.143.152:9090"
echo ""
echo "测试命令:"
echo "curl -x http://47.103.143.152:7890 https://www.google.com"
