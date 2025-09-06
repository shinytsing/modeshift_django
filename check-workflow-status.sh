#!/bin/bash

# 检查GitHub Actions工作流状态脚本
# 使用方法: ./check-workflow-status.sh

set -e

echo "🔍 检查GitHub Actions工作流状态..."

# 检查当前工作流文件
echo "📋 当前工作流文件："
ls -la .github/workflows/

echo ""
echo "📊 工作流配置信息："
echo "- 工作流名称: ModeShift Django CI/CD Pipeline"
echo "- 触发分支: main, develop, feature/*, hotfix/*, release/**"
echo "- Python版本: 3.13"
echo "- 数据库: PostgreSQL (test_modeshift_django)"
echo "- 部署脚本: deploy-ci.sh"

echo ""
echo "🔧 最近的工作流运行状态："

# 使用GitHub CLI检查工作流状态（如果安装了的话）
if command -v gh &> /dev/null; then
    echo "使用GitHub CLI检查状态..."
    gh run list --limit 5
else
    echo "GitHub CLI未安装，请访问以下链接查看状态："
    echo "https://github.com/shinytsing/modeshift_django/actions"
fi

echo ""
echo "📝 工作流触发条件："
echo "1. 推送到main分支 - 自动触发持续部署"
echo "2. 推送到develop分支 - 触发CI检查"
echo "3. 创建Pull Request - 触发CI检查"
echo "4. 手动触发 - 可选择不同工作流类型"

echo ""
echo "🚀 部署环境："
echo "- 生产环境: http://47.103.143.152"
echo "- 域名访问: http://shenyiqing.xin"
echo "- 健康检查: http://47.103.143.152/health/"

echo ""
echo "✅ 修复完成的问题："
echo "- API密钥安全配置"
echo "- 健康检查URL修复"
echo "- 数据库配置优化"
echo "- 部署脚本更新"
echo "- 重复工作流文件清理"

echo ""
echo "🎯 下一步："
echo "1. 等待当前工作流完成"
echo "2. 检查部署状态"
echo "3. 验证功能正常"
echo "4. 监控性能指标"
