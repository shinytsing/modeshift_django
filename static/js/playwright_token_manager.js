/**
 * Playwright Token管理器 - 参考Java项目get_jobs的跨标签页同步机制
 * 解决不同标签页无法获取token值的问题
 */

class PlaywrightTokenManager {
    constructor() {
        this.storageKey = 'playwright_tokens';
        this.syncKey = 'token_sync';
        this.platforms = ['boss', 'lagou', 'liepin', 'zhipin', '51job'];
        this.syncInterval = 3000; // 3秒同步一次
        this.syncTimer = null;
        this.isActive = true;
        
        this.init();
    }
    
    init() {
        console.log('🚀 初始化Playwright Token管理器');
        
        // 监听storage变化事件
        window.addEventListener('storage', this.handleStorageChange.bind(this));
        
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        
        // 监听页面卸载
        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
        
        // 开始定期同步
        this.startPeriodicSync();
        
        // 立即同步一次
        this.syncTokens();
        
        console.log('✅ Playwright Token管理器初始化完成');
    }
    
    /**
     * 处理storage变化事件
     */
    handleStorageChange(event) {
        if (event.key === this.storageKey) {
            console.log('🔄 检测到Token变化，开始同步');
            this.syncTokens();
        }
    }
    
    /**
     * 处理页面可见性变化
     */
    handleVisibilityChange() {
        if (document.visibilityState === 'visible') {
            console.log('👁️ 页面变为可见，同步Token');
            this.syncTokens();
        }
    }
    
    /**
     * 处理页面卸载
     */
    handleBeforeUnload() {
        this.stopPeriodicSync();
    }
    
    /**
     * 开始定期同步
     */
    startPeriodicSync() {
        if (this.syncTimer) {
            clearInterval(this.syncTimer);
        }
        
        this.syncTimer = setInterval(() => {
            if (this.isActive) {
                this.syncTokens();
            }
        }, this.syncInterval);
        
        console.log(`⏰ 开始定期同步，间隔: ${this.syncInterval}ms`);
    }
    
    /**
     * 停止定期同步
     */
    stopPeriodicSync() {
        if (this.syncTimer) {
            clearInterval(this.syncTimer);
            this.syncTimer = null;
        }
    }
    
    /**
     * 同步tokens
     */
    async syncTokens() {
        try {
            // 从localStorage获取tokens
            const storedTokens = this.getTokensFromStorage();
            
            // 从服务器获取最新状态
            const serverTokens = await this.getServerTokens();
            
            // 合并tokens
            const mergedTokens = this.mergeTokens(storedTokens, serverTokens);
            
            // 保存到localStorage
            this.saveTokensToStorage(mergedTokens);
            
            // 更新UI
            this.updateUI(mergedTokens);
            
            console.log('✅ Tokens同步成功');
            
        } catch (error) {
            console.error('❌ Token同步失败:', error);
        }
    }
    
