#!/bin/bash

# Claude专用绕过脚本
# 解决Cloudflare 403错误

echo "🔧 配置Claude专用绕过..."

# 1. 设置更宽松的SSL配置
export SSL_CERT_FILE=""
export SSL_CERT_DIR=""
export CURL_CA_BUNDLE=""
export REQUESTS_CA_BUNDLE=""
export NODE_TLS_REJECT_UNAUTHORIZED=0

# 2. 设置代理环境变量
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 3. 设置系统代理
networksetup -setwebproxy "Wi-Fi" 127.0.0.1 7890
networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 7890

# 4. 测试不同的User-Agent
echo "🧪 测试不同User-Agent..."

# Chrome User-Agent
echo -n "Chrome UA: "
curl -x http://127.0.0.1:7890 --insecure -I https://claude.ai --connect-timeout 10 \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" \
  -H "Accept-Language: en-US,en;q=0.5" \
  -H "Accept-Encoding: gzip, deflate, br" \
  -H "DNT: 1" \
  -H "Connection: keep-alive" \
  -H "Upgrade-Insecure-Requests: 1" 2>/dev/null | head -1 | grep -q "200" && echo "✅" || echo "❌"

# Firefox User-Agent
echo -n "Firefox UA: "
curl -x http://127.0.0.1:7890 --insecure -I https://claude.ai --connect-timeout 10 \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" \
  -H "Accept-Language: en-US,en;q=0.5" \
  -H "Accept-Encoding: gzip, deflate, br" \
  -H "DNT: 1" \
  -H "Connection: keep-alive" \
  -H "Upgrade-Insecure-Requests: 1" 2>/dev/null | head -1 | grep -q "200" && echo "✅" || echo "❌"

# Safari User-Agent
echo -n "Safari UA: "
curl -x http://127.0.0.1:7890 --insecure -I https://claude.ai --connect-timeout 10 \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
  -H "Accept-Language: en-US,en;q=0.5" \
  -H "Accept-Encoding: gzip, deflate, br" \
  -H "DNT: 1" \
  -H "Connection: keep-alive" 2>/dev/null | head -1 | grep -q "200" && echo "✅" || echo "❌"

echo ""
echo "🌐 当前IP: $(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip | grep -o '"[0-9.]*"' | tr -d '"')"

echo ""
echo "🚀 现在尝试启动Cursor..."
pkill -f "Cursor" 2>/dev/null || true
sleep 2
open -a "Cursor"

echo "✅ 配置完成！请检查Cursor中的Claude功能"
