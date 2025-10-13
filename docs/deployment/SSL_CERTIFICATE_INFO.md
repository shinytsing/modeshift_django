# 🔒 SSL证书信息文档

## 📋 证书概览

### 1. 生产环境SSL证书 (shenyiqing.xin)

**证书基本信息：**
- **域名**: www.shenyiqing.xin, shenyiqing.xin
- **证书颁发机构**: DigiCert Inc
- **证书类型**: DV (Domain Validated) TLS证书
- **有效期**: 2025年9月4日 - 2025年12月2日
- **密钥长度**: RSA 2048位
- **签名算法**: SHA256withRSA
- **证书状态**: ✅ 有效

**证书文件位置：**
```
/Users/gaojie/Desktop/PycharmProjects/modeshift_django/ssl_certs/
├── shenyiqing.xin.crt    # SSL证书文件
└── shenyiqing.xin.key    # 私钥文件
```

**证书详细信息：**
- **序列号**: 0c:9f:2a:26:53:b6:c7:2f:36:af:32:95:e8:85:29:3e
- **颁发者**: C=US, O=DigiCert Inc, OU=www.digicert.com, CN=Encryption Everywhere DV TLS CA - G2
- **主题**: CN=www.shenyiqing.xin
- **公钥算法**: RSA加密
- **公钥长度**: 2048位
- **指数**: 65537 (0x10001)

**扩展信息：**
- **主题备用名称**: DNS:www.shenyiqing.xin, DNS:shenyiqing.xin
- **密钥用途**: 数字签名, 密钥加密
- **扩展密钥用途**: TLS Web服务器认证, TLS Web客户端认证
- **证书策略**: 2.23.140.1.2.1
- **OCSP**: http://ocsp.digicert.com
- **CA颁发者**: http://cacerts.digicert.com/EncryptionEverywhereDVTLSCA-G2.crt

### 2. Trojan服务器SSL证书

**证书基本信息：**
- **域名**: trojan-server (自签名证书)
- **证书类型**: 自签名证书
- **有效期**: 2025年9月16日 - 2026年9月16日
- **密钥长度**: RSA 2048位
- **签名算法**: SHA256withRSA
- **证书状态**: ⚠️ 自签名证书

**证书文件位置：**
```
/Users/gaojie/Desktop/PycharmProjects/modeshift_django/trojan_server/
├── server.crt    # Trojan服务器证书
└── server.key    # Trojan服务器私钥
```

**证书详细信息：**
- **序列号**: 10:4d:7b:c4:e5:c0:ae:8a:ea:83:a5:c8:a3:28:57:8d:cd:8c:a6:b0
- **颁发者**: C=CN, ST=Beijing, L=Beijing, O=Trojan Server, CN=trojan-server
- **主题**: C=CN, ST=Beijing, L=Beijing, O=Trojan Server, CN=trojan-server
- **公钥算法**: RSA加密
- **公钥长度**: 2048位

---

## 🏗️ SSL配置架构

### Nginx SSL配置
```nginx
# HTTPS服务器配置
server {
    listen 443 ssl http2;
    server_name 47.103.143.152 shenyiqing.xin www.shenyiqing.xin;
    
    # SSL证书配置
    ssl_certificate /etc/nginx/ssl/shenyiqing.xin.crt;
    ssl_certificate_key /etc/nginx/ssl/shenyiqing.xin.key;
    
    # SSL协议和加密套件
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    
    # SSL会话优化
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # 安全头
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;";
}
```

### Docker配置
```yaml
# docker-compose.prod.yml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.prod.conf:/etc/nginx/conf.d/default.conf:ro
    - ./ssl_certs:/etc/nginx/ssl:ro  # SSL证书挂载
```

---

## 🔧 SSL证书管理

### 证书验证命令
```bash
# 检查证书有效期
openssl x509 -in ssl_certs/shenyiqing.xin.crt -noout -dates

# 检查证书详细信息
openssl x509 -in ssl_certs/shenyiqing.xin.crt -text -noout

# 检查证书和私钥匹配
openssl x509 -noout -modulus -in ssl_certs/shenyiqing.xin.crt | openssl md5
openssl rsa -noout -modulus -in ssl_certs/shenyiqing.xin.key | openssl md5

# 检查证书指纹
openssl x509 -in ssl_certs/shenyiqing.xin.crt -noout -fingerprint -sha256
```

