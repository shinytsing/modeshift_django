/**
 * 会话管理器
 * 处理用户会话状态、超时检测等功能
 */

(function() {
    'use strict';
    
    // 会话超时时间（30分钟）
    const SESSION_TIMEOUT = 30 * 60 * 1000;
    
    // 最后活动时间
    let lastActivityTime = Date.now();
    
    // 会话检查间隔（5分钟）
    const CHECK_INTERVAL = 5 * 60 * 1000;
    
    // 会话管理器对象
    const SessionManager = {
        
        /**
         * 初始化会话管理器
         */
        init: function() {
            this.bindEvents();
            this.startSessionCheck();
            console.log('Session Manager initialized');
        },
        
        /**
         * 绑定事件监听器
         */
        bindEvents: function() {
            // 监听用户活动
            const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
            
            events.forEach(event => {
                document.addEventListener(event, this.updateActivity.bind(this), true);
            });
            
            // 监听页面可见性变化
            document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
            
            // 监听页面卸载
            window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
        },
        
        /**
         * 更新最后活动时间
         */
        updateActivity: function() {
            lastActivityTime = Date.now();
        },
        
        /**
         * 开始会话检查
         */
        startSessionCheck: function() {
            setInterval(() => {
                this.checkSession();
            }, CHECK_INTERVAL);
        },
        
        /**
         * 检查会话状态
         */
        checkSession: function() {
            const now = Date.now();
            const timeSinceLastActivity = now - lastActivityTime;
            
            if (timeSinceLastActivity > SESSION_TIMEOUT) {
                this.handleSessionTimeout();
            }
        },
        
        /**
         * 处理会话超时
         */
        handleSessionTimeout: function() {
            console.log('Session timeout detected');
            
            // 显示超时提示
            if (confirm('您的会话已超时，是否重新登录？')) {
                window.location.href = '/users/login/';
            } else {
                // 清除本地存储并重定向到首页
                this.clearSession();
                window.location.href = '/';
            }
        },
        
        /**
         * 处理页面可见性变化
         */
        handleVisibilityChange: function() {
            if (document.hidden) {
                // 页面隐藏时暂停某些操作
                console.log('Page hidden, pausing session checks');
            } else {
                // 页面显示时恢复操作
                console.log('Page visible, resuming session checks');
                this.updateActivity();
            }
        },
        
        /**
         * 处理页面卸载
         */
        handleBeforeUnload: function() {
            // 保存会话状态
            this.saveSessionState();
        },
        
        /**
         * 保存会话状态
         */
        saveSessionState: function() {
            try {
                const sessionData = {
                    lastActivity: lastActivityTime,
                    timestamp: Date.now()
                };
                sessionStorage.setItem('sessionData', JSON.stringify(sessionData));
            } catch (error) {
                console.error('Failed to save session state:', error);
            }
        },
        
        /**
         * 恢复会话状态
         */
        restoreSessionState: function() {
            try {
                const sessionData = sessionStorage.getItem('sessionData');
                if (sessionData) {
                    const data = JSON.parse(sessionData);
                    lastActivityTime = data.lastActivity || Date.now();
                }
            } catch (error) {
                console.error('Failed to restore session state:', error);
            }
        },
        
        /**
         * 清除会话
         */
        clearSession: function() {
            try {
                sessionStorage.removeItem('sessionData');
                localStorage.removeItem('userToken');
                localStorage.removeItem('userData');
            } catch (error) {
                console.error('Failed to clear session:', error);
            }
        },
        
        /**
         * 获取会话状态
         */
        getSessionStatus: function() {
            return {
                lastActivity: lastActivityTime,
                timeSinceLastActivity: Date.now() - lastActivityTime,
                isActive: (Date.now() - lastActivityTime) < SESSION_TIMEOUT
            };
        }
    };
    
    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            SessionManager.init();
        });
    } else {
        SessionManager.init();
    }
    
    // 恢复会话状态
    SessionManager.restoreSessionState();
    
    // 将SessionManager暴露到全局作用域
    window.SessionManager = SessionManager;
    
})();
