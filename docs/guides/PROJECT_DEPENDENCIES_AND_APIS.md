# 🔧 ModeShift Django 项目依赖和API密钥完整总结

## 📋 项目概述

**项目名称**: ModeShift Django (QAToolBox)  
**技术栈**: Django 4.2.18 + PostgreSQL + Redis + Docker  
**部署方式**: Docker容器化 + 传统部署  
**当前状态**: 私有仓库，已清理敏感信息  

---

## 🐍 Python依赖包 (requirements.txt)

### 核心框架
```python
Django==4.2.18                    # Django Web框架
django-allauth==0.57.0            # 用户认证和社交登录
django-cors-headers==4.3.1        # 跨域请求处理
django-redis==5.4.0               # Redis缓存支持
django-captcha==1.0.0             # 验证码功能
psycopg2-binary==2.9.9            # PostgreSQL数据库适配器
gunicorn==21.2.0                  # WSGI服务器
whitenoise==6.6.0                 # 静态文件服务
Pillow==10.1.0                    # 图像处理
requests==2.31.0                  # HTTP请求库
python-dotenv==1.0.0              # 环境变量管理
django-environ==0.11.2            # Django环境变量
```

### 异步和任务队列
```python
celery==5.3.4                     # 异步任务队列
redis==5.0.1                      # Redis客户端
channels==4.0.0                   # WebSocket支持
daphne==4.0.0                     # ASGI服务器
```

### 开发和调试工具
```python
django-extensions==3.2.3          # Django扩展工具
django-debug-toolbar==4.2.0       # 调试工具栏
django-cleanup==9.0.0             # 文件清理
django-storages==1.14.2           # 云存储支持
boto3==1.34.0                     # AWS SDK
```

### 安全和性能
```python
cryptography==45.0.7              # 加密库
django-cachalot==2.6.1            # 查询缓存
django-health-check==3.17.0       # 健康检查
```

### API和表单
```python
djangorestframework==3.14.0       # REST API框架
django-crispy-forms==2.1          # 表单美化
```

### 自动化测试
```python
PyYAML>=6.0                       # YAML解析
selenium>=4.0.0                   # 浏览器自动化
```

---

## 🔑 API密钥和服务配置

### 🤖 AI服务API密钥

#### 1. DeepSeek AI (主要AI服务)
- **环境变量**: `DEEPSEEK_API_KEY`
- **当前值**: `sk-c4a84c8bbff341cbb3006ecaf84030fe`
- **用途**: 主要AI对话和内容生成服务
- **API文档**: https://api.deepseek.com/
- **状态**: ✅ 已配置

#### 2. AIMLAPI (聚合AI服务)
- **环境变量**: `AIMLAPI_API_KEY`
- **当前值**: `d78968b01cd8440eb7b28d683f3230da`
- **用途**: 支持200+种AI模型的聚合服务
- **状态**: ⚠️ 需要验证
- **验证页面**: https://aimlapi.com/app/billing/verification

#### 3. 腾讯混元大模型
- **环境变量**: `TENCENT_SECRET_ID`, `TENCENT_SECRET_KEY`
- **当前值**: 
  - `TENCENT_SECRET_ID`: `100032618506_100032618506_16a17a3a4bc2eba0534e7b25c4363fc8`
  - `TENCENT_SECRET_KEY`: `sk-O5tVxVeCGTtSgPlaHMuPe9CdmgEUuy2d79yK5rf5Rp5qsI3m`
- **用途**: 腾讯云混元大模型服务
- **API文档**: https://cloud.tencent.com/document/product/1729/101848

#### 4. 免费AI服务 (推荐配置)
```bash
# Groq API - 免费额度大，速度快
GROQ_API_KEY=your_groq_api_key_here

# AI Tools API - 无需登录，兼容OpenAI
AITOOLS_API_KEY=your_aitools_key_here

# Together AI - 有免费额度
TOGETHER_API_KEY=your_together_api_key_here

# OpenRouter - 聚合多个模型
OPENROUTER_API_KEY=your_openrouter_api_key_here

# 讯飞星火 - 完全免费
XUNFEI_API_KEY=your_xunfei_key_here

# 百度千帆 - 免费额度
BAIDU_API_KEY=your_baidu_key_here

# 字节扣子 - 开发者免费
BYTEDANCE_API_KEY=your_bytedance_key_here

# 硅基流动 - 免费额度
SILICONFLOW_API_KEY=your_siliconflow_key_here
```

