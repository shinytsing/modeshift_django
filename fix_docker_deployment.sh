#!/bin/bash

# 修复Docker部署问题的脚本
echo "🔧 修复Docker部署问题..."

# 1. 更新Docker Compose配置，移除过时的version字段
echo "📝 更新Docker Compose配置..."
cat > docker-compose-fixed.yml << 'EOF'
services:
  # PostgreSQL数据库
  db:
    image: postgres:15-alpine
    container_name: qatoolbox_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: qatoolbox_production
      POSTGRES_USER: qatoolbox
      POSTGRES_PASSWORD: qatoolbox123
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U qatoolbox -d qatoolbox_production"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: qatoolbox_redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass redis123
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Django应用
  web:
    build: .
    container_name: qatoolbox_web
    restart: unless-stopped
    environment:
      # Django配置
      DJANGO_SETTINGS_MODULE: config.settings.production
      DJANGO_SECRET_KEY: django-production-secret-key-change-me
      DJANGO_DEBUG: "False"
      
      # 数据库配置
      DB_NAME: qatoolbox_production
      DB_USER: qatoolbox
      DB_PASSWORD: qatoolbox123
      DB_HOST: db
      DB_PORT: 5432
      
      # Redis配置
      REDIS_URL: redis://:redis123@redis:6379/0
      
      # 第三方API配置
      DEEPSEEK_API_KEY: sk-c4a84c8bbff341cbb3006ecaf84030fe
      GOOGLE_API_KEY: ""
      GOOGLE_CSE_ID: ""
      OPENWEATHER_API_KEY: ""
      
      # 邮件配置
      EMAIL_HOST: smtp.gmail.com
      EMAIL_PORT: 587
      EMAIL_HOST_USER: your-email@gmail.com
      EMAIL_HOST_PASSWORD: your-email-password
      DEFAULT_FROM_EMAIL: noreply@shenyiqing.xin
      
      # 安全配置
      SECURE_SSL_REDIRECT: "False"
      
      # 允许的主机
      ALLOWED_HOSTS: 47.103.143.152,shenyiqing.xin,www.shenyiqing.xin,localhost,127.0.0.1,0.0.0.0
    volumes:
      - media_data:/app/media
      - static_data:/app/staticfiles
      - logs_data:/app/logs
      - task_storage_data:/app/task_storage
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: qatoolbox_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.production.conf:/etc/nginx/nginx.conf:ro
      - ./ssl_certs:/etc/nginx/ssl:ro
      - static_data:/var/www/static:ro
      - media_data:/var/www/media:ro
    depends_on:
      - web
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

# 数据卷
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  media_data:
    driver: local
  static_data:
    driver: local
  logs_data:
    driver: local
  task_storage_data:
    driver: local

# 网络
networks:
  qatoolbox_network:
    driver: bridge
EOF

# 2. 尝试拉取基础镜像
echo "📥 尝试拉取基础镜像..."
docker pull postgres:15-alpine || echo "PostgreSQL镜像拉取失败，将使用本地构建"
docker pull redis:7-alpine || echo "Redis镜像拉取失败，将使用本地构建"
docker pull nginx:alpine || echo "Nginx镜像拉取失败，将使用本地构建"

# 3. 使用修复后的配置启动服务
echo "🚀 启动服务..."
docker-compose -f docker-compose-fixed.yml up -d --build

# 4. 检查服务状态
echo "🔍 检查服务状态..."
sleep 30
docker-compose -f docker-compose-fixed.yml ps

echo "✅ 修复脚本执行完成"
