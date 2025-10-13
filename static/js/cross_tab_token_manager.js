/**
 * 跨标签页Token同步管理器
 * 参考Java项目get_jobs的cookie管理机制
 * 解决不同标签页无法获取token值的问题
 */

class CrossTabTokenManager {
    constructor() {
        this.storageKey = 'cross_tab_tokens';
        this.syncKey = 'token_sync';
        this.platforms = ['boss', 'lagou', 'liepin', 'zhipin', '51job'];
        this.syncInterval = 5000; // 5秒同步一次
        this.syncTimer = null;
        
        this.init();
    }
    
    init() {
        // 监听storage变化事件
        window.addEventListener('storage', this.handleStorageChange.bind(this));
        
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        
        // 监听页面卸载事件
        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
        
        // 开始定期同步
        this.startPeriodicSync();
        
        // 页面加载时立即同步
        this.syncTokens();
        
        console.log('CrossTabTokenManager initialized');
    }
    
    /**
     * 处理storage变化事件
     */
    handleStorageChange(event) {
        if (event.key === this.storageKey) {
            console.log('Token storage changed, syncing...');
            this.syncTokens();
        }
    }
    
    /**
     * 处理页面可见性变化
     */
    handleVisibilityChange() {
        if (document.visibilityState === 'visible') {
            console.log('Page became visible, syncing tokens...');
            this.syncTokens();
        }
    }
    
    /**
     * 处理页面卸载事件
     */
    handleBeforeUnload() {
        this.saveTokensToStorage();
    }
    
