#!/bin/bash

# SSH配置验证和修复脚本
# 解决GitHub Actions中SSH认证失败的问题

echo "🔧 SSH配置验证和修复..."

# 检查必要的环境变量
echo "检查GitHub Secrets配置..."
echo "需要配置的Secrets:"
echo "- SERVER_HOST: 服务器IP地址"
echo "- SERVER_USER: SSH用户名"
echo "- SERVER_SSH_KEY: SSH私钥"
echo "- SERVER_PORT: SSH端口 (可选，默认22)"
echo ""

# 生成新的SSH密钥对
echo "生成新的SSH密钥对..."
KEY_NAME="github_actions_$(date +%Y%m%d_%H%M%S)"
KEY_PATH="$HOME/.ssh/$KEY_NAME"

# 创建.ssh目录
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 生成RSA密钥对
ssh-keygen -t rsa -b 4096 -f "$KEY_PATH" -N "" -C "github-actions-$(date +%Y%m%d)"

echo "✅ SSH密钥对已生成: $KEY_PATH"
echo ""

# 显示公钥
echo "📋 请将以下公钥添加到服务器的 ~/.ssh/authorized_keys 文件中："
echo "=========================================="
cat "${KEY_PATH}.pub"
echo "=========================================="
echo ""

# 显示私钥
echo "📋 请将以下私钥添加到GitHub Secrets中的 SERVER_SSH_KEY："
echo "=========================================="
cat "$KEY_PATH"
echo "=========================================="
echo ""

# 创建SSH配置测试脚本
cat > test-ssh-connection.sh << 'EOF'
#!/bin/bash
# SSH连接测试脚本

echo "测试SSH连接..."

# 检查SSH密钥格式
if [ -f "$HOME/.ssh/github_actions_*" ]; then
    KEY_FILE=$(ls $HOME/.ssh/github_actions_* | head -1)
    echo "使用密钥文件: $KEY_FILE"
    
    # 检查密钥权限
    chmod 600 "$KEY_FILE"
    chmod 644 "${KEY_FILE}.pub"
    
    echo "密钥权限已设置"
else
    echo "❌ 未找到SSH密钥文件"
    exit 1
fi

echo "✅ SSH配置完成"
echo ""
echo "📝 下一步操作："
echo "1. 将公钥添加到服务器的 ~/.ssh/authorized_keys"
echo "2. 将私钥添加到GitHub Secrets中的 SERVER_SSH_KEY"
echo "3. 确保服务器SSH服务正在运行"
echo "4. 测试SSH连接"
EOF

chmod +x test-ssh-connection.sh

echo "✅ SSH配置验证脚本已创建"
echo ""
echo "🚀 现在可以运行: ./test-ssh-connection.sh"
