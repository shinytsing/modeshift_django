# Google OAuth一键登录配置说明

## 已完成的配置

1. ✅ 创建了Google OAuth服务类
2. ✅ 创建了Google OAuth视图
3. ✅ 创建了代理中间件
4. ✅ 配置了URL路由

## 需要完成的步骤

### 1. 配置Google OAuth应用

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建或选择项目
3. 启用Google+ API
4. 创建OAuth 2.0客户端ID
5. 设置授权重定向URI: `https://shenyiqing.xin/tools/auth/google/callback/`

### 2. 设置环境变量

```bash
export GOOGLE_OAUTH_CLIENT_ID="你的Google客户端ID"
export GOOGLE_OAUTH_CLIENT_SECRET="你的Google客户端密钥"
```

### 3. 测试服务

访问: `https://shenyiqing.xin/tools/auth/google/test/`

### 4. 开始登录

访问: `https://shenyiqing.xin/tools/auth/google/start/`

## 文件位置

- 服务类: `apps/tools/services/google_oauth_service.py`
- 视图: `apps/tools/views/google_oauth_views.py`
- URL配置: `apps/tools/urls_google_oauth.py`
- 中间件: `apps/tools/middleware/proxy_middleware.py`

## 注意事项

1. 确保服务器能够访问Google服务
2. 确保Google OAuth应用配置正确
3. 确保重定向URI匹配
4. 确保环境变量正确设置
