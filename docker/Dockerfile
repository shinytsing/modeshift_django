# QAToolBox Docker配置
# 使用Python 3.11官方镜像作为基础镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    DJANGO_SETTINGS_MODULE=config.settings.production

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    # 基础工具
    build-essential \
    curl \
    wget \
    git \
    # PostgreSQL客户端
    libpq-dev \
    postgresql-client \
    # 图像处理依赖
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    zlib1g-dev \
    # 音频处理依赖
    libsndfile1 \
    # 网络工具
    netcat-openbsd \
    # 清理缓存
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 先复制requirements文件（利用Docker层缓存）
COPY requirements.txt /app/

# 安装Python依赖（这部分会缓存，除非requirements.txt变化）
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 最后复制项目文件（这部分变化最频繁）
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/logs \
    && mkdir -p /app/media \
    && mkdir -p /app/staticfiles \
    && mkdir -p /app/task_storage

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app

# 设置权限
RUN chmod +x /app/manage.py \
    && chmod +x /app/start.sh \
    && chown -R app:app /app

# 切换到非root用户
USER app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# 启动命令 - 使用启动脚本
CMD ["./start.sh"]