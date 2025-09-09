/**
 * 移动端优化JavaScript - 性能优先
 * 包含触摸优化、懒加载、性能监控等功能
 */

(function() {
    'use strict';
    
    // 性能监控
    const performanceMonitor = {
        startTime: performance.now(),
        
        log: function(message) {
            if (window.console && window.console.log) {
                console.log(`[Mobile Optimized] ${message}`);
            }
        },
        
        measure: function(name, fn) {
            const start = performance.now();
            const result = fn();
            const end = performance.now();
            this.log(`${name} took ${(end - start).toFixed(2)}ms`);
            return result;
        }
    };
    
    // 触摸优化
    const touchOptimizer = {
        init: function() {
            this.addTouchClasses();
            this.optimizeScroll();
            this.addTouchFeedback();
        },
        
        addTouchClasses: function() {
            if ('ontouchstart' in window) {
                document.documentElement.classList.add('touch-device');
            } else {
                document.documentElement.classList.add('no-touch');
            }
        },
        
        optimizeScroll: function() {
            // 优化滚动性能
            let ticking = false;
            
            function updateScroll() {
                // 滚动处理逻辑
                ticking = false;
            }
            
            function requestTick() {
                if (!ticking) {
                    requestAnimationFrame(updateScroll);
                    ticking = true;
                }
            }
            
            window.addEventListener('scroll', requestTick, { passive: true });
        },
        
        addTouchFeedback: function() {
            // 为按钮添加触摸反馈
            const buttons = document.querySelectorAll('.btn, .nav-link, .dropdown-item');
            
            buttons.forEach(button => {
                button.addEventListener('touchstart', function() {
                    this.classList.add('touch-active');
                }, { passive: true });
                
                button.addEventListener('touchend', function() {
                    setTimeout(() => {
                        this.classList.remove('touch-active');
                    }, 150);
                }, { passive: true });
            });
        }
    };
    
    // 懒加载优化
    const lazyLoader = {
        init: function() {
            if ('IntersectionObserver' in window) {
                this.setupIntersectionObserver();
            } else {
                this.fallbackLazyLoad();
            }
        },
        
        setupIntersectionObserver: function() {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        this.loadImage(img);
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });
            
            const images = document.querySelectorAll('img[data-src]');
            images.forEach(img => imageObserver.observe(img));
        },
        
        loadImage: function(img) {
            const src = img.getAttribute('data-src');
            if (src) {
                img.src = src;
                img.classList.remove('lazy');
                img.classList.add('loaded');
            }
        },
        
        fallbackLazyLoad: function() {
            const images = document.querySelectorAll('img[data-src]');
            const loadImages = () => {
                images.forEach(img => {
                    const rect = img.getBoundingClientRect();
                    if (rect.top < window.innerHeight && rect.bottom > 0) {
                        this.loadImage(img);
                    }
                });
            };
            
            window.addEventListener('scroll', loadImages, { passive: true });
            loadImages(); // 初始加载
        }
    };
    
    // 移动端导航优化
    const mobileNav = {
        init: function() {
            this.createMobileMenu();
            this.optimizeDropdowns();
        },
        
        createMobileMenu: function() {
            const navbar = document.querySelector('.navbar');
            if (!navbar) return;
            
            // 创建移动端菜单按钮
            const menuButton = document.createElement('button');
            menuButton.className = 'navbar-toggler d-md-none';
            menuButton.innerHTML = '<i class="fas fa-bars"></i>';
            menuButton.setAttribute('aria-label', 'Toggle navigation');
            
            // 创建移动端菜单
            const mobileMenu = document.createElement('div');
            mobileMenu.className = 'mobile-menu';
            mobileMenu.innerHTML = `
                <div class="mobile-menu-content">
                    <div class="mobile-menu-header">
                        <h5>菜单</h5>
                        <button class="mobile-menu-close" aria-label="关闭菜单">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="mobile-menu-body"></div>
                </div>
            `;
            
            // 移动导航项到移动菜单
            const navItems = navbar.querySelector('.navbar-nav');
            if (navItems) {
                const mobileMenuBody = mobileMenu.querySelector('.mobile-menu-body');
                mobileMenuBody.appendChild(navItems.cloneNode(true));
                
                // 隐藏原始导航
                navItems.style.display = 'none';
            }
            
            // 添加事件监听
            menuButton.addEventListener('click', () => {
                mobileMenu.classList.toggle('active');
                document.body.classList.toggle('menu-open');
            });
            
            mobileMenu.querySelector('.mobile-menu-close').addEventListener('click', () => {
                mobileMenu.classList.remove('active');
                document.body.classList.remove('menu-open');
            });
            
            // 点击背景关闭菜单
            mobileMenu.addEventListener('click', (e) => {
                if (e.target === mobileMenu) {
                    mobileMenu.classList.remove('active');
                    document.body.classList.remove('menu-open');
                }
            });
            
            // 添加到页面
            navbar.appendChild(menuButton);
            document.body.appendChild(mobileMenu);
        },
        
        optimizeDropdowns: function() {
            const dropdowns = document.querySelectorAll('.dropdown');
            
            dropdowns.forEach(dropdown => {
                const toggle = dropdown.querySelector('.dropdown-toggle');
                const menu = dropdown.querySelector('.dropdown-menu');
                
                if (toggle && menu) {
                    // 移动端优化：点击切换
                    toggle.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // 关闭其他下拉菜单
                        dropdowns.forEach(other => {
                            if (other !== dropdown) {
                                other.classList.remove('show');
                            }
                        });
                        
                        dropdown.classList.toggle('show');
                    });
                }
            });
            
            // 点击外部关闭下拉菜单
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.dropdown')) {
                    dropdowns.forEach(dropdown => {
                        dropdown.classList.remove('show');
                    });
                }
            });
        }
    };
    
    // 表单优化
    const formOptimizer = {
        init: function() {
            this.optimizeInputs();
            this.addFormValidation();
            this.optimizeFileUploads();
        },
        
        optimizeInputs: function() {
            const inputs = document.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                // 移动端键盘优化
                if (input.type === 'email') {
                    input.setAttribute('autocomplete', 'email');
                } else if (input.type === 'password') {
                    input.setAttribute('autocomplete', 'current-password');
                } else if (input.type === 'tel') {
                    input.setAttribute('inputmode', 'tel');
                } else if (input.type === 'number') {
                    input.setAttribute('inputmode', 'numeric');
                }
                
                // 添加焦点样式
                input.addEventListener('focus', function() {
                    this.parentElement.classList.add('focused');
                });
                
                input.addEventListener('blur', function() {
                    this.parentElement.classList.remove('focused');
                });
            });
        },
        
        addFormValidation: function() {
            const forms = document.querySelectorAll('form');
            
            forms.forEach(form => {
                form.addEventListener('submit', (e) => {
                    if (!form.checkValidity()) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // 显示验证错误
                        const firstInvalid = form.querySelector(':invalid');
                        if (firstInvalid) {
                            firstInvalid.focus();
                            firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }
                    
                    form.classList.add('was-validated');
                });
            });
        },
        
        optimizeFileUploads: function() {
            const fileInputs = document.querySelectorAll('input[type="file"]');
            
            fileInputs.forEach(input => {
                // 添加文件预览
                input.addEventListener('change', function() {
                    const files = this.files;
                    if (files.length > 0) {
                        this.parentElement.classList.add('has-files');
                        
                        // 显示文件信息
                        const fileInfo = document.createElement('div');
                        fileInfo.className = 'file-info';
                        fileInfo.textContent = `${files.length} 个文件已选择`;
                        
                        const existingInfo = this.parentElement.querySelector('.file-info');
                        if (existingInfo) {
                            existingInfo.remove();
                        }
                        
                        this.parentElement.appendChild(fileInfo);
                    }
                });
            });
        }
    };
    
    // 性能优化
    const performanceOptimizer = {
        init: function() {
            this.debounceScroll();
            this.optimizeAnimations();
            this.preloadCriticalResources();
        },
        
        debounceScroll: function() {
            let scrollTimeout;
            
            window.addEventListener('scroll', () => {
                if (scrollTimeout) {
                    clearTimeout(scrollTimeout);
                }
                
                scrollTimeout = setTimeout(() => {
                    // 滚动结束后的处理
                    this.handleScrollEnd();
                }, 100);
            }, { passive: true });
        },
        
        handleScrollEnd: function() {
            // 滚动结束后的优化处理
            const navbar = document.querySelector('.navbar');
            if (navbar) {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > 100) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
            }
        },
        
        optimizeAnimations: function() {
            // 减少动画以提升性能
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                document.documentElement.classList.add('reduce-motion');
            }
        },
        
        preloadCriticalResources: function() {
            // 预加载关键资源
            const criticalImages = document.querySelectorAll('img[data-preload]');
            criticalImages.forEach(img => {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.as = 'image';
                link.href = img.getAttribute('data-preload');
                document.head.appendChild(link);
            });
        }
    };
    
    // 错误处理
    const errorHandler = {
        init: function() {
            window.addEventListener('error', this.handleError);
            window.addEventListener('unhandledrejection', this.handlePromiseRejection);
        },
        
        handleError: function(event) {
            performanceMonitor.log(`JavaScript Error: ${event.message} at ${event.filename}:${event.lineno}`);
            
            // 在开发环境中显示错误
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.error('Error:', event.error);
            }
        },
        
        handlePromiseRejection: function(event) {
            performanceMonitor.log(`Unhandled Promise Rejection: ${event.reason}`);
            
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.error('Promise Rejection:', event.reason);
            }
        }
    };
    
    // 网络状态监控
    const networkMonitor = {
        init: function() {
            if ('connection' in navigator) {
                this.monitorConnection();
            }
            
            this.handleOffline();
            this.handleOnline();
        },
        
        monitorConnection: function() {
            const connection = navigator.connection;
            
            connection.addEventListener('change', () => {
                const effectiveType = connection.effectiveType;
                performanceMonitor.log(`Connection changed to: ${effectiveType}`);
                
                // 根据网络状况调整加载策略
                if (effectiveType === 'slow-2g' || effectiveType === '2g') {
                    document.documentElement.classList.add('slow-connection');
                } else {
                    document.documentElement.classList.remove('slow-connection');
                }
            });
        },
        
        handleOffline: function() {
            window.addEventListener('offline', () => {
                performanceMonitor.log('Network offline');
                this.showOfflineMessage();
            });
        },
        
        handleOnline: function() {
            window.addEventListener('online', () => {
                performanceMonitor.log('Network online');
                this.hideOfflineMessage();
            });
        },
        
        showOfflineMessage: function() {
            const message = document.createElement('div');
            message.id = 'offline-message';
            message.className = 'alert alert-warning position-fixed';
            message.style.cssText = 'top: 0; left: 0; right: 0; z-index: 9999; margin: 0; border-radius: 0;';
            message.innerHTML = '<i class="fas fa-wifi"></i> 网络连接已断开，请检查网络设置';
            document.body.appendChild(message);
        },
        
        hideOfflineMessage: function() {
            const message = document.getElementById('offline-message');
            if (message) {
                message.remove();
            }
        }
    };
    
    // 初始化所有优化功能
    const init = function() {
        performanceMonitor.measure('Initialization', () => {
            touchOptimizer.init();
            lazyLoader.init();
            mobileNav.init();
            formOptimizer.init();
            performanceOptimizer.init();
            errorHandler.init();
            networkMonitor.init();
        });
        
        performanceMonitor.log('Mobile optimization initialized');
    };
    
    // DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // 暴露一些工具函数到全局
    window.MobileOptimizer = {
        performanceMonitor,
        touchOptimizer,
        lazyLoader,
        mobileNav,
        formOptimizer,
        performanceOptimizer
    };
    
})();
