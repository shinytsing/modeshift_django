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
