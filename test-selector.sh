#!/bin/bash

# 🎯 CI/CD测试选择器
# 根据需求选择最适合的测试方式

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🎯 CI/CD测试选择器                        ║"
echo "║                                                              ║"
echo "║  选择最适合你当前需求的测试方式                               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${BLUE}📋 可用的测试选项：${NC}"
echo ""
echo -e "${GREEN}1. 🚀 本地快速测试 (10-30秒)${NC}"
echo "   - 核心代码质量检查"
echo "   - 关键语法检查"
echo "   - Django设置检查"
echo "   - 适合：日常开发验证"
echo ""
echo -e "${YELLOW}2. ⚡ 本地完整测试 (3-5分钟)${NC}"
echo "   - 包含所有本地测试内容"
echo "   - 基础单元测试"
echo "   - 集成测试"
echo "   - 适合：提交前验证"
echo ""
echo -e "${BLUE}3. 🔍 GitHub完整CI/CD (10-15分钟)${NC}"
echo "   - 完整代码质量检查"
echo "   - 完整单元测试 + 集成测试"
echo "   - Docker构建测试"
echo "   - 完整部署流程"
echo "   - 适合：发布前验证"
echo ""
echo -e "${CYAN}4. 🌐 GitHub快速测试 (2-3分钟)${NC}"
echo "   - 在GitHub Actions中运行"
echo "   - 快速代码质量检查"
echo "   - 适合：PR验证"
echo ""
echo -e "${RED}5. 🚨 紧急测试 (30秒)${NC}"
echo "   - 仅语法检查"
echo "   - 基础导入检查"
echo "   - 适合：紧急修复验证"
echo ""

# 获取用户选择
read -p "请选择测试类型 (1-5): " choice

case $choice in
    1)
        echo -e "${GREEN}🚀 启动本地快速测试...${NC}"
        ./local-quick-test.sh
        ;;
    2)
        echo -e "${YELLOW}⚡ 启动本地完整测试...${NC}"
        ./local-github-cicd.sh
        ;;
    3)
        echo -e "${BLUE}🔍 启动GitHub完整CI/CD...${NC}"
        echo "推送代码到GitHub触发完整CI/CD工作流..."
        echo "或者手动触发: https://github.com/shinytsing/modeshift_django/actions/workflows/complete-cicd.yml"
        echo ""
        echo "🚀 推送命令:"
        echo "git add ."
        echo "git commit -m \"完整CI/CD测试\""
        echo "git push origin main"
        ;;
    4)
        echo -e "${CYAN}🌐 启动GitHub快速测试...${NC}"
        echo "推送代码到GitHub触发快速测试工作流..."
        echo "或者手动触发: https://github.com/shinytsing/modeshift_django/actions/workflows/quick-test.yml"
        ;;
    5)
        echo -e "${RED}🚨 启动紧急测试...${NC}"
        echo "检查Python语法..."
        python3 -m py_compile manage.py
        find apps/ -name "*.py" -exec python3 -m py_compile {} \;
        echo "检查Django设置..."
        python3 -c "
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')
        import django
        django.setup()
        print('✅ 紧急测试通过')
        "
        ;;
    *)
        echo -e "${RED}❌ 无效选择，请重新运行脚本${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ 测试完成！${NC}"
echo -e "${BLUE}💡 提示：${NC}"
echo "   - 本地测试通过后，可以安全推送到GitHub"
echo "   - 如需完整CI/CD测试，使用选项3"
echo "   - 如需快速验证，使用选项1或4"
