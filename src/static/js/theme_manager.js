/**
 * 主题管理器 - 可在您的项目中使用
 * 使用方法：
 * 1. 引入此文件
 * 2. 调用 ThemeManager.switchTheme('work') 切换主题
 * 3. 调用 ThemeManager.getCurrentTheme() 获取当前主题
 */

class ThemeManager {
    constructor() {
        this.themes = {
            'work': {
                name: '极客模式',
                background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
                color: '#e8e8e8',
                buttonColors: {
                    primary: 'linear-gradient(135deg, rgba(52, 152, 219, 0.9), rgba(41, 128, 185, 0.9))',
                    secondary: 'linear-gradient(135deg, rgba(155, 89, 182, 0.9), rgba(142, 68, 173, 0.9))',
                    success: 'rgba(255, 255, 255, 0.9)',
                    danger: 'linear-gradient(135deg, rgba(231, 76, 60, 0.9), rgba(192, 57, 43, 0.9))'
                }
            },
            'life': {
                name: '生活模式',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: '#ffffff',
                buttonColors: {
                    primary: 'linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9))',
                    secondary: 'linear-gradient(135deg, rgba(155, 89, 182, 0.9), rgba(142, 68, 173, 0.9))',
                    success: 'rgba(255, 255, 255, 0.9)',
                    danger: 'linear-gradient(135deg, rgba(231, 76, 60, 0.9), rgba(192, 57, 43, 0.9))'
                }
            },
            'training': {
                name: '狂暴模式',
                background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 50%, #ff3838 100%)',
                color: '#ffffff',
                buttonColors: {
                    primary: 'linear-gradient(135deg, rgba(255, 107, 107, 0.9), rgba(238, 90, 36, 0.9))',
                    secondary: 'linear-gradient(135deg, rgba(255, 56, 56, 0.9), rgba(192, 57, 43, 0.9))',
                    success: 'rgba(255, 255, 255, 0.9)',
                    danger: 'linear-gradient(135deg, rgba(139, 0, 0, 0.9), rgba(128, 0, 0, 0.9))'
                }
            },
            'emo': {
                name: 'Emo模式',
                background: 'linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #7f8c8d 100%)',
                color: '#ecf0f1',
                buttonColors: {
                    primary: 'linear-gradient(135deg, rgba(44, 62, 80, 0.9), rgba(52, 73, 94, 0.9))',
                    secondary: 'linear-gradient(135deg, rgba(127, 140, 141, 0.9), rgba(149, 165, 166, 0.9))',
                    success: 'rgba(255, 255, 255, 0.9)',
                    danger: 'linear-gradient(135deg, rgba(149, 165, 166, 0.9), rgba(127, 140, 141, 0.9))'
                }
            }
        };
        
        this.currentTheme = localStorage.getItem('currentTheme') || 'work';
        this.apiBaseUrl = '/users/theme/';
        
        this.init();
    }
    