    /**
     * 从localStorage获取tokens
     */
    getTokensFromStorage() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : {};
        } catch (error) {
            console.error('获取localStorage tokens失败:', error);
            return {};
        }
    }
    
    /**
     * 从服务器获取tokens
     */
    async getServerTokens() {
        try {
            const response = await fetch('/tools/api/token/get-all/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.tokens || {};
            } else {
                console.warn('获取服务器tokens失败:', response.status);
                return {};
            }
        } catch (error) {
            console.error('获取服务器tokens异常:', error);
            return {};
        }
    }
    
    /**
     * 合并tokens
     */
    mergeTokens(storedTokens, serverTokens) {
        const merged = { ...storedTokens };
        
        // 合并服务器tokens
        for (const [platform, tokenData] of Object.entries(serverTokens)) {
            if (tokenData && tokenData.token) {
                merged[platform] = {
                    ...tokenData,
                    source: 'server',
                    lastSync: Date.now()
                };
            }
        }
        
        return merged;
    }
    
    /**
     * 保存tokens到localStorage
     */
    saveTokensToStorage(tokens) {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(tokens));
            console.log('💾 Tokens已保存到localStorage');
        } catch (error) {
            console.error('保存tokens到localStorage失败:', error);
        }
    }
    
    /**
     * 更新UI
     */
    updateUI(tokens) {
        // 更新所有平台的token显示
        for (const platform of this.platforms) {
            const tokenData = tokens[platform];
            if (tokenData && tokenData.token) {
                this.updatePlatformUI(platform, tokenData);
            }
        }
        
        // 触发自定义事件
        this.dispatchTokenUpdateEvent(tokens);
    }
    
    /**
     * 更新平台UI
     */
    updatePlatformUI(platform, tokenData) {
        // 更新token输入框
        const tokenInput = document.querySelector(`input[name="${platform}_token"]`);
        if (tokenInput && !tokenInput.value) {
            tokenInput.value = tokenData.token;
        }
        
        // 更新登录状态显示
        const statusElement = document.querySelector(`#${platform}_status`);
        if (statusElement) {
            statusElement.textContent = '已登录';
            statusElement.className = 'status-logged-in';
        }
        
        // 更新登录时间显示
        const timeElement = document.querySelector(`#${platform}_login_time`);
        if (timeElement && tokenData.login_time) {
            const loginTime = new Date(tokenData.login_time * 1000).toLocaleString();
            timeElement.textContent = loginTime;
        }
    }
    
    /**
     * 触发token更新事件
     */
    dispatchTokenUpdateEvent(tokens) {
        const event = new CustomEvent('playwrightTokensUpdated', {
            detail: { tokens }
        });
        window.dispatchEvent(event);
    }
    
    /**
     * 保存token到服务器
     */
    async saveTokenToServer(platform, token) {
        try {
            const response = await fetch('/tools/api/token/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    platform: platform,
                    token: token
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ ${platform} Token保存成功:`, data.message);
                
                // 立即同步
                this.syncTokens();
                
                return true;
            } else {
                const error = await response.json();
                console.error(`❌ ${platform} Token保存失败:`, error.error);
                return false;
            }
        } catch (error) {
            console.error(`❌ ${platform} Token保存异常:`, error);
            return false;
        }
    }
    
    /**
     * 检查登录状态
     */
    async checkLoginStatus(platform) {
        try {
            const response = await fetch(`/tools/api/token/check-login/?platform=${platform}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`${platform} 登录状态:`, data);
                return data.is_logged_in;
            } else {
                console.warn(`检查${platform}登录状态失败:`, response.status);
                return false;
            }
        } catch (error) {
            console.error(`检查${platform}登录状态异常:`, error);
            return false;
        }
    }
    
    /**
     * 启动Playwright自动登录
     */
    async startPlaywrightLogin(platform) {
        try {
            console.log(`🚀 启动${platform} Playwright自动登录`);
            
            // 检查是否有token
            const tokens = this.getTokensFromStorage();
            const tokenData = tokens[platform];
            
            if (!tokenData || !tokenData.token) {
                console.warn(`❌ ${platform} 没有可用的Token`);
                return false;
            }
            
            // 调用后端API启动Playwright
            const response = await fetch('/tools/api/playwright/start-login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    platform: platform,
                    token: tokenData.token
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ ${platform} Playwright启动成功:`, data.message);
                
                // 显示状态
                this.showPlaywrightStatus(platform, '启动中...');
                
                return true;
            } else {
                const error = await response.json();
                console.error(`❌ ${platform} Playwright启动失败:`, error.error);
                this.showPlaywrightStatus(platform, '启动失败');
                return false;
            }
        } catch (error) {
            console.error(`❌ ${platform} Playwright启动异常:`, error);
            this.showPlaywrightStatus(platform, '启动异常');
            return false;
        }
    }
    
    /**
     * 显示Playwright状态
     */
    showPlaywrightStatus(platform, status) {
        const statusElement = document.querySelector(`#${platform}_playwright_status`);
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `playwright-status ${status.includes('成功') ? 'success' : 'error'}`;
        }
    }
    
    /**
     * 获取CSRF Token
     */
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    /**
     * 获取指定平台的token
     */
    getToken(platform) {
        const tokens = this.getTokensFromStorage();
        const tokenData = tokens[platform];
        return tokenData ? tokenData.token : null;
    }
    
    /**
     * 设置指定平台的token
     */
    setToken(platform, token) {
        const tokens = this.getTokensFromStorage();
        tokens[platform] = {
            token: token,
            login_time: Date.now() / 1000,
            platform: platform,
            source: 'manual',
            lastSync: Date.now()
        };
        
        this.saveTokensToStorage(tokens);
        this.saveTokenToServer(platform, token);
        
        console.log(`✅ ${platform} Token已设置`);
    }
    
    /**
     * 清除指定平台的token
     */
    clearToken(platform) {
        const tokens = this.getTokensFromStorage();
        delete tokens[platform];
        this.saveTokensToStorage(tokens);
        
        console.log(`🗑️ ${platform} Token已清除`);
    }
    
    /**
     * 获取所有tokens
     */
    getAllTokens() {
        return this.getTokensFromStorage();
    }
    
    /**
     * 销毁管理器
     */
    destroy() {
        this.stopPeriodicSync();
        this.isActive = false;
        
        window.removeEventListener('storage', this.handleStorageChange.bind(this));
        document.removeEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        window.removeEventListener('beforeunload', this.handleBeforeUnload.bind(this));
        
        console.log('🔚 Playwright Token管理器已销毁');
    }
}

// 全局实例
let playwrightTokenManager = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    playwrightTokenManager = new PlaywrightTokenManager();
    
    // 绑定按钮事件
    bindButtonEvents();
});

/**
 * 绑定按钮事件
 */
function bindButtonEvents() {
    // 保存Token按钮
    document.querySelectorAll('[data-action="save-token"]').forEach(button => {
        button.addEventListener('click', function() {
            const platform = this.dataset.platform;
            const tokenInput = document.querySelector(`input[name="${platform}_token"]`);
            if (tokenInput && tokenInput.value) {
                playwrightTokenManager.setToken(platform, tokenInput.value);
            }
        });
    });
    
    // 启动Playwright按钮
    document.querySelectorAll('[data-action="start-playwright"]').forEach(button => {
        button.addEventListener('click', function() {
            const platform = this.dataset.platform;
            playwrightTokenManager.startPlaywrightLogin(platform);
        });
    });
    
    // 检查登录状态按钮
    document.querySelectorAll('[data-action="check-login"]').forEach(button => {
        button.addEventListener('click', async function() {
            const platform = this.dataset.platform;
            const isLoggedIn = await playwrightTokenManager.checkLoginStatus(platform);
            alert(`${platform} 登录状态: ${isLoggedIn ? '已登录' : '未登录'}`);
        });
    });
    
    // 清除Token按钮
    document.querySelectorAll('[data-action="clear-token"]').forEach(button => {
        button.addEventListener('click', function() {
            const platform = this.dataset.platform;
            if (confirm(`确定要清除${platform}的Token吗？`)) {
                playwrightTokenManager.clearToken(platform);
                const tokenInput = document.querySelector(`input[name="${platform}_token"]`);
                if (tokenInput) {
                    tokenInput.value = '';
                }
            }
        });
    });
}

// 导出到全局
window.PlaywrightTokenManager = PlaywrightTokenManager;
window.playwrightTokenManager = playwrightTokenManager;
