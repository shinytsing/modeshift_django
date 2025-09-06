# 🔧 环境变量配置指南

## 概述
为了确保线上功能正常工作，需要正确配置以下环境变量。没有这些环境变量，相关功能将无法使用。

## 必需的环境变量

### 1. 数据库配置
```bash
export DJANGO_SECRET_KEY="your_production_secret_key_here"
export DB_NAME="modeshift_production"
export DB_USER="modeshift"
export DB_PASSWORD="your_db_password"
export DB_HOST="localhost"
export DB_PORT="5432"
```

### 2. API密钥配置
```bash
# DeepSeek AI API - 用于AI对话和内容生成
export DEEPSEEK_API_KEY="sk-your_deepseek_api_key_here"

# Pixabay API - 用于冥想音效
export PIXABAY_API_KEY="your_pixabay_api_key_here"

# 高德地图API - 用于地图和位置服务
export AMAP_API_KEY="your_amap_api_key_here"
```

### 3. 其他配置
```bash
export DEBUG="False"
export ALLOWED_HOSTS="47.103.143.152,localhost,127.0.0.1"
export REDIS_URL="redis://localhost:6379/0"
```

## 配置方法

### 方法1: 服务器环境变量
在服务器上直接设置环境变量：
```bash
# 编辑 ~/.bashrc 或 ~/.profile
echo 'export DEEPSEEK_API_KEY="sk-your_key_here"' >> ~/.bashrc
echo 'export PIXABAY_API_KEY="your_key_here"' >> ~/.bashrc
echo 'export AMAP_API_KEY="your_key_here"' >> ~/.bashrc

# 重新加载配置
source ~/.bashrc
```

### 方法2: .env文件
在项目根目录创建 `.env.production` 文件：
```bash
# 数据库配置
DJANGO_SECRET_KEY=your_production_secret_key_here
DB_NAME=modeshift_production
DB_USER=modeshift
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# API密钥
DEEPSEEK_API_KEY=sk-your_deepseek_api_key_here
PIXABAY_API_KEY=your_pixabay_api_key_here
AMAP_API_KEY=your_amap_api_key_here

# 其他配置
DEBUG=False
ALLOWED_HOSTS=47.103.143.152,localhost,127.0.0.1
REDIS_URL=redis://localhost:6379/0
```

### 方法3: Docker环境变量
在 `docker-compose.yml` 中配置：
```yaml
services:
  web:
    environment:
      - DEEPSEEK_API_KEY=sk-your_deepseek_api_key_here
      - PIXABAY_API_KEY=your_pixabay_api_key_here
      - AMAP_API_KEY=your_amap_api_key_here
```

## 功能依赖关系

### 需要 DEEPSEEK_API_KEY 的功能
- AI对话聊天
- 内容生成
- 旅游攻略生成
- 塔罗牌解读
- 营养建议
- 其他AI相关功能

### 需要 PIXABAY_API_KEY 的功能
- 冥想音效服务
- 音乐推荐

### 需要 AMAP_API_KEY 的功能
- 地图搜索
- 位置服务
- 地址解析

## 验证配置

### 1. 检查环境变量
```bash
# 在服务器上运行
echo $DEEPSEEK_API_KEY
echo $PIXABAY_API_KEY
echo $AMAP_API_KEY
```

### 2. 测试功能
```bash
# 启动Django shell
python manage.py shell

# 测试API密钥
from django.conf import settings
print("DEEPSEEK_API_KEY:", bool(settings.DEEPSEEK_API_KEY))
print("PIXABAY_API_KEY:", bool(settings.PIXABAY_API_KEY))
print("AMAP_API_KEY:", bool(settings.AMAP_API_KEY))
```

### 3. 查看日志
```bash
# 查看应用日志
docker-compose logs web | grep -i "api_key\|environment"

# 查看错误日志
docker-compose logs web | grep -i "error"
```

## 获取API密钥

### DeepSeek API
1. 访问 [DeepSeek平台](https://platform.deepseek.com/)
2. 注册/登录账户
3. 在API管理页面创建新的API密钥
4. 复制密钥并配置到环境变量

### Pixabay API
1. 访问 [Pixabay API](https://pixabay.com/api/docs/)
2. 注册免费账户
3. 获取API密钥
4. 配置到环境变量

### 高德地图API
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册开发者账户
3. 创建应用并获取API密钥
4. 配置到环境变量

## 故障排除

### 问题1: API密钥未生效
```bash
# 重启Docker服务
docker-compose down
docker-compose up -d

# 检查环境变量
docker-compose exec web env | grep API_KEY
```

### 问题2: 功能不可用
1. 检查日志中的错误信息
2. 确认API密钥格式正确
3. 验证API密钥是否有效
4. 检查网络连接

### 问题3: 环境变量丢失
1. 检查 `.env.production` 文件是否存在
2. 确认文件权限正确
3. 重新设置环境变量

## 安全注意事项

1. **不要**将API密钥提交到代码仓库
2. **不要**在日志中输出API密钥
3. **定期**轮换API密钥
4. **使用**环境变量或密钥管理服务
5. **限制**API密钥的权限范围

---
**最后更新**: $(date)
**状态**: 生产就绪
