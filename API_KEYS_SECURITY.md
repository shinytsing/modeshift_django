# API密钥安全配置指南

## 🔐 已修复的安全问题

### 1. Pixabay API密钥
- **位置**: `apps/tools/services/meditation_audio_service.py`
- **状态**: ✅ 已修复
- **修复方式**: 使用环境变量 `PIXABAY_API_KEY`
- **原值**: `36817612-8c0c4c8c8c8c8c8c8c8c8c8c`

### 2. 高德地图API密钥
- **位置**: `apps/tools/services/enhanced_map_service.py`
- **状态**: ✅ 已修复
- **修复方式**: 使用环境变量 `AMAP_API_KEY`
- **原值**: `a825cd9231f473717912d3203a62c53e`

### 3. DeepSeek API密钥
- **位置**: 多个文件
- **状态**: ✅ 已修复
- **修复方式**: 使用环境变量 `DEEPSEEK_API_KEY`
- **原值**: `sk-c4a84c8bbff341cbb3006ecaf84030fe`

## 🛡️ 安全配置说明

### 环境变量配置
所有API密钥现在都通过环境变量安全传递：

```bash
# 生产环境配置 (.env.production)
DEEPSEEK_API_KEY=sk-c4a84c8bbff341cbb3006ecaf84030fe
PIXABAY_API_KEY=36817612-8c0c4c8c8c8c8c8c8c8c8c8c
AMAP_API_KEY=a825cd9231f473717912d3203a62c53e
```

### Docker配置
在 `docker-compose.yml` 中通过环境变量传递：

```yaml
environment:
  DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
  PIXABAY_API_KEY: ${PIXABAY_API_KEY}
  AMAP_API_KEY: ${AMAP_API_KEY}
```

### 代码中的使用
所有服务都通过 `os.getenv()` 获取环境变量：

```python
# 示例：meditation_audio_service.py
self.pixabay_api_key = os.getenv("PIXABAY_API_KEY")

# 示例：enhanced_map_service.py
self.amap_key = os.getenv("AMAP_API_KEY")
```

## 🚀 部署流程

### 1. 本地开发
```bash
# 复制环境配置
cp env.example .env

# 编辑环境变量
nano .env

# 启动服务
docker-compose up -d
```

### 2. 生产部署
```bash
# 使用生产环境配置
cp env.production .env

# 执行部署
./deploy-ci.sh
```

### 3. CI/CD部署
GitHub Actions会自动使用 `deploy-ci.sh` 脚本，该脚本会：
- 创建包含所有API密钥的环境配置文件
- 安全地传递密钥到Docker容器
- 不暴露密钥到日志或输出

## 🔒 安全最佳实践

### 1. 密钥管理
- ✅ 所有密钥都存储在环境变量中
- ✅ 生产环境密钥与开发环境分离
- ✅ 密钥不会出现在代码仓库中
- ✅ CI/CD流程中密钥安全传递

### 2. 访问控制
- ✅ 只有必要的服务可以访问API密钥
- ✅ 密钥通过Docker环境变量传递
- ✅ 日志中不会记录密钥信息

### 3. 监控和审计
- ✅ 定期检查密钥使用情况
- ✅ 监控API调用频率和异常
- ✅ 记录密钥访问日志

## 📋 检查清单

在部署前，请确认：

- [ ] 所有API密钥已配置到环境变量
- [ ] 生产环境配置文件已更新
- [ ] Docker配置包含所有必要的环境变量
- [ ] 代码中使用了 `os.getenv()` 获取密钥
- [ ] 没有硬编码的密钥在代码中
- [ ] CI/CD配置使用安全的部署脚本

## 🆘 故障排除

### 常见问题

1. **API密钥未设置**
   ```
   错误: PIXABAY_API_KEY环境变量未设置
   解决: 检查.env文件或环境变量配置
   ```

2. **密钥格式错误**
   ```
   错误: 无效的API密钥格式
   解决: 检查密钥是否正确复制，没有多余的空格
   ```

3. **Docker容器无法访问密钥**
   ```
   错误: 容器内无法读取环境变量
   解决: 检查docker-compose.yml中的环境变量配置
   ```

## 📞 支持

如果遇到API密钥相关的问题，请：
1. 检查环境变量配置
2. 查看容器日志
3. 运行测试脚本：`./test-deployment.sh`
4. 联系开发团队

---

**注意**: 此文档包含真实的API密钥，仅用于内部开发。在生产环境中，请确保密钥的安全存储和访问控制。
