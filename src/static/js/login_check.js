/**
 * 全局登录检查系统
 * 自动检测用户登录状态，为需要登录的功能按钮添加点击事件监听
 * 支持工具页面链接的自动登录检查
 * 提供现代化的登录弹窗界面
 */

class LoginCheckSystem {
    constructor() {
        this.isLoggedIn = false;
        this.targetUrl = null;
        this.loginModal = null;
        this.loginRequiredSelectors = [
            // 通用登录按钮
            '.login-btn',
            '.login-button',
            '.auth-btn',
            '.auth-button',
            '[data-requires-login="true"]',
            '[data-login-required="true"]',
            
            // 工具相关按钮
            '.tool-btn',
            '.tool-button',
            '.feature-btn',
            '.feature-button',
            
            // 特定工具按钮
            '.ai-chat-btn',
            '.ai-chat-button',
            '.code-generator-btn',
            '.image-generator-btn',
            '.document-converter-btn',
            '.task-manager-btn',
            '.diary-btn',
            '.meditation-btn',
            '.travel-planner-btn',
            '.food-tracker-btn',
            '.fitness-tracker-btn',
            '.expense-tracker-btn',
            '.weather-btn',
            '.map-btn',
            '.calendar-btn',
            '.note-btn',
            '.bookmark-btn',
            '.download-btn',
            '.export-btn',
            '.share-btn',
            '.upload-btn',
            '.create-btn',
            '.edit-btn',
            '.delete-btn',
            '.save-btn',
            '.submit-btn',
            
            // 导航链接
            '.nav-tool',
            '.nav-feature',
            '.tool-link',
            '.feature-link',
            
            // 卡片和项目
            '.tool-card',
            '.feature-card',
            '.project-card',
            '.item-card'
        ];
        
        this.init();
    }
    
    /**
     * 初始化登录检查系统
     */
    init() {
        this.checkLoginStatus();
        this.bindEvents();
        this.scanForLoginRequiredElements();
        
        // 系统已初始化
    }
    
    /**
     * 检查用户登录状态
     */
    checkLoginStatus() {
        // 检查是否有用户认证信息
        const userElement = document.querySelector('[data-user-authenticated]');
        const authToken = this.getAuthToken();
        
        this.isLoggedIn = userElement ? userElement.dataset.userAuthenticated === 'true' : false;
        
        if (this.isLoggedIn) {
            // 用户已登录
            this.updateUIForLoggedInUser();
        } else {
            // 用户未登录
            this.updateUIForGuestUser();
        }
    }
    
    /**
     * 获取认证令牌
     */
    getAuthToken() {
        // 从Cookie中获取CSRF token
        const csrfToken = this.getCookie('csrftoken');
        return csrfToken;
    }
    
