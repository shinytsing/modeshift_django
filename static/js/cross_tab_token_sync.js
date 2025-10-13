/**
 * 跨标签页Token同步模块
 * 参考Java项目get_jobs的token管理机制
 * 解决不同标签页无法获取token值的问题
 */

class CrossTabTokenSync {
    constructor() {
        this.storageKey = 'boss_token_sync';
        this.eventKey = 'boss_token_update';
        this.syncInterval = 5000; // 5秒同步一次
        this.maxRetries = 3;
        this.retryCount = 0;
        this.isInitialized = false;
        this.callbacks = new Map();
        this.currentToken = null;
        this.lastSyncTime = 0;
        
        // 绑定方法上下文
        this.handleStorageChange = this.handleStorageChange.bind(this);
        this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
        this.syncFromServer = this.syncFromServer.bind(this);
        
        this.init();
    }
    
    /**
     * 初始化跨标签页同步
     */
    init() {
        if (this.isInitialized) {
            return;
        }
        
        console.log('🔄 初始化跨标签页Token同步系统');
        
        // 监听localStorage变化（跨标签页通信）
        window.addEventListener('storage', this.handleStorageChange);
        
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', this.handleVisibilityChange);
        
        // 监听页面卸载
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
        
        // 启动定期同步
        this.startPeriodicSync();
        
        // 初始化时从服务器获取最新token
        this.syncFromServer();
        
        this.isInitialized = true;
        console.log('✅ 跨标签页Token同步系统初始化完成');
    }
    
    /**
     * 处理localStorage变化事件
     */
    handleStorageChange(event) {
        if (event.key === this.storageKey && event.newValue) {
            try {
                const tokenData = JSON.parse(event.newValue);
                console.log('📨 收到跨标签页Token更新:', tokenData);
                
                // 验证token数据
                if (this.validateTokenData(tokenData)) {
                    this.currentToken = tokenData;
                    this.notifyCallbacks('token_updated', tokenData);
                }
            } catch (error) {
                console.error('❌ 解析跨标签页Token数据失败:', error);
            }
        }
    }
    
    /**
     * 处理页面可见性变化
     */
    handleVisibilityChange() {
        if (!document.hidden) {
            // 页面变为可见时，同步最新token
            console.log('👁️ 页面变为可见，同步Token状态');
            this.syncFromServer();
        }
    }
    
    /**
     * 启动定期同步
     */
    startPeriodicSync() {
        setInterval(() => {
            if (!document.hidden) {
                this.syncFromServer();
            }
        }, this.syncInterval);
    }
    
