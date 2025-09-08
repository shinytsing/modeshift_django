#!/bin/bash

# SSH调试脚本
# 用于检查SSH密钥配置

echo "🔍 SSH调试信息"
echo "================"

echo "1. 检查本地SSH密钥："
ls -la ~/.ssh/

echo ""
echo "2. 检查SSH公钥："
cat ~/.ssh/id_rsa.pub

echo ""
echo "3. 检查SSH私钥格式："
ssh-keygen -l -f ~/.ssh/id_rsa

echo ""
echo "4. 测试SSH连接："
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@47.103.143.152 "echo 'SSH连接成功'" && echo "✅ SSH连接正常" || echo "❌ SSH连接失败"

echo ""
echo "5. 检查服务器SSH配置："
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@47.103.143.152 "ls -la ~/.ssh/ && echo '---' && cat ~/.ssh/authorized_keys | head -1"

echo ""
echo "📋 需要添加到GitHub Secrets的SSH私钥："
echo "======================================"
cat ~/.ssh/id_rsa