### 证书安装步骤
```bash
# 1. 创建SSL证书目录
mkdir -p /etc/nginx/ssl

# 2. 复制证书文件
cp ssl_certs/shenyiqing.xin.crt /etc/nginx/ssl/
cp ssl_certs/shenyiqing.xin.key /etc/nginx/ssl/

# 3. 设置正确的权限
chmod 644 /etc/nginx/ssl/shenyiqing.xin.crt
chmod 600 /etc/nginx/ssl/shenyiqing.xin.key
chown root:root /etc/nginx/ssl/shenyiqing.xin.*

# 4. 测试Nginx配置
nginx -t

# 5. 重载Nginx配置
systemctl reload nginx
```

### 在线验证工具
- **SSL Labs**: https://www.ssllabs.com/ssltest/
- **SSL Checker**: https://www.sslshopper.com/ssl-checker.html
- **DigiCert SSL Checker**: https://www.digicert.com/help/

---

## 📊 证书状态总结

| 证书类型 | 域名 | 状态 | 有效期 | 颁发机构 | 用途 |
|---------|------|------|--------|----------|------|
| 生产证书 | shenyiqing.xin | ✅ 有效 | 2025.09.04 - 2025.12.02 | DigiCert Inc | 网站HTTPS |
| Trojan证书 | trojan-server | ⚠️ 自签名 | 2025.09.16 - 2026.09.16 | 自签名 | 内部通信 |

---

## ⚠️ 重要提醒

### 证书到期管理
1. **生产证书**: 将于2025年12月2日过期，需要提前30天续期
2. **Trojan证书**: 自签名证书，有效期1年，需要定期更新
3. **监控建议**: 设置证书到期提醒，避免服务中断

### 安全配置
1. **现代协议**: 已配置TLS 1.2和1.3，禁用旧版本
2. **强加密套件**: 使用ECDHE和AES-GCM加密算法
3. **OCSP Stapling**: 已启用以提高SSL握手性能
4. **安全头**: 已配置HSTS、CSP等安全头
5. **会话优化**: 配置SSL会话缓存和超时

### 最佳实践
1. **定期检查**: 每月检查证书状态和有效期
2. **自动续期**: 考虑使用Let's Encrypt等免费CA自动续期
3. **备份证书**: 定期备份证书和私钥文件
4. **权限管理**: 确保私钥文件权限为600，证书文件权限为644
5. **监控告警**: 设置证书到期告警机制

---

## 🔄 证书更新流程

### 手动更新步骤
1. **申请新证书**: 从DigiCert或其他CA申请新证书
2. **下载证书**: 下载证书文件和私钥
3. **备份旧证书**: 备份现有证书文件
4. **安装新证书**: 按照安装步骤部署新证书
5. **测试配置**: 验证Nginx配置和SSL连接
6. **重载服务**: 重载Nginx服务使配置生效
7. **验证功能**: 测试网站HTTPS访问是否正常

### 自动更新建议
```bash
#!/bin/bash
# 证书自动更新脚本示例

CERT_DIR="/etc/nginx/ssl"
DOMAIN="shenyiqing.xin"
EMAIL="admin@shenyiqing.xin"

# 检查证书有效期
check_cert_expiry() {
    local cert_file="$CERT_DIR/${DOMAIN}.crt"
    local expiry_date=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
    local expiry_timestamp=$(date -d "$expiry_date" +%s)
    local current_timestamp=$(date +%s)
    local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
    
    echo "证书将在 $days_until_expiry 天后过期"
    
    if [ $days_until_expiry -lt 30 ]; then
        echo "警告: 证书即将过期，需要更新！"
        return 1
    fi
    return 0
}

# 执行检查
check_cert_expiry
```

---

## 📞 联系信息

- **项目**: modeshift_django
- **域名**: shenyiqing.xin
- **服务器**: 47.103.143.152
- **证书CA**: DigiCert Inc
- **最后更新**: 2025年1月7日

---

*本文档包含项目的SSL证书详细信息，请妥善保管证书私钥文件，确保系统安全。*