    /**
     * 开始定期同步
     */
    startPeriodicSync() {
        this.syncTimer = setInterval(() => {
            this.syncTokens();
        }, this.syncInterval);
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
            
            console.log('Tokens synced successfully');
            
        } catch (error) {
            console.error('Token sync failed:', error);
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
            console.error('Failed to get tokens from storage:', error);
            return {};
        }
    }
    
    /**
     * 保存tokens到localStorage
     */
    saveTokensToStorage(tokens = null) {
        try {
            const tokensToSave = tokens || this.getCurrentTokens();
            localStorage.setItem(this.storageKey, JSON.stringify(tokensToSave));
            
            // 触发storage事件通知其他标签页
            window.dispatchEvent(new StorageEvent('storage', {
                key: this.storageKey,
                newValue: JSON.stringify(tokensToSave),
                oldValue: localStorage.getItem(this.storageKey)
            }));
            
        } catch (error) {
            console.error('Failed to save tokens to storage:', error);
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
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.tokens || {};
            } else {
                console.warn('Failed to get server tokens:', response.status);
                return {};
            }
        } catch (error) {
            console.error('Error getting server tokens:', error);
            return {};
        }
    }
    
    /**
     * 合并tokens
     */
    mergeTokens(storedTokens, serverTokens) {
        const merged = { ...storedTokens };
        
        for (const platform of this.platforms) {
            const stored = storedTokens[platform];
            const server = serverTokens[platform];
            
            if (server && server.is_valid) {
                // 服务器token有效，使用服务器数据
                merged[platform] = {
                    ...server,
                    lastSync: Date.now()
                };
            } else if (stored && stored.is_valid) {
                // 服务器token无效但本地有效，保持本地数据
                merged[platform] = {
                    ...stored,
                    lastSync: Date.now()
                };
            } else {
                // 都无效，清除
                delete merged[platform];
            }
        }
        
        return merged;
    }
    
    /**
     * 获取当前tokens（从页面元素或全局变量）
     */
    getCurrentTokens() {
        const tokens = {};
        
        for (const platform of this.platforms) {
            // 尝试从页面元素获取token
            const tokenElement = document.querySelector(`#${platform}_token`);
            if (tokenElement && tokenElement.value) {
                tokens[platform] = {
                    token: tokenElement.value,
                    is_valid: true,
                    login_time: Date.now(),
                    platform: platform,
                    source: 'page_element'
                };
            }
            
            // 尝试从全局变量获取token
            if (window[`${platform}_token`]) {
                tokens[platform] = {
                    token: window[`${platform}_token`],
                    is_valid: true,
                    login_time: Date.now(),
                    platform: platform,
                    source: 'global_variable'
                };
            }
        }
        
        return tokens;
    }
    
    /**
     * 更新UI
     */
    updateUI(tokens) {
        for (const platform of this.platforms) {
            const token = tokens[platform];
            
            if (token && token.is_valid) {
                // 更新token输入框
                const tokenElement = document.querySelector(`#${platform}_token`);
                if (tokenElement && !tokenElement.value) {
                    tokenElement.value = token.token;
                }
                
                // 更新登录状态显示
                const statusElement = document.querySelector(`#${platform}_status`);
                if (statusElement) {
                    statusElement.textContent = '已登录';
                    statusElement.className = 'status-logged-in';
                }
                
                // 更新登录时间显示
                const timeElement = document.querySelector(`#${platform}_login_time`);
                if (timeElement && token.login_time) {
                    timeElement.textContent = new Date(token.login_time).toLocaleString();
                }
            } else {
                // 清除无效token
                const tokenElement = document.querySelector(`#${platform}_token`);
                if (tokenElement) {
                    tokenElement.value = '';
                }
                
                const statusElement = document.querySelector(`#${platform}_status`);
                if (statusElement) {
                    statusElement.textContent = '未登录';
                    statusElement.className = 'status-logged-out';
                }
            }
        }
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
                credentials: 'same-origin',
                body: JSON.stringify({
                    platform: platform,
                    token: token
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`Token saved to server for ${platform}:`, data);
                return true;
            } else {
                console.error(`Failed to save token for ${platform}:`, response.status);
                return false;
            }
        } catch (error) {
            console.error(`Error saving token for ${platform}:`, error);
            return false;
        }
    }
    
    /**
     * 同步session到服务器
     */
    async syncSessionToServer(platform, token) {
        try {
            const response = await fetch('/tools/api/token/sync-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    platform: platform,
                    token: token
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`Session synced to server for ${platform}:`, data);
                return true;
            } else {
                console.error(`Failed to sync session for ${platform}:`, response.status);
                return false;
            }
        } catch (error) {
            console.error(`Error syncing session for ${platform}:`, error);
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
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                return data;
            } else {
                console.error(`Failed to check login status for ${platform}:`, response.status);
                return null;
            }
        } catch (error) {
            console.error(`Error checking login status for ${platform}:`, error);
            return null;
        }
    }
    
    /**
     * 测试登录
     */
    async testLogin(platform) {
        try {
            const response = await fetch(`/tools/api/token/test-login/?platform=${platform}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`Login test result for ${platform}:`, data);
                return data;
            } else {
                console.error(`Failed to test login for ${platform}:`, response.status);
                return null;
            }
        } catch (error) {
            console.error(`Error testing login for ${platform}:`, error);
            return null;
        }
    }
    
    /**
     * 清除token
     */
    async clearToken(platform) {
        try {
            const response = await fetch('/tools/api/token/clear/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    platform: platform
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`Token cleared for ${platform}:`, data);
                
                // 清除本地存储
                const tokens = this.getTokensFromStorage();
                delete tokens[platform];
                this.saveTokensToStorage(tokens);
                
                return true;
            } else {
                console.error(`Failed to clear token for ${platform}:`, response.status);
                return false;
            }
        } catch (error) {
            console.error(`Error clearing token for ${platform}:`, error);
            return false;
        }
    }
    
    /**
     * 获取CSRF Token
     */
    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
    
    /**
     * 销毁管理器
     */
    destroy() {
        this.stopPeriodicSync();
        window.removeEventListener('storage', this.handleStorageChange.bind(this));
        document.removeEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        window.removeEventListener('beforeunload', this.handleBeforeUnload.bind(this));
        console.log('CrossTabTokenManager destroyed');
    }
}

// 全局实例
window.crossTabTokenManager = new CrossTabTokenManager();

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CrossTabTokenManager;
}
