# 🔐 极客风格登录系统

## 🎯 核心功能

### 全局登录检查系统 (`src/static/js/login_check.js`)
- ✅ 自动检测用户登录状态
- ✅ 为所有需要登录的功能按钮添加点击事件监听
- ✅ 支持工具页面链接的自动登录检查
- ✅ 提供现代化的登录弹窗界面

### 极客风格登录弹窗
- ✅ 支持用户名/密码登录
- ✅ 支持用户注册
- ✅ 支持Google和微信一键登录
- ✅ 包含服务条款和隐私政策
- ✅ 响应式设计，支持移动端

### 登录后跳转处理
- ✅ 保存用户点击的目标页面URL
- ✅ 登录成功后自动跳转到目标页面
- ✅ 支持所有登录方式的重定向
- ✅ 处理相对路径和绝对路径

## 🎨 极客风格特色

### 视觉设计
- **终端风格界面**：仿照命令行终端的黑色背景和绿色文字
- **ASCII艺术Logo**：使用ASCII字符绘制的ModeShift Logo
- **霓虹色彩**：青色、绿色、紫色等霓虹色彩搭配
- **矩阵背景**：动态的矩阵雨效果背景
- **粒子效果**：连接粒子的动态背景效果

### 动画效果
- **打字机效果**：终端消息的逐字显示效果
- **扫描线动画**：标题栏的扫描线动画
- **脉冲效果**：Logo和按钮的脉冲发光效果
- **悬停动画**：按钮悬停时的发光和移动效果
- **密码强度指示器**：实时显示密码强度等级

### 交互体验
- **键盘快捷键**：
  - `L` - 切换到登录标签
  - `R` - 切换到注册标签
  - `G` - Google一键登录
  - `ESC` - 关闭登录弹窗
- **终端提示符**：仿照Linux终端的命令提示符
- **实时消息**：终端风格的状态消息显示
- **密码强度检测**：智能密码强度分析

## 🚀 使用方法

### 1. 自动检测
系统会自动检测以下类型的元素：
```html
<!-- 通用登录按钮 -->
<button class="login-btn" data-requires-login="true">登录</button>

<!-- 工具相关按钮 -->
<button class="tool-btn" data-requires-login="true">使用工具</button>

<!-- 链接 -->
<a href="/tools/ai_chat/" class="tool-link" data-requires-login="true">AI聊天</a>
```

### 2. 手动标记
```html
<!-- 使用data属性 -->
<button data-requires-login="true">需要登录的功能</button>

<!-- 使用CSS类 -->
<button class="login-required">需要登录的功能</button>
```

### 3. JavaScript调用
```javascript
// 显示登录弹窗
showGeekLoginModal();

// 检查登录状态
checkLoginStatus();

// 标记元素需要登录
markElementRequiresLogin(element);
```

## 📁 文件结构

```
apps/users/templates/users/
├── geek_login_modal.html          # 极客风格登录弹窗HTML
├── geek_login_modal_styles.html   # 极客风格CSS样式
├── geek_login_modal_scripts.html  # 极客风格JavaScript功能
└── modern_login_modal.html       # 现代化登录弹窗（备用）

src/static/js/
└── login_check.js                 # 全局登录检查系统

templates/
├── base.html                      # 主模板（已集成）
└── test_geek_login.html          # 测试页面
```

## 🧪 测试页面

访问 `/test-geek-login/` 可以测试极客风格登录系统的所有功能：

- **测试按钮**：各种需要登录的按钮测试
- **直接测试**：直接调用登录弹窗和检查系统
- **系统状态**：实时显示登录检查系统状态
- **使用说明**：详细的功能说明和快捷键

## 🔧 技术实现

### 登录检查系统
- 使用 `MutationObserver` 监听DOM变化
- 自动扫描和绑定需要登录的元素
- 支持SPA应用的动态内容检测
- 智能保存和恢复目标URL

### 极客风格弹窗
- Canvas绘制的矩阵背景动画
- WebGL粒子效果（可选）
- CSS3动画和过渡效果
- 响应式设计适配移动端

### 密码强度检测
- 检查常见弱密码
- 分析密码复杂度
- 检测键盘模式
- 实时强度指示器

## 🎮 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `L` | 切换到登录标签 |
| `R` | 切换到注册标签 |
| `G` | Google一键登录 |
| `ESC` | 关闭登录弹窗 |

## 📱 响应式支持

- **桌面端**：完整的极客风格效果
- **平板端**：适配中等屏幕尺寸
- **移动端**：简化的界面和触摸优化

## 🔒 安全特性

- CSRF令牌保护
- 密码强度检测
- 安全的认证流程
- 自动清理敏感数据

## 🎨 自定义配置

可以通过修改CSS变量来自定义颜色主题：

```css
:root {
  --geek-primary: #00ffff;
  --geek-secondary: #00ff00;
  --geek-accent: #ff00ff;
  --geek-background: #0a0a0a;
}
```

## 🚀 部署说明

1. 确保所有文件都已正确放置
2. 运行 `python manage.py collectstatic` 收集静态文件
3. 重启Django服务器
4. 访问 `/test-geek-login/` 测试功能

## 📝 更新日志

### v2.0.1-alpha
- ✅ 创建极客风格登录弹窗
- ✅ 实现全局登录检查系统
- ✅ 添加矩阵背景和粒子效果
- ✅ 支持键盘快捷键
- ✅ 创建测试页面
- ✅ 集成到主模板

---

**ModeShift 极客工坊** - 让登录变得更有趣！ 🚀
