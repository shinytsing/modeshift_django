#!/bin/bash

# 测试部署配置脚本
# 验证API密钥配置和部署脚本

set -e

echo "🧪 开始测试部署配置..."

# 检查API密钥配置
echo "🔑 检查API密钥配置..."

# 检查meditation_audio_service.py
if grep -q "os.getenv(\"PIXABAY_API_KEY\")" apps/tools/services/meditation_audio_service.py; then
    echo "✅ meditation_audio_service.py 已正确配置PIXABAY_API_KEY"
else
    echo "❌ meditation_audio_service.py 未正确配置PIXABAY_API_KEY"
    exit 1
fi

# 检查enhanced_map_service.py
if grep -q "os.getenv(\"AMAP_API_KEY\")" apps/tools/services/enhanced_map_service.py; then
    echo "✅ enhanced_map_service.py 已正确配置AMAP_API_KEY"
else
    echo "❌ enhanced_map_service.py 未正确配置AMAP_API_KEY"
    exit 1
fi

# 检查环境配置文件
echo "📋 检查环境配置文件..."

if [ -f "env.production" ]; then
    if grep -q "DEEPSEEK_API_KEY=sk-c4a84c8bbff341cbb3006ecaf84030fe" env.production; then
        echo "✅ env.production 包含DEEPSEEK_API_KEY"
    else
        echo "❌ env.production 缺少DEEPSEEK_API_KEY"
        exit 1
    fi
    
    if grep -q "PIXABAY_API_KEY=36817612-8c0c4c8c8c8c8c8c8c8c8c8c" env.production; then
        echo "✅ env.production 包含PIXABAY_API_KEY"
    else
        echo "❌ env.production 缺少PIXABAY_API_KEY"
        exit 1
    fi
    
    if grep -q "AMAP_API_KEY=a825cd9231f473717912d3203a62c53e" env.production; then
        echo "✅ env.production 包含AMAP_API_KEY"
    else
        echo "❌ env.production 缺少AMAP_API_KEY"
        exit 1
    fi
else
    echo "❌ env.production 文件不存在"
    exit 1
fi

# 检查docker-compose.yml
echo "🐳 检查docker-compose.yml配置..."

if grep -q "PIXABAY_API_KEY: \${PIXABAY_API_KEY}" docker-compose.yml; then
    echo "✅ docker-compose.yml 包含PIXABAY_API_KEY环境变量"
else
    echo "❌ docker-compose.yml 缺少PIXABAY_API_KEY环境变量"
    exit 1
fi

if grep -q "AMAP_API_KEY: \${AMAP_API_KEY}" docker-compose.yml; then
    echo "✅ docker-compose.yml 包含AMAP_API_KEY环境变量"
else
    echo "❌ docker-compose.yml 缺少AMAP_API_KEY环境变量"
    exit 1
fi

# 检查部署脚本
echo "📜 检查部署脚本..."

if [ -f "deploy-ci.sh" ]; then
    echo "✅ deploy-ci.sh 存在"
    if [ -x "deploy-ci.sh" ]; then
        echo "✅ deploy-ci.sh 可执行"
    else
        echo "❌ deploy-ci.sh 不可执行"
        exit 1
    fi
else
    echo "❌ deploy-ci.sh 不存在"
    exit 1
fi

# 检查CI/CD配置
echo "🔄 检查CI/CD配置..."

if grep -q "deploy-ci.sh" .github/workflows/ci-cd.yml; then
    echo "✅ CI/CD配置使用deploy-ci.sh"
else
    echo "❌ CI/CD配置未使用deploy-ci.sh"
    exit 1
fi

# 检查健康检查URL
if grep -q "http://localhost/health/" .github/workflows/ci-cd.yml; then
    echo "✅ CI/CD配置使用正确的健康检查URL"
else
    echo "❌ CI/CD配置健康检查URL不正确"
    exit 1
fi

echo "🎉 所有配置检查通过！"
echo ""
echo "📋 配置总结："
echo "- ✅ API密钥已安全配置到环境变量"
echo "- ✅ 部署脚本已更新"
echo "- ✅ CI/CD配置已修复"
echo "- ✅ 健康检查URL已修正"
echo ""
echo "🚀 现在可以运行CI/CD测试了！"