### 🗺️ 地图和位置服务

#### 高德地图API
- **环境变量**: `AMAP_API_KEY`
- **当前值**: `a825cd9231f473717912d3203a62c53e`
- **用途**: 地图服务、位置查询、路径规划
- **API文档**: https://lbs.amap.com/

### 🖼️ 图片和媒体服务

#### Pixabay图片API
- **环境变量**: `PIXABAY_API_KEY`
- **当前值**: `36817612-8c0c4c8c8c8c8c8c8c8c8c8c`
- **用途**: 免费图片搜索和下载
- **API文档**: https://pixabay.com/api/docs/

### 🌤️ 天气服务

#### OpenWeather API
- **环境变量**: `OPENWEATHER_API_KEY`
- **用途**: 天气信息查询
- **API文档**: https://openweathermap.org/api

### 🔐 Google服务

#### Google API
- **环境变量**: `GOOGLE_API_KEY`
- **用途**: Google服务集成

#### Google自定义搜索
- **环境变量**: `GOOGLE_CSE_ID`
- **用途**: 自定义搜索引擎

#### Google OAuth
- **环境变量**: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`
- **用途**: Google社交登录
- **API文档**: https://developers.google.com/identity/protocols/oauth2

### 📱 社交媒体API配置
```bash
XIAOHONGSHU_API_KEY=your-xiaohongshu-api-key
DOUYIN_API_KEY=your-douyin-api-key
NETEASE_API_KEY=your-netease-api-key
WEIBO_API_KEY=your-weibo-api-key
BILIBILI_API_KEY=your-bilibili-api-key
ZHIHU_API_KEY=your-zhihu-api-key
```

---

## 🗄️ 数据库和缓存配置

### PostgreSQL数据库
- **环境变量**: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- **开发环境配置**:
  - `DB_NAME`: `qatoolbox_local`
  - `DB_USER`: `gaojie`
  - `DB_PASSWORD`: (空)
  - `DB_HOST`: `localhost`
  - `DB_PORT`: `5432`

- **生产环境配置**:
  - `DB_NAME`: `qatoolbox_production`
  - `DB_USER`: `qatoolbox`
  - `DB_PASSWORD`: `qatoolbox123`
  - `DB_HOST`: `localhost`
  - `DB_PORT`: `5432`

### Redis缓存
- **环境变量**: `REDIS_URL`, `REDIS_PASSWORD`
- **当前配置**:
  - `REDIS_URL`: `redis://localhost:6379/0`
  - `REDIS_PASSWORD`: `redis123`

---

## 🐳 Docker配置

### 基础镜像
- **Python版本**: 3.11-slim (标准版) / 3.12-slim (国内优化版)
- **系统依赖**:
  - PostgreSQL客户端 (`libpq-dev`, `postgresql-client`)
  - 图像处理依赖 (`libjpeg-dev`, `libpng-dev`, `libfreetype6-dev`)
  - 音频处理依赖 (`libsndfile1`)
  - 浏览器自动化依赖 (`chromium`, `chromium-driver`)
  - OCR依赖 (`tesseract-ocr`, `tesseract-ocr-chi-sim`)

### Docker Compose服务
```yaml
services:
  db:                    # PostgreSQL数据库
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: qatoolbox_production
      POSTGRES_USER: qatoolbox
      POSTGRES_PASSWORD: qatoolbox123

  redis:                 # Redis缓存
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass redis123

  web:                   # Django应用
    build: .
    ports:
      - "8000:8000"
```

---

## 🌐 部署配置

### 服务器要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+
- **Python版本**: 3.11+
- **内存**: 最低2GB，推荐4GB+
- **存储**: 最低20GB，推荐50GB+

### 系统依赖
```bash
# 基础工具
build-essential curl wget git

# 数据库
postgresql postgresql-contrib

# 缓存
redis-server

# Web服务器
nginx

# 容器化
docker docker-compose

# 浏览器自动化
chromium chromium-driver

# OCR支持
tesseract-ocr tesseract-ocr-chi-sim
```

### 环境变量文件结构

