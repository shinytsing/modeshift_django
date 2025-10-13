#!/bin/bash

# 🚀 一键部署到服务器
# 使用虚拟环境部署到 47.103.143.152

echo "🚀 开始一键部署到服务器..."
echo "服务器: 47.103.143.152"
echo "域名: shenyiqing.xin"
echo ""

# 检查sshpass是否安装
if ! command -v sshpass &> /dev/null; then
    echo "❌ 需要安装sshpass来连接服务器"
    echo "请运行: brew install sshpass"
    exit 1
fi

# 执行部署脚本
./deploy-server-venv.sh

echo ""
echo "✅ 部署完成！"
echo "🌐 访问地址: https://shenyiqing.xin"
echo "👤 管理员账号: admin/admin123"
