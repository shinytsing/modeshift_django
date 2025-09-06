#!/bin/bash

# SSH认证问题修复脚本
# 解决GitHub Actions中SSH认证失败的问题

echo "🔧 修复SSH认证问题..."

# 检查SSH密钥格式
echo "检查SSH密钥格式..."

# 创建测试SSH密钥
echo "创建测试SSH密钥..."
ssh-keygen -t rsa -b 4096 -f ~/.ssh/github_actions_test -N "" -C "github-actions-test"

# 显示公钥
echo "📋 请将以下公钥添加到服务器的 ~/.ssh/authorized_keys 文件中："
echo "=========================================="
cat ~/.ssh/github_actions_test.pub
echo "=========================================="

# 显示私钥（用于GitHub Secrets）
echo "📋 请将以下私钥添加到GitHub Secrets中的 SERVER_SSH_KEY："
echo "=========================================="
cat ~/.ssh/github_actions_test
echo "=========================================="

echo "✅ SSH密钥生成完成"
echo ""
echo "📝 下一步操作："
echo "1. 将公钥添加到服务器的 ~/.ssh/authorized_keys"
echo "2. 将私钥添加到GitHub Secrets中的 SERVER_SSH_KEY"
echo "3. 确保服务器SSH服务正在运行"
echo "4. 测试SSH连接：ssh -i ~/.ssh/github_actions_test user@server"