    /**
     * 从服务器同步token
     */
    async syncFromServer() {
        try {
            const response = await fetch('/tools/api/token/check-login/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                const tokenData = {
                    platform: result.platform || 'boss',
                    user_id: result.user_id,
                    username: result.username,
                    has_session_token: result.has_session_token,
                    has_cookie_token: result.has_cookie_token,
                    has_cached_token: result.has_cached_token,
                    is_logged_in: result.is_logged_in,
                    session_login_time: result.session_login_time,
                    cookie_login_time: result.cookie_login_time,
                    cached_login_time: result.cached_login_time,
                    timestamp: result.timestamp,
                    sync_time: Date.now()
                };
                
                // 检查是否有更新
                if (this.hasTokenChanged(tokenData)) {
                    console.log('🔄 Token状态已更新:', tokenData);
                    this.updateToken(tokenData);
                }
                
                this.retryCount = 0; // 重置重试计数
            } else {
                console.warn('⚠️ 服务器返回错误:', result.error);
            }
            
        } catch (error) {
            console.error('❌ 从服务器同步Token失败:', error);
            this.handleSyncError(error);
        }
    }
    
    /**
     * 检查token是否有变化
     */
    hasTokenChanged(newTokenData) {
        if (!this.currentToken) {
            return true;
        }
        
        // 比较关键字段
        const keyFields = ['is_logged_in', 'session_login_time', 'cookie_login_time', 'cached_login_time'];
        
        for (const field of keyFields) {
            if (this.currentToken[field] !== newTokenData[field]) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * 更新token并同步到其他标签页
     */
    updateToken(tokenData) {
        if (!this.validateTokenData(tokenData)) {
            console.error('❌ Token数据验证失败:', tokenData);
            return false;
        }
        
        this.currentToken = tokenData;
        this.lastSyncTime = Date.now();
        
        // 保存到localStorage（触发其他标签页的storage事件）
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(tokenData));
            console.log('💾 Token已保存到localStorage');
        } catch (error) {
            console.error('❌ 保存Token到localStorage失败:', error);
        }
        
        // 通知回调函数
        this.notifyCallbacks('token_updated', tokenData);
        
        return true;
    }
    
    /**
     * 验证token数据
     */
    validateTokenData(tokenData) {
        if (!tokenData || typeof tokenData !== 'object') {
            return false;
        }
        
        const requiredFields = ['platform', 'user_id', 'is_logged_in', 'timestamp'];
        
        for (const field of requiredFields) {
            if (!(field in tokenData)) {
                console.warn(`❌ Token数据缺少必需字段: ${field}`);
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * 处理同步错误
     */
    handleSyncError(error) {
        this.retryCount++;
        
        if (this.retryCount <= this.maxRetries) {
            const retryDelay = Math.pow(2, this.retryCount) * 1000; // 指数退避
            console.log(`🔄 ${retryDelay/1000}秒后重试同步 (${this.retryCount}/${this.maxRetries})`);
            
            setTimeout(() => {
                this.syncFromServer();
            }, retryDelay);
        } else {
            console.error('❌ Token同步失败次数过多，停止重试');
            this.notifyCallbacks('sync_failed', error);
        }
    }
    
    /**
     * 获取当前token状态
     */
    getCurrentToken() {
        // 优先返回内存中的token
        if (this.currentToken) {
            return this.currentToken;
        }
        
        // 尝试从localStorage获取
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const tokenData = JSON.parse(stored);
                if (this.validateTokenData(tokenData)) {
                    this.currentToken = tokenData;
                    return tokenData;
                }
            }
        } catch (error) {
            console.error('❌ 从localStorage读取Token失败:', error);
        }
        
        return null;
    }
    
    /**
     * 检查是否已登录
     */
    isLoggedIn() {
        const token = this.getCurrentToken();
        return token && token.is_logged_in === true;
    }
    
    /**
     * 获取登录状态详情
     */
    getLoginStatus() {
        const token = this.getCurrentToken();
        
        if (!token) {
            return {
                is_logged_in: false,
                platform: 'boss',
                message: '未找到Token信息'
            };
        }
        
        return {
            is_logged_in: token.is_logged_in,
            platform: token.platform,
            user_id: token.user_id,
            username: token.username,
            has_session_token: token.has_session_token,
            has_cookie_token: token.has_cookie_token,
            has_cached_token: token.has_cached_token,
            last_sync: new Date(token.sync_time || 0).toLocaleString(),
            message: token.is_logged_in ? '已登录' : '未登录'
        };
    }
    
    /**
     * 强制刷新token
     */
    async refreshToken() {
        console.log('🔄 强制刷新Token状态');
        await this.syncFromServer();
        return this.getCurrentToken();
    }
    
    /**
     * 清除token
     */
    clearToken() {
        console.log('🗑️ 清除Token状态');
        
        this.currentToken = null;
        this.lastSyncTime = 0;
        
        try {
            localStorage.removeItem(this.storageKey);
        } catch (error) {
            console.error('❌ 清除localStorage Token失败:', error);
        }
        
        this.notifyCallbacks('token_cleared', null);
    }
    
    /**
     * 注册回调函数
     */
    onTokenChange(callback) {
        if (typeof callback === 'function') {
            const id = Date.now() + Math.random();
            this.callbacks.set(id, callback);
            return id;
        }
        return null;
    }
    
    /**
     * 移除回调函数
     */
    offTokenChange(callbackId) {
        return this.callbacks.delete(callbackId);
    }
    
    /**
     * 通知所有回调函数
     */
    notifyCallbacks(event, data) {
        this.callbacks.forEach(callback => {
            try {
                callback(event, data);
            } catch (error) {
                console.error('❌ 回调函数执行失败:', error);
            }
        });
    }
    
    /**
     * 获取CSRF Token
     */
    getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        
        // 尝试从meta标签获取
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }
        
        // 尝试从隐藏input获取
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        return '';
    }
    
    /**
     * 清理资源
     */
    cleanup() {
        if (this.isInitialized) {
            window.removeEventListener('storage', this.handleStorageChange);
            document.removeEventListener('visibilitychange', this.handleVisibilityChange);
            this.callbacks.clear();
            this.isInitialized = false;
            console.log('🧹 跨标签页Token同步系统已清理');
        }
    }
    
    /**
     * 获取调试信息
     */
    getDebugInfo() {
        return {
            isInitialized: this.isInitialized,
            currentToken: this.currentToken,
            lastSyncTime: new Date(this.lastSyncTime).toLocaleString(),
            retryCount: this.retryCount,
            callbackCount: this.callbacks.size,
            storageKey: this.storageKey
        };
    }
}

// 创建全局实例
window.CrossTabTokenSync = window.CrossTabTokenSync || new CrossTabTokenSync();

// 导出模块（如果支持ES6模块）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CrossTabTokenSync;
}

// 提供便捷的全局函数
window.getTokenStatus = function() {
    return window.CrossTabTokenSync.getLoginStatus();
};

window.isUserLoggedIn = function() {
    return window.CrossTabTokenSync.isLoggedIn();
};

window.refreshTokenStatus = function() {
    return window.CrossTabTokenSync.refreshToken();
};

console.log('✅ 跨标签页Token同步模块已加载');

