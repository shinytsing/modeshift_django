/**
 * Google Auth 代理客户端
 * 用于前端调用服务器端 Google OAuth 代理
 */

class GoogleAuthProxy {
    constructor() {
        this.baseUrl = '/users';
        this.isInitialized = false;
        this.init();
    }

    /**
     * 初始化 Google Auth 代理
     */
    async init() {
        try {
            // 检查 Google Auth 状态
            const status = await this.checkStatus();
            if (status.success) {
                this.isInitialized = true;
                // console.log('Google Auth Proxy initialized successfully');  // 调试信息已隐藏
                this.updateUI(status.config);
            } else {
                console.error('Google Auth Proxy initialization failed:', status.error);
                this.showError('Google 登录服务不可用');
            }
        } catch (error) {
            console.error('Google Auth Proxy initialization error:', error);
            this.showError('Google 登录服务初始化失败');
        }
    }

    /**
     * 检查 Google Auth 状态
     */
    async checkStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/auth/google/status/`);
            return await response.json();
        } catch (error) {
            console.error('Status check failed:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * 启动 Google 登录流程
     */
    async startLogin() {
        if (!this.isInitialized) {
            this.showError('Google 登录服务未初始化');
            return;
        }

        try {
            // 显示加载状态
            this.showLoading('正在启动 Google 登录...');

            // 获取授权 URL
            const response = await fetch(`${this.baseUrl}/api/auth/google/initiate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
            });

            const result = await response.json();

            if (result.success) {
                // 重定向到 Google 授权页面
                window.location.href = result.auth_url;
            } else {
                this.showError(result.message || 'Google 登录启动失败');
            }
        } catch (error) {
            console.error('Google login start failed:', error);
            this.showError('Google 登录启动失败');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 更新 UI 状态
     */
    updateUI(config) {
        const googleAuthButtons = document.querySelectorAll('.google-auth-btn');
        
        googleAuthButtons.forEach(button => {
            if (config.client_id_configured && config.client_secret_configured) {
                button.style.display = 'block';
                button.disabled = false;
                button.onclick = () => this.startLogin();
            } else {
                button.style.display = 'none';
                // console.warn('Google OAuth not configured');  // 调试信息已隐藏
            }
        });

        // 更新状态指示器
        const statusIndicator = document.getElementById('google-auth-status');
        if (statusIndicator) {
            if (config.proxy_working) {
                statusIndicator.className = 'status-indicator success';
                statusIndicator.textContent = 'Google 登录可用';
            } else {
                statusIndicator.className = 'status-indicator error';
                statusIndicator.textContent = 'Google 登录不可用';
            }
        }
    }

    /**
     * 显示加载状态
     */
    showLoading(message) {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
            const loadingText = loadingOverlay.querySelector('.loading-text');
            if (loadingText) {
                loadingText.textContent = message;
            }
        }
    }

    /**
     * 隐藏加载状态
     */
    hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }

    /**
     * 显示错误消息
     */
    showError(message) {
        // 创建或更新错误提示
        let errorDiv = document.getElementById('google-auth-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'google-auth-error';
            errorDiv.className = 'alert alert-danger';
            errorDiv.style.position = 'fixed';
            errorDiv.style.top = '20px';
            errorDiv.style.right = '20px';
            errorDiv.style.zIndex = '9999';
            errorDiv.style.maxWidth = '300px';
            document.body.appendChild(errorDiv);
        }

        errorDiv.innerHTML = `
            <strong>Google 登录错误</strong><br>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;

        // 3秒后自动隐藏
        setTimeout(() => {
            if (errorDiv && errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 3000);
    }

    /**
     * 获取 CSRF Token
     */
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    /**
     * 处理登录成功
     */
    handleLoginSuccess(userInfo) {
        // console.log('Google login successful:', userInfo);  // 调试信息已隐藏
        
        // 显示成功消息
        this.showSuccess(`欢迎，${userInfo.email}！`);
        
        // 刷新页面或更新用户界面
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }

    /**
     * 显示成功消息
     */
    showSuccess(message) {
        let successDiv = document.getElementById('google-auth-success');
        if (!successDiv) {
            successDiv = document.createElement('div');
            successDiv.id = 'google-auth-success';
            successDiv.className = 'alert alert-success';
            successDiv.style.position = 'fixed';
            successDiv.style.top = '20px';
            successDiv.style.right = '20px';
            successDiv.style.zIndex = '9999';
            successDiv.style.maxWidth = '300px';
            document.body.appendChild(successDiv);
        }

        successDiv.innerHTML = `
            <strong>登录成功</strong><br>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;

        // 3秒后自动隐藏
        setTimeout(() => {
            if (successDiv && successDiv.parentElement) {
                successDiv.remove();
            }
        }, 3000);
    }
}

// 全局实例
let googleAuthProxy;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    googleAuthProxy = new GoogleAuthProxy();
});

// 导出供其他脚本使用
window.GoogleAuthProxy = GoogleAuthProxy;
