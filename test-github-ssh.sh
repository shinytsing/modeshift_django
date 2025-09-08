#!/bin/bash

# 模拟GitHub Actions的SSH设置
# 用于测试SSH密钥配置

echo "🔍 模拟GitHub Actions SSH设置"
echo "=============================="

# 模拟GitHub Actions环境
export HOST="47.103.143.152"
export USERNAME="root"
export DEPLOY_PATH="/root/modeshift_django"

# 读取本地SSH私钥（模拟GitHub Secrets）
SSH_KEY=$(cat ~/.ssh/id_rsa)

echo "1. 检查SSH私钥内容..."
echo "SSH私钥长度: ${#SSH_KEY} 字符"
echo "SSH私钥开头: ${SSH_KEY:0:50}..."
echo "SSH私钥结尾: ...${SSH_KEY: -50}"

echo ""
echo "2. 设置SSH环境..."
mkdir -p ~/.ssh
echo "$SSH_KEY" > ~/.ssh/id_rsa_test
chmod 600 ~/.ssh/id_rsa_test
chmod 700 ~/.ssh

echo ""
echo "3. 检查SSH密钥格式..."
if ssh-keygen -l -f ~/.ssh/id_rsa_test > /dev/null 2>&1; then
    echo "✅ SSH密钥格式正确"
    ssh-keygen -l -f ~/.ssh/id_rsa_test
else
    echo "❌ SSH密钥格式错误"
    exit 1
fi

echo ""
echo "4. 添加SSH主机密钥..."
ssh-keyscan -H $HOST >> ~/.ssh/known_hosts

echo ""
echo "5. 测试SSH连接..."
ssh -i ~/.ssh/id_rsa_test -o ConnectTimeout=10 -o StrictHostKeyChecking=no $USERNAME@$HOST "echo 'SSH连接成功！'" && echo "✅ SSH连接正常" || echo "❌ SSH连接失败"

echo ""
echo "6. 清理测试文件..."
rm ~/.ssh/id_rsa_test

echo ""
echo "📋 需要添加到GitHub Secrets的SSH私钥："
echo "======================================"
cat ~/.ssh/id_rsa
