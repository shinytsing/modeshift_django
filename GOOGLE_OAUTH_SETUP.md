# Google OAuth 配置指南

## 概述

本项目已集成Google OAuth登录功能，使用django-allauth库实现。用户可以通过Google账户快速登录系统。

## 功能特性

- ✅ Google OAuth 2.0 登录
- ✅ 自动用户注册
- ✅ 用户信息同步
- ✅ 安全的回调处理
- ✅ 极客风格UI集成

## 配置步骤

### 1. Google Cloud Console 配置

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Google+ API
4. 转到"凭据"页面
5. 点击"创建凭据" > "OAuth 2.0 客户端ID"
6. 选择"Web应用程序"
7. 设置授权重定向URI：
   ```
   http://localhost:8000/accounts/google/login/callback/  # 开发环境
   https://shenyiqing.xin/accounts/google/login/callback/  # 生产环境
   ```

### 2. 环境变量配置

在 `.env` 文件中添加以下配置：

```bash
# Google OAuth配置
GOOGLE_OAUTH_CLIENT_ID=your-google-oauth-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-oauth-client-secret
```

### 3. Django设置

项目已自动配置以下设置：

- `django-allauth` 已安装并配置
- Google Provider 已启用
- 认证后端已配置
- URL路由已添加

## 使用方法

### 前端集成

在极客登录模态框中，Google OAuth按钮已集成：

```html
<a href="{% url 'socialaccount_login' 'google' %}" class="geek-btn google-oauth">
    <span class="btn-icon">🔍</span>
    <span class="btn-text">GOOGLE AUTH</span>
    <span class="btn-shortcut">[G]</span>
</a>
```

### JavaScript集成

```javascript
function initiateGoogleAuth() {
    showTerminalMessage('[OAUTH] 正在初始化Google认证...', 'info');
    
    setTimeout(() => {
        showTerminalMessage('[REDIRECT] 跳转到Google认证页面...', 'info');
        window.location.href = '/accounts/google/login/';
    }, 1000);
}
```

## 测试页面

访问 `/google-oauth-test/` 可以查看：
- 配置状态检查
- Google OAuth登录按钮
- 详细的配置说明

## 安全注意事项

1. **客户端ID和密钥安全**：
   - 客户端ID可以公开
   - 客户端密钥必须保密
   - 使用环境变量存储敏感信息

2. **重定向URI验证**：
   - 只允许配置的域名重定向
   - 生产环境使用HTTPS

3. **用户数据保护**：
   - 只请求必要的权限（profile, email）
   - 遵循GDPR和隐私法规

## 故障排除

### 常见问题

1. **"重定向URI不匹配"错误**：
   - 检查Google Console中的重定向URI配置
   - 确保域名和端口正确

2. **"客户端ID无效"错误**：
   - 检查环境变量是否正确设置
   - 重启Django服务器

3. **用户无法登录**：
   - 检查Google+ API是否已启用
   - 验证OAuth同意屏幕配置

### 调试步骤

1. 检查环境变量：
   ```bash
   echo $GOOGLE_OAUTH_CLIENT_ID
   echo $GOOGLE_OAUTH_CLIENT_SECRET
   ```

2. 查看Django日志：
   ```bash
   tail -f logs/django.log
   ```

3. 测试配置页面：
   访问 `/google-oauth-test/` 查看配置状态

## 生产环境部署

### 环境变量设置

在服务器上设置环境变量：

```bash
export GOOGLE_OAUTH_CLIENT_ID="your-production-client-id"
export GOOGLE_OAUTH_CLIENT_SECRET="your-production-client-secret"
```

### Nginx配置

确保HTTPS重定向正常工作：

```nginx
location /accounts/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 联系信息

如有问题，请联系：
- 邮箱：1009383129@qq.com

## 更新日志

- **2024-12-29**: 初始实现Google OAuth集成
- 添加django-allauth依赖
- 配置Google Provider
- 集成极客风格UI
- 添加测试页面和文档