    /**
     * 初始化主题管理器
     */
    init() {

        this.applyTheme(this.currentTheme);
        this.setupEventListeners();
        

    }
    

    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 监听主题切换按钮
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-theme]')) {
                const theme = e.target.dataset.theme;
                this.switchTheme(theme);
            }
        });
        
        // 监听键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key >= '1' && e.key <= '4') {
                const themes = ['work', 'life', 'training', 'emo'];
                const themeIndex = parseInt(e.key) - 1;
                if (themes[themeIndex]) {
                    this.switchTheme(themes[themeIndex]);
                }
            }
        });
    }
    
    /**
     * 切换主题
     * @param {string} theme - 主题名称
     * @param {boolean} saveToServer - 是否保存到服务器
     */
    async switchTheme(theme, saveToServer = true) {
        if (!this.themes[theme]) {
            // 无效的主题
            return false;
        }

        try {
            // 应用主题样式
            this.applyTheme(theme);
            
            // 保存到本地存储
            localStorage.setItem('currentTheme', theme);
            this.currentTheme = theme;
            
            // 保存到服务器
            if (saveToServer) {
                await this.saveThemeToServer(theme);
            }
            
            // 触发主题切换事件
            this.triggerThemeChangeEvent(theme);

            return true;
            
        } catch (error) {
            // 主题切换失败
            return false;
        }
    }
    
    /**
     * 应用主题样式
     * @param {string} theme - 主题名称
     */
    applyTheme(theme) {
        const themeConfig = this.themes[theme];
        if (!themeConfig) return;
        
        const body = document.body;
        const root = document.documentElement;
        
        // 移除之前的主题类
        body.classList.remove('theme-work', 'theme-life', 'theme-training', 'theme-emo');
        
        // 添加新主题类
        body.classList.add(`theme-${theme}`);
        
        // 动态加载主题CSS文件
        this.loadThemeCSS(theme);
        
        // 应用背景和颜色
        body.style.background = themeConfig.background;
        body.style.color = themeConfig.color;
        
        // 设置CSS变量
        root.style.setProperty('--theme-primary', themeConfig.buttonColors.primary);
        root.style.setProperty('--theme-secondary', themeConfig.buttonColors.secondary);
        root.style.setProperty('--theme-success', themeConfig.buttonColors.success);
        root.style.setProperty('--theme-danger', themeConfig.buttonColors.danger);
        
        // 更新主题标识
        this.updateThemeIndicator(theme);
    }
    
    /**
     * 动态加载主题CSS文件
     * @param {string} theme - 主题名称
     */
    loadThemeCSS(theme) {
        const themeCSSMap = {
            'work': '/static/geek.css',
            'life': '/static/life.css',
            'training': '/static/rage.css',
            'emo': '/static/emo.css'
        };
        
        const cssUrl = themeCSSMap[theme];
        if (!cssUrl) return;
        
        // 移除之前的主题CSS
        const existingLink = document.querySelector(`link[href*="${themeCSSMap[theme]}"]`);
        if (existingLink) {
            existingLink.remove();
        }
        
        // 添加新的主题CSS
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = cssUrl;
        link.id = `theme-css-${theme}`;
        document.head.appendChild(link);

    }
    
    /**
     * 更新主题标识
     * @param {string} theme - 主题名称
     */
    updateThemeIndicator(theme) {
        const themeConfig = this.themes[theme];
        if (!themeConfig) return;
        
        // 更新页面标题
        const titleElement = document.querySelector('title');
        if (titleElement) {
            const originalTitle = titleElement.getAttribute('data-original-title') || titleElement.textContent;
            titleElement.setAttribute('data-original-title', originalTitle);
            titleElement.textContent = `${themeConfig.name} - ${originalTitle}`;
        }
        
        // 更新主题标识元素
        const themeIndicator = document.getElementById('theme-indicator');
        if (themeIndicator) {
            themeIndicator.textContent = themeConfig.name;
        }
        
        // 更新关于按钮
        const aboutButton = document.getElementById('aboutButton');
        if (aboutButton) {
            const span = aboutButton.querySelector('span');
            if (span) {
                span.textContent = themeConfig.name;
            }
        }
    }
    
    /**
     * 保存主题到服务器
     * @param {string} theme - 主题名称
     */
    async saveThemeToServer(theme) {
        try {
            const response = await fetch(this.apiBaseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ mode: theme })  // 修改参数名从 theme 改为 mode
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || '保存失败');
            }

        } catch (error) {
            // 保存主题到服务器失败
            // 不抛出错误，因为本地保存已经成功
        }
    }
    
    /**
     * 从服务器获取主题
     */
    async getThemeFromServer() {
        try {
            const response = await fetch(this.apiBaseUrl);
            const data = await response.json();
            
            if (data.success) {
                return data.data.mode;  // 从 data.mode 获取主题
            }
            
        } catch (error) {
            // 从服务器获取主题失败
        }
        
        return null;
    }
    
    /**
     * 获取当前主题
     */
    getCurrentTheme() {
        return this.currentTheme;
    }
    
    /**
     * 获取主题配置
     * @param {string} theme - 主题名称
     */
    getThemeConfig(theme) {
        return this.themes[theme] || null;
    }
    
    /**
     * 获取所有可用主题
     */
    getAvailableThemes() {
        return Object.keys(this.themes);
    }
    
    /**
     * 创建主题切换按钮
     * @param {string} containerSelector - 容器选择器
     */
    createThemeButtons(containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) return;
        
        const buttonsHtml = Object.entries(this.themes).map(([key, config]) => `
            <button 
                class="theme-btn ${key === this.currentTheme ? 'active' : ''}" 
                data-theme="${key}"
                style="
                    padding: 12px; 
                    border-radius: 8px; 
                    background: rgba(255, 255, 255, 0.1); 
                    color: white; 
                    border: 1px solid rgba(255, 255, 255, 0.3); 
                    cursor: pointer; 
                    transition: all 0.3s ease;
                    margin: 5px;
                "
            >
                <div style="font-weight: 600;">${config.name}</div>
                <div style="font-size: 0.8rem; opacity: 0.8;">
                    ${key === 'work' ? '专注技术' : 
                      key === 'life' ? '轻松愉悦' : 
                      key === 'training' ? '激情四射' : '情感表达'}
                </div>
            </button>
        `).join('');
        
        container.innerHTML = `
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: 600;">🎨 主题模式</label>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    ${buttonsHtml}
                </div>
            </div>
        `;
    }
    
    /**
     * 触发主题切换事件
     * @param {string} theme - 主题名称
     */
    triggerThemeChangeEvent(theme) {
        const event = new CustomEvent('themeChange', {
            detail: {
                theme: theme,
                config: this.themes[theme]
            }
        });
        document.dispatchEvent(event);
    }
    
    /**
     * 获取CSRF Token
     */
    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }
    
    /**
     * 显示主题切换通知
     * @param {string} theme - 主题名称
     */
    showThemeNotification(theme) {
        const themeConfig = this.themes[theme];
        if (!themeConfig) return;
        
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${themeConfig.buttonColors.primary};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.2rem;">🎨</span>
                <span>已切换到 ${themeConfig.name}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // 3秒后移除通知
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, 3000);
    }
}

// 添加CSS动画
const themeStyle = document.createElement('style');
themeStyle.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .theme-btn.active {
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.6) !important;
    }
    
    .theme-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
`;
document.head.appendChild(themeStyle);

// 创建全局实例
window.ThemeManager = new ThemeManager();

// 导出到模块系统（如果支持）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