    /**
     * 获取Cookie值
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 监听页面变化（SPA应用）
        this.observePageChanges();
        
        // 监听登录状态变化
        this.observeLoginStatusChanges();
        
        // 监听窗口焦点变化（检查登录状态）
        window.addEventListener('focus', () => {
            this.checkLoginStatus();
        });
    }
    
    /**
     * 监听页面变化
     */
    observePageChanges() {
        // 使用MutationObserver监听DOM变化
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    // 新元素添加到页面时，重新扫描需要登录的元素
                    this.scanForLoginRequiredElements();
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    /**
     * 监听登录状态变化
     */
    observeLoginStatusChanges() {
        // 监听自定义事件
        document.addEventListener('userLoggedIn', () => {
            this.isLoggedIn = true;
            this.updateUIForLoggedInUser();
            this.scanForLoginRequiredElements();
        });
        
        document.addEventListener('userLoggedOut', () => {
            this.isLoggedIn = false;
            this.updateUIForGuestUser();
            this.scanForLoginRequiredElements();
        });
    }
    
    /**
     * 扫描需要登录的元素
     */
    scanForLoginRequiredElements() {
        this.loginRequiredSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                this.processElement(element);
            });
        });
        
        // 扫描所有带有data-requires-login属性的元素
        const customElements = document.querySelectorAll('[data-requires-login]');
        customElements.forEach(element => {
            this.processElement(element);
        });
    }
    
    /**
     * 处理单个元素
     */
    processElement(element) {
        // 避免重复绑定事件
        if (element.dataset.loginCheckBound === 'true') {
            return;
        }
        
        // 标记已绑定
        element.dataset.loginCheckBound = 'true';
        
        // 根据元素类型绑定不同的事件
        if (element.tagName === 'A') {
            this.bindLinkElement(element);
        } else if (element.tagName === 'BUTTON') {
            this.bindButtonElement(element);
        } else {
            this.bindGenericElement(element);
        }
    }
    
    /**
     * 绑定链接元素
     */
    bindLinkElement(element) {
        element.addEventListener('click', (event) => {
            if (!this.isLoggedIn) {
                event.preventDefault();
                this.handleLoginRequired(element, event);
            }
        });
    }
    
    /**
     * 绑定按钮元素
     */
    bindButtonElement(element) {
        element.addEventListener('click', (event) => {
            if (!this.isLoggedIn) {
                event.preventDefault();
                this.handleLoginRequired(element, event);
            }
        });
    }
    
    /**
     * 绑定通用元素
     */
    bindGenericElement(element) {
        element.addEventListener('click', (event) => {
            if (!this.isLoggedIn) {
                event.preventDefault();
                this.handleLoginRequired(element, event);
            }
        });
    }
    
    /**
     * 处理需要登录的情况
     */
    handleLoginRequired(element, event) {
        // 检测到需要登录的操作
        
        // 保存目标URL
        this.saveTargetUrl(element, event);
        
        // 显示登录弹窗
        this.showLoginModal();
        
        // 显示提示消息
        this.showLoginPrompt(element);
    }
    
    /**
     * 保存目标URL
     */
    saveTargetUrl(element, event) {
        let targetUrl = null;
        
        if (element.tagName === 'A') {
            targetUrl = element.href;
        } else if (element.dataset.targetUrl) {
            targetUrl = element.dataset.targetUrl;
        } else if (element.dataset.href) {
            targetUrl = element.dataset.href;
        } else {
            // 获取当前页面URL
            targetUrl = window.location.href;
        }
        
        // 处理相对路径
        if (targetUrl && !targetUrl.startsWith('http')) {
            targetUrl = new URL(targetUrl, window.location.origin).href;
        }
        
        this.targetUrl = targetUrl;
        
        // 保存到localStorage
        if (targetUrl) {
            localStorage.setItem('loginTargetUrl', targetUrl);
        }
        
        // 保存目标URL
    }
    
    /**
     * 显示登录弹窗
     */
    showLoginModal() {
        // 优先使用极客风格登录弹窗
        if (typeof showGeekLoginModal === 'function') {
            showGeekLoginModal();
        } else if (typeof showLoginModal === 'function') {
            showLoginModal();
        } else {
            // 回退到简单的登录提示
            this.showSimpleLoginPrompt();
        }
    }
    
    /**
     * 显示简单登录提示
     */
    showSimpleLoginPrompt() {
        const message = '此功能需要登录，请先登录后再使用。';
        
        if (confirm(message)) {
            // 跳转到登录页面
            showGeekLoginModal();
        }
    }
    
    /**
     * 显示登录提示消息
     */
    showLoginPrompt(element) {
        const elementText = element.textContent || element.title || '此功能';
        const message = `🔐 ${elementText} 需要登录后才能使用`;
        
        // 创建提示元素
        const prompt = document.createElement('div');
        prompt.className = 'login-prompt';
        prompt.innerHTML = `
            <div class="login-prompt-content">
                <div class="login-prompt-icon">🔐</div>
                <div class="login-prompt-text">${message}</div>
                <div class="login-prompt-actions">
                    <button class="login-prompt-btn primary" onclick="showGeekLoginModal()">立即登录</button>
                    <button class="login-prompt-btn secondary" onclick="this.parentElement.parentElement.parentElement.remove()">稍后再说</button>
                </div>
            </div>
        `;
        
        // 添加样式
        prompt.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 2px solid rgba(0, 255, 255, 0.3);
            border-radius: 10px;
            padding: 20px;
            color: #00ffff;
            font-family: 'Courier New', monospace;
            z-index: 10000;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
            animation: slideInRight 0.3s ease-out;
        `;
        
        // 添加动画样式
        if (!document.getElementById('loginPromptStyles')) {
            const style = document.createElement('style');
            style.id = 'loginPromptStyles';
            style.textContent = `
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                .login-prompt-content {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 15px;
                }
                .login-prompt-icon {
                    font-size: 24px;
                    animation: pulse 2s infinite;
                }
                .login-prompt-text {
                    text-align: center;
                    font-size: 14px;
                    font-weight: bold;
                }
                .login-prompt-actions {
                    display: flex;
                    gap: 10px;
                }
                .login-prompt-btn {
                    padding: 8px 16px;
                    border: 1px solid rgba(0, 255, 255, 0.3);
                    border-radius: 6px;
                    background: rgba(0, 255, 255, 0.1);
                    color: #00ffff;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .login-prompt-btn:hover {
                    background: rgba(0, 255, 255, 0.2);
                    box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
                }
                .login-prompt-btn.primary {
                    background: linear-gradient(135deg, #00ffff 0%, #0099cc 100%);
                    color: #000000;
                }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(prompt);
        
        // 5秒后自动移除
        setTimeout(() => {
            if (prompt.parentElement) {
                prompt.remove();
            }
        }, 5000);
    }
    
    /**
     * 更新已登录用户的UI
     */
    updateUIForLoggedInUser() {
        // 移除登录提示
        document.querySelectorAll('.login-prompt').forEach(prompt => {
            prompt.remove();
        });
        
        // 更新按钮状态
        document.querySelectorAll('[data-login-required]').forEach(element => {
            element.classList.remove('login-required');
            element.classList.add('login-enabled');
        });
        
        // 触发自定义事件
        document.dispatchEvent(new CustomEvent('loginCheckUpdated', {
            detail: { isLoggedIn: true }
        }));
    }
    
    /**
     * 更新访客用户的UI
     */
    updateUIForGuestUser() {
        // 更新按钮状态
        document.querySelectorAll('[data-login-required]').forEach(element => {
            element.classList.add('login-required');
            element.classList.remove('login-enabled');
        });
        
        // 触发自定义事件
        document.dispatchEvent(new CustomEvent('loginCheckUpdated', {
            detail: { isLoggedIn: false }
        }));
    }
    
    /**
     * 处理登录成功后的重定向
     */
    handleLoginSuccess() {
        const savedUrl = localStorage.getItem('loginTargetUrl');
        
        if (savedUrl) {
            // 登录成功，重定向到目标URL
            
            // 清除保存的URL
            localStorage.removeItem('loginTargetUrl');
            
            // 延迟重定向，让用户看到成功消息
            setTimeout(() => {
                window.location.href = savedUrl;
            }, 1000);
        } else {
            // 登录成功，刷新当前页面
            window.location.reload();
        }
    }
    
    /**
     * 检查特定元素是否需要登录
     */
    checkElementRequiresLogin(element) {
        // 检查data属性
        if (element.dataset.requiresLogin === 'true' || 
            element.dataset.loginRequired === 'true') {
            return true;
        }
        
        // 检查CSS类
        const loginClasses = ['login-required', 'requires-login', 'auth-required'];
        return loginClasses.some(className => element.classList.contains(className));
    }
    
    /**
     * 手动标记元素需要登录
     */
    markElementRequiresLogin(element) {
        element.dataset.requiresLogin = 'true';
        element.classList.add('login-required');
        this.processElement(element);
    }
    
    /**
     * 获取登录状态
     */
    getLoginStatus() {
        return {
            isLoggedIn: this.isLoggedIn,
            targetUrl: this.targetUrl,
            authToken: this.getAuthToken()
        };
    }
}

// 创建全局实例
window.loginCheckSystem = new LoginCheckSystem();

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LoginCheckSystem;
}

// 全局函数，供外部调用
window.checkLoginStatus = () => window.loginCheckSystem.checkLoginStatus();
window.markElementRequiresLogin = (element) => window.loginCheckSystem.markElementRequiresLogin(element);
window.handleLoginSuccess = () => window.loginCheckSystem.handleLoginSuccess();

// 全局登录检查系统已加载
