#!/bin/bash

# 服务器环境变量配置脚本
# 用于在服务器上配置AI API密钥

echo "🚀 配置服务器AI API密钥"
echo "=================================="

# 检查是否在服务器上
if [ "$(hostname)" != "shenyiqing.xin" ] && [ "$(hostname)" != "47.103.143.152" ]; then
    echo "⚠️  警告: 此脚本应在服务器上运行"
    echo "当前主机名: $(hostname)"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 设置环境变量
echo "📝 设置环境变量..."

# Groq API
export GROQ_API_KEY="YOUR_GROQ_API_KEY_HERE"
echo "✅ GROQ_API_KEY 已设置"

# 腾讯混元API
export TENCENT_SECRET_ID="YOUR_TENCENT_SECRET_ID_HERE"
export TENCENT_SECRET_KEY="YOUR_TENCENT_SECRET_KEY_HERE"
echo "✅ 腾讯混元API密钥已设置"

# 将环境变量写入.env文件
echo "💾 保存环境变量到.env文件..."
cat > .env << EOF
# AI API配置
GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
TENCENT_SECRET_ID=YOUR_TENCENT_SECRET_ID_HERE
TENCENT_SECRET_KEY=YOUR_TENCENT_SECRET_KEY_HERE

# 其他配置
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
EOF

echo "✅ 环境变量已保存到.env文件"

# 测试AI服务
echo "🧪 测试AI服务..."
python3 -c "
import os
from apps.tools.services.llm_service import get_llm_service

# 检查可用的AI服务
llm_service = get_llm_service()
available_providers = llm_service.get_available_providers()

print('可用的AI服务提供商:')
for provider in available_providers:
    print(f'  - {provider.value}')

if available_providers:
    print('\\n测试第一个可用的服务...')
    try:
        result = llm_service.generate_content('Hello, test message')
        print(f'✅ AI服务可用，响应: {result[:100]}...')
    except Exception as e:
        print(f'❌ AI服务调用失败: {e}')
else:
    print('❌ 没有可用的AI服务')
"

echo "🎉 配置完成！"
echo "请重启Django服务使配置生效："
echo "  sudo systemctl restart gunicorn"
echo "  sudo systemctl restart nginx"
