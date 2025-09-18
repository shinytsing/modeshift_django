#!/bin/bash
# 检查服务器Clash状态

echo "=== 检查服务器Clash状态 ==="

ssh root@47.103.143.152 << 'EOF'
echo "1. 检查系统信息..."
uname -a
cat /etc/os-release

echo "2. 检查是否已安装Clash..."
which clash
ls -la /usr/local/bin/clash 2>/dev/null || echo "Clash未安装在/usr/local/bin"
ls -la /opt/clash 2>/dev/null || echo "Clash未安装在/opt"
ls -la /usr/bin/clash 2>/dev/null || echo "Clash未安装在/usr/bin"

echo "3. 检查Clash进程..."
ps aux | grep clash | grep -v grep || echo "没有Clash进程在运行"

echo "4. 检查端口监听..."
netstat -tlnp | grep -E "(7890|7891|9090)" || echo "没有Clash相关端口在监听"

echo "5. 检查systemd服务..."
systemctl status clash --no-pager 2>/dev/null || echo "Clash服务未配置"

echo "6. 检查配置文件..."
ls -la /etc/clash/ 2>/dev/null || echo "Clash配置目录不存在"

echo "7. 尝试手动安装Clash..."
cd /tmp
# 尝试多种下载方式
echo "尝试下载Clash..."
wget -O clash.gz "https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-linux-amd64-v1.18.0.gz" 2>/dev/null || \
curl -L -o clash.gz "https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-linux-amd64-v1.18.0.gz" 2>/dev/null || \
echo "下载失败"

if [ -f "clash.gz" ]; then
    echo "下载成功，解压文件..."
    gunzip clash.gz
    ls -la clash
    file clash
    chmod +x clash
    
    echo "测试Clash..."
    ./clash --version 2>/dev/null || echo "Clash测试失败"
    
    echo "移动Clash到系统目录..."
    mkdir -p /opt
    mv clash /opt/clash
    
    echo "创建配置目录..."
    mkdir -p /etc/clash
    
    echo "Clash安装完成"
else
    echo "Clash下载失败"
fi
EOF

echo "检查完成"