#### 开发环境 (.env)
```bash
# Django基础配置
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development

# AI服务API密钥
DEEPSEEK_API_KEY=sk-c4a84c8bbff341cbb3006ecaf84030fe
AIMLAPI_API_KEY=d78968b01cd8440eb7b28d683f3230da
GROQ_API_KEY=your-groq-api-key
AITOOLS_API_KEY=your-aitools-api-key

# 地图和图片服务
AMAP_API_KEY=a825cd9231f473717912d3203a62c53e
PIXABAY_API_KEY=36817612-8c0c4c8c8c8c8c8c8c8c8c8c

# Google服务
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-google-custom-search-engine-id
GOOGLE_OAUTH_CLIENT_ID=your-google-oauth-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-oauth-client-secret

# 天气服务
OPENWEATHER_API_KEY=your-openweather-api-key

# 腾讯混元
TENCENT_SECRET_ID=100032618506_100032618506_16a17a3a4bc2eba0534e7b25c4363fc8
TENCENT_SECRET_KEY=sk-O5tVxVeCGTtSgPlaHMuPe9CdmgEUuy2d79yK5rf5Rp5qsI3m

# 数据库配置
DB_NAME=qatoolbox_local
DB_USER=gaojie
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0
```

#### 生产环境 (env.production)
```bash
# Django基础配置
DJANGO_SECRET_KEY=django-aliyun-production-key-$(openssl rand -hex 32)
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production

# 主机配置
ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost,127.0.0.1

# AI服务API密钥
DEEPSEEK_API_KEY=sk-c4a84c8bbff341cbb3006ecaf84030fe
AIMLAPI_API_KEY=d78968b01cd8440eb7b28d683f3230da

# 地图和图片服务
AMAP_API_KEY=a825cd9231f473717912d3203a62c53e
PIXABAY_API_KEY=36817612-8c0c4c8c8c8c8c8c8c8c8c8c

# Google OAuth配置
GOOGLE_OAUTH_CLIENT_ID=1046109123456-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz123456

# 腾讯混元
TENCENT_SECRET_ID=100032618506_100032618506_16a17a3a4bc2eba0534e7b25c4363fc8
TENCENT_SECRET_KEY=sk-O5tVxVeCGTtSgPlaHMuPe9CdmgEUuy2d79yK5rf5Rp5qsI3m

# 数据库配置
DB_NAME=qatoolbox_production
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox123
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0
```

---

## 🚀 快速配置脚本

### 1. 配置AI Tools API (推荐，无需登录)
```bash
python setup_aitools_api.py
```

### 2. 配置Groq API (推荐，免费额度大)
```bash
python quick_setup_groq.py
```

### 3. 配置腾讯混元API
```bash
python setup_tencent_hunyuan.py
```

---

## 📊 服务优先级

系统会按以下优先级自动选择可用的AI服务：

1. **AIMLAPI** (你的密钥) - 最高优先级
2. **AI Tools** (无需登录) - 立即可用
3. **Groq** (免费额度大) - 推荐
4. **讯飞星火** (完全免费) - 国内服务
5. **百度千帆** (免费额度) - 国内服务
6. **腾讯混元** (免费版本) - 国内服务
7. **字节扣子** (开发者免费) - 国内服务
8. **硅基流动** (免费额度) - 国内服务
9. **DeepSeek** (备用) - 费用较高

---

## 🔒 安全注意事项

1. **永远不要**将API密钥提交到版本控制
2. **永远不要**在日志中输出API密钥
3. **永远不要**在错误消息中暴露API密钥
4. 使用 `.gitignore` 忽略包含密钥的文件
5. 定期审查代码中的密钥使用情况
6. 定期轮换API密钥
7. 监控API使用情况

---

## 📞 获取帮助

### API服务文档
- **DeepSeek**: https://api.deepseek.com/
- **AIMLAPI**: https://aimlapi.com/app/billing/verification
- **AI Tools**: https://platform.aitools.cfd/
- **Groq**: https://console.groq.com/
- **腾讯混元**: https://hunyuan.tencent.com/
- **高德地图**: https://lbs.amap.com/
- **Pixabay**: https://pixabay.com/api/docs/
- **Google OAuth**: https://developers.google.com/identity/protocols/oauth2

### 项目文档
- **隐私保护指南**: `PRIVACY_PROTECTION_GUIDE.md`
- **API密钥汇总**: `API_KEYS_SUMMARY.md`
- **免费AI服务指南**: `FREE_AI_APIS_GUIDE.md`

---

## 📝 更新日志

- **2024-12-29**: 创建完整的依赖和API密钥总结文档
- **2024-12-29**: 清理敏感信息，将仓库设置为私有
- **2024-12-29**: 完善SSL证书和密钥文件保护
- **2024-12-29**: 更新.gitignore规则，全面保护隐私内容

---

*最后更新：2024年12月29日*  
*文档版本：v1.0*
