#!/bin/bash

echo "🔍 测试SSH连接..."

# 测试SSH连接
ssh -i ~/.ssh/github_actions_deploy -o StrictHostKeyChecking=no root@47.103.143.152 "echo 'SSH连接测试成功'"

if [ $? -eq 0 ]; then
    echo "✅ SSH连接测试通过"
else
    echo "❌ SSH连接测试失败"
    exit 1
fi

echo "🔍 测试服务器上的项目目录..."

# 检查项目目录
ssh -i ~/.ssh/github_actions_deploy -o StrictHostKeyChecking=no root@47.103.143.152 "ls -la ~/modeshift_django"

if [ $? -eq 0 ]; then
    echo "✅ 项目目录存在"
else
    echo "❌ 项目目录不存在，需要创建"
    echo "📁 创建项目目录..."
    ssh -i ~/.ssh/github_actions_deploy -o StrictHostKeyChecking=no root@47.103.143.152 "mkdir -p ~/modeshift_django"
fi

echo "🔍 测试Git克隆..."

# 测试Git克隆
ssh -i ~/.ssh/github_actions_deploy -o StrictHostKeyChecking=no root@47.103.143.152 "cd ~/modeshift_django && git status"

if [ $? -eq 0 ]; then
    echo "✅ Git仓库正常"
else
    echo "❌ Git仓库异常，需要重新克隆"
    echo "📥 克隆项目..."
    ssh -i ~/.ssh/github_actions_deploy -o StrictHostKeyChecking=no root@47.103.143.152 "cd ~ && rm -rf modeshift_django && git clone https://github.com/shinytsing/modeshift_django.git"
fi

echo "🎉 所有测试完成！"
