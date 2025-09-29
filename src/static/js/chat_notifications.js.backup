/**
 * 聊天消息通知系统
 * 用于在右上角显示未读消息提示
 */

class ChatNotificationManager {
    constructor() {
        this.unreadCount = 0;
        this.notifications = [];
        this.isVisible = false;
        this.pollInterval = null;
        this.isDragging = false;
        this.currentX = 0;
        this.currentY = 0;
        this.xOffset = 0;
        this.yOffset = 0;
        this.init();
    }

    init() {
        try {
            console.log('ChatNotificationManager: 开始初始化');
            this.createNotificationUI();
            this.startPolling();
            this.bindEvents();
            console.log('ChatNotificationManager: 初始化完成');
        } catch (error) {
            console.error('ChatNotificationManager: 初始化失败', error);
        }
    }

    getUserAvatar() {
        // 尝试从多个位置获取用户头像
        const avatarSelectors = [
            '.top-ui-avatar img',
            '.user-avatar img',
            '.avatar img',
            '.profile-avatar img',
            '.user-profile img',
            '[class*="avatar"] img',
            'img[src*="avatar"]',
            'img[src*="media"]',
            '.top-ui-bar img',
            '.user-info img'
        ];
        
        console.log('开始检测用户头像...');
        
        for (const selector of avatarSelectors) {
            const avatarImg = document.querySelector(selector);
            console.log(`检测选择器: ${selector}`, avatarImg);
            
            if (avatarImg && avatarImg.src) {
                console.log(`找到头像图片: ${avatarImg.src}`);
                
                // 检查是否是有效头像（不是默认头像）
                if (!avatarImg.src.includes('default') && 
                    !avatarImg.src.includes('placeholder') &&
                    !avatarImg.src.includes('blank') &&
                    avatarImg.src.length > 10) {
                    console.log('使用用户头像创建机器人');
                    return avatarImg.src;
                } else {
                    console.log('跳过默认头像:', avatarImg.src);
                }
            }
        }
        
        // 如果没找到，返回null使用默认乌萨奇
        console.log('未找到用户头像，使用默认乌萨奇');
        return null;
    }

    createNotificationUI() {
        // 如果已存在，先移除
        const existing = document.getElementById('chat-notification-manager');
        if (existing) {
            existing.remove();
        }

        // 检查用户头像
        const userAvatar = this.getUserAvatar();
        console.log('检测到的用户头像:', userAvatar);
        
        // 创建通知区域
        const notificationArea = document.createElement('div');
        notificationArea.id = 'chat-notification-manager';
        notificationArea.className = 'chat-notification-manager';
        
        let characterHTML = '';
        if (userAvatar) {
            console.log('创建用户头像形象');
            // 使用用户头像创建可爱形象
            characterHTML = `
                <div class="avatar-character" id="avatar-character">
                    <div class="character-head">
                        <img src="${userAvatar}" alt="User Avatar" class="avatar-image">
                        <div class="character-accessories">
                            <div class="sparkle sparkle-1"></div>
                            <div class="sparkle sparkle-2"></div>
                            <div class="sparkle sparkle-3"></div>
                        </div>
                    </div>
                    <div class="character-body">
                        <div class="character-wings left-wing"></div>
                        <div class="character-wings right-wing"></div>
                        <div class="character-heart"></div>
                    </div>
                </div>
            `;
        } else {
            console.log('使用默认乌萨奇');
            // 使用默认乌萨奇
            characterHTML = `
                <div class="usaki-character" id="usaki-character">
                    <div class="usaki-head">
                        <div class="usaki-ear left-ear"></div>
                        <div class="usaki-ear right-ear"></div>
                        <div class="usaki-face">
                            <div class="usaki-eye left-eye"></div>
                            <div class="usaki-eye right-eye"></div>
                            <div class="usaki-blush left-blush"></div>
                            <div class="usaki-blush right-blush"></div>
                            <div class="usaki-mouth"></div>
                        </div>
                    </div>
                    <div class="usaki-body">
                        <div class="usaki-button top-button"></div>
                        <div class="usaki-button bottom-button"></div>
                        <div class="usaki-arm left-arm"></div>
                        <div class="usaki-arm right-arm"></div>
                        <div class="usaki-leg left-leg"></div>
                        <div class="usaki-leg right-leg"></div>
                    </div>
                </div>
            `;
        }
        
        notificationArea.innerHTML = `
            <div class="notification-icon" id="notification-icon">
                ${characterHTML}
            </div>
            <!-- 未读消息红标 -->
            <div class="unread-badge" id="unread-badge" style="display: none;">
                <span class="unread-count">0</span>
            </div>
            <!-- 右上角消息提示 -->
            <div class="message-toast" id="message-toast" style="display: none;">
                <div class="toast-content">
                    <i class="fas fa-robot"></i>
                    <span class="toast-text">【新消息】</span>
                </div>
            </div>
            <div class="notification-dropdown" id="notification-dropdown" style="display: none;">
                <div class="notification-header">
                    <h3>未读消息</h3>
                    <button class="clear-all-btn" id="clear-all-notifications">全部标记已读</button>
                </div>
                <div class="drag-hint">
                    <small>💡 提示：拖拽图标可移动位置，双击可重置</small>
                </div>
                <div class="notification-list" id="notification-list">
                    <div class="no-notifications">暂无未读消息</div>
                </div>
            </div>
        `;

        // 添加样式
        const style = document.createElement('style');
        style.textContent = `
            .chat-notification-manager {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                user-select: none;
                transition: none;
            }

            .chat-notification-manager.dragging {
                transition: none !important;
            }

            .notification-icon {
                position: relative;
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, #ffd700, #ffed4e);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                cursor: move;
                box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
                border: 2px solid #ffd700;
                transition: all 0.3s ease;
            }

            /* 用户头像形象样式 */
            .avatar-character {
                width: 32px;
                height: 32px;
                position: relative;
                animation: avatarCharacterIdle 4s ease-in-out infinite;
            }

            .character-head {
                width: 24px;
                height: 24px;
                position: relative;
                margin: 0 auto 2px;
                border-radius: 50%;
                overflow: hidden;
                border: 3px solid #ff6b9d;
                background: linear-gradient(135deg, #ff9a9e, #fecfef);
                box-shadow: 0 0 15px rgba(255, 107, 157, 0.4);
            }

            .avatar-image {
                width: 100%;
                height: 100%;
                object-fit: cover;
                border-radius: 50%;
            }

            .character-accessories {
                position: absolute;
                top: -5px;
                left: -5px;
                right: -5px;
                bottom: -5px;
                pointer-events: none;
            }

            .sparkle {
                position: absolute;
                width: 3px;
                height: 3px;
                background: #fff;
                border-radius: 50%;
                animation: sparkleTwinkle 2s ease-in-out infinite;
            }

            .sparkle-1 {
                top: 2px;
                right: 2px;
                animation-delay: 0s;
            }

            .sparkle-2 {
                top: 8px;
                left: 2px;
                animation-delay: 0.7s;
            }

            .sparkle-3 {
                bottom: 2px;
                right: 8px;
                animation-delay: 1.4s;
            }

            .character-body {
                width: 20px;
                height: 12px;
                position: relative;
                margin: 0 auto;
            }

            .character-wings {
                position: absolute;
                top: 2px;
                width: 8px;
                height: 6px;
                background: linear-gradient(135deg, #ff9a9e, #fecfef);
                border-radius: 50% 0 0 50%;
                animation: wingFlutter 1.5s ease-in-out infinite;
            }

            .left-wing {
                left: -2px;
                animation-delay: 0s;
            }

            .right-wing {
                right: -2px;
                transform: scaleX(-1);
                animation-delay: 0.75s;
            }

            .character-heart {
                position: absolute;
                top: 4px;
                left: 50%;
                transform: translateX(-50%);
                width: 4px;
                height: 4px;
                background: #ff6b9d;
                border-radius: 50% 50% 50% 0;
                transform: translateX(-50%) rotate(-45deg);
                animation: heartBeat 2s ease-in-out infinite;
            }

            /* 乌萨奇角色样式 - 基于图片设计 */
            .usaki-character {
                width: 32px;
                height: 32px;
                position: relative;
                animation: usakiIdle 4s ease-in-out infinite;
            }

            .usaki-head {
                width: 20px;
                height: 20px;
                background: #fffacd;
                border-radius: 50%;
                position: relative;
                margin: 0 auto 1px;
                border: 1px solid #000;
            }

            .usaki-ear {
                position: absolute;
                top: -3px;
                width: 5px;
                height: 8px;
                background: #ffd700;
                border-radius: 50% 50% 0 0;
                border: 1px solid #000;
            }

            .usaki-ear.left-ear {
                left: 2px;
                transform: rotate(-10deg);
            }

            .usaki-ear.right-ear {
                right: 2px;
                transform: rotate(10deg);
            }

            .usaki-face {
                position: absolute;
                top: 3px;
                left: 50%;
                transform: translateX(-50%);
                width: 14px;
                height: 12px;
            }

            .usaki-eye {
                position: absolute;
                top: 1px;
                width: 2px;
                height: 2px;
                background: #000;
                border-radius: 50%;
                animation: eyeBlink 4s ease-in-out infinite;
            }

            .usaki-eye.left-eye {
                left: 1px;
            }

            .usaki-eye.right-eye {
                right: 1px;
            }

            .usaki-blush {
                position: absolute;
                top: 3px;
                width: 3px;
                height: 1px;
                background: #ffb6c1;
                border-radius: 1px;
            }

            .usaki-blush.left-blush {
                left: -1px;
            }

            .usaki-blush.right-blush {
                right: -1px;
            }

            .usaki-mouth {
                position: absolute;
                top: 6px;
                left: 50%;
                transform: translateX(-50%);
                width: 4px;
                height: 1px;
                background: #000;
                border-radius: 1px;
                animation: mouthMove 3s ease-in-out infinite;
            }

            .usaki-body {
                width: 18px;
                height: 12px;
                background: #ffd700;
                border-radius: 8px 8px 12px 12px;
                position: relative;
                margin: 0 auto;
                border: 1px solid #000;
            }

            .usaki-button {
                position: absolute;
                top: 2px;
                left: 50%;
                transform: translateX(-50%);
                width: 2px;
                height: 2px;
                background: #000;
                border-radius: 50%;
            }

            .usaki-button.top-button {
                top: 2px;
            }

            .usaki-button.bottom-button {
                top: 5px;
            }

            .usaki-arm {
                position: absolute;
                top: 3px;
                width: 3px;
                height: 4px;
                background: #ffd700;
                border-radius: 2px;
                border: 1px solid #000;
                animation: armMove 2.5s ease-in-out infinite;
            }

            .usaki-arm.left-arm {
                left: -1px;
                animation-delay: 0s;
            }

            .usaki-arm.right-arm {
                right: -1px;
                animation-delay: 1.25s;
            }

            .usaki-leg {
                position: absolute;
                bottom: -2px;
                width: 4px;
                height: 3px;
                background: #ffd700;
                border-radius: 2px;
                border: 1px solid #000;
                animation: legMove 2s ease-in-out infinite;
            }

            .usaki-leg.left-leg {
                left: 3px;
                animation-delay: 0s;
            }

            .usaki-leg.right-leg {
                right: 3px;
                animation-delay: 1s;
            }

            /* 动画效果 */
            @keyframes avatarCharacterIdle {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                25% { transform: translateY(-1px) rotate(0.5deg); }
                50% { transform: translateY(0px) rotate(0deg); }
                75% { transform: translateY(-0.5px) rotate(-0.5deg); }
            }

            @keyframes sparkleTwinkle {
                0%, 100% { opacity: 0.3; transform: scale(0.8); }
                50% { opacity: 1; transform: scale(1.2); }
            }

            @keyframes wingFlutter {
                0%, 100% { transform: rotate(0deg); }
                50% { transform: rotate(10deg); }
            }

            @keyframes heartBeat {
                0%, 100% { transform: translateX(-50%) rotate(-45deg) scale(1); }
                50% { transform: translateX(-50%) rotate(-45deg) scale(1.2); }
            }


            /* 拖动时的动画效果 */
            @keyframes dragCharacterWiggle {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                25% { transform: translateY(-2px) rotate(-2deg); }
                50% { transform: translateY(0px) rotate(0deg); }
                75% { transform: translateY(-1px) rotate(2deg); }
            }

            @keyframes dragUsakiWiggle {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                25% { transform: translateY(-2px) rotate(-2deg); }
                50% { transform: translateY(0px) rotate(0deg); }
                75% { transform: translateY(-1px) rotate(2deg); }
            }

            @keyframes dragSparkleSpin {
                0% { transform: rotate(0deg) scale(1); }
                50% { transform: rotate(180deg) scale(1.3); }
                100% { transform: rotate(360deg) scale(1); }
            }

            @keyframes dragWingFlap {
                0%, 100% { transform: rotate(0deg); }
                50% { transform: rotate(20deg); }
            }

            @keyframes dragHeartPulse {
                0%, 100% { transform: translateX(-50%) rotate(-45deg) scale(1); }
                50% { transform: translateX(-50%) rotate(-45deg) scale(1.5); }
            }

            @keyframes dragEarWiggle {
                0%, 100% { transform: rotate(0deg); }
                25% { transform: rotate(-10deg); }
                75% { transform: rotate(10deg); }
            }

            @keyframes dragTailWag {
                0%, 100% { transform: rotate(0deg); }
                50% { transform: rotate(15deg); }
            }

            @keyframes dragParticleGlow {
                0%, 100% { 
                    opacity: 0.3; 
                    transform: translate(-50%, -50%) scale(1); 
                }
                50% { 
                    opacity: 0.8; 
                    transform: translate(-50%, -50%) scale(1.2); 
                }
            }

            @keyframes dragTrail {
                0% { 
                    opacity: 0; 
                    transform: translateX(0px) scale(0.5); 
                }
                50% { 
                    opacity: 1; 
                    transform: translateX(-5px) scale(1); 
                }
                100% { 
                    opacity: 0; 
                    transform: translateX(-10px) scale(0.5); 
                }
            }

            @keyframes dragShake {
                0%, 100% { transform: scale(1.1) rotate(5deg) translateX(0px); }
                25% { transform: scale(1.1) rotate(5deg) translateX(-1px) translateY(-1px); }
                50% { transform: scale(1.1) rotate(5deg) translateX(1px) translateY(1px); }
                75% { transform: scale(1.1) rotate(5deg) translateX(-1px) translateY(1px); }
            }

            @keyframes dragStartBounce {
                0% { transform: scale(1) rotate(0deg); }
                50% { transform: scale(1.2) rotate(10deg); }
                100% { transform: scale(1.1) rotate(5deg); }
            }

            @keyframes dragEndBounce {
                0% { transform: scale(1.1) rotate(5deg); }
                25% { transform: scale(1.3) rotate(-5deg); }
                50% { transform: scale(0.9) rotate(3deg); }
                75% { transform: scale(1.1) rotate(-2deg); }
                100% { transform: scale(1) rotate(0deg); }
            }

            @keyframes robotEyeBlink {
                0%, 90%, 100% { opacity: 1; }
                95% { opacity: 0.3; }
            }

            @keyframes robotMouthMove {
                0%, 100% { transform: translateX(-50%) scaleX(1); }
                50% { transform: translateX(-50%) scaleX(1.2); }
            }

            @keyframes antennaGlow {
                0%, 100% { opacity: 0.6; box-shadow: 0 0 2px #00ff88; }
                50% { opacity: 1; box-shadow: 0 0 6px #00ff88; }
            }

            @keyframes robotLegMove {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-1px); }
            }

            @keyframes usakiIdle {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                25% { transform: translateY(-1px) rotate(0.5deg); }
                50% { transform: translateY(0px) rotate(0deg); }
                75% { transform: translateY(-0.5px) rotate(-0.5deg); }
            }

            @keyframes eyeBlink {
                0%, 90%, 100% { transform: scaleY(1); }
                95% { transform: scaleY(0.1); }
            }

            @keyframes mouthMove {
                0%, 100% { transform: translateX(-50%) scaleX(1); }
                50% { transform: translateX(-50%) scaleX(1.3); }
            }

            @keyframes armMove {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-1px); }
            }

            @keyframes legMove {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-1px); }
            }

            /* 新消息时的底部跑圈动画 */
            .avatar-character.new-message {
                animation: avatarCharacterRunAround 3s ease-in-out;
                z-index: 1000;
            }

            .usaki-character.new-message {
                animation: usakiRunAround 3s ease-in-out;
                z-index: 1000;
            }

            /* 跑圈动画时的发光效果 */
            .notification-icon .avatar-character.new-message,
            .notification-icon .usaki-character.new-message {
                filter: drop-shadow(0 0 10px #00ff88) drop-shadow(0 0 20px #00ff88);
            }

            /* 振动效果 */
            .notification-icon.vibrate {
                animation: vibrate 0.5s ease-in-out;
            }

            @keyframes vibrate {
                0%, 100% { transform: translateX(0px) translateY(0px); }
                10% { transform: translateX(-2px) translateY(-1px); }
                20% { transform: translateX(2px) translateY(1px); }
                30% { transform: translateX(-2px) translateY(1px); }
                40% { transform: translateX(2px) translateY(-1px); }
                50% { transform: translateX(-1px) translateY(2px); }
                60% { transform: translateX(1px) translateY(-2px); }
                70% { transform: translateX(-1px) translateY(-1px); }
                80% { transform: translateX(1px) translateY(1px); }
                90% { transform: translateX(-1px) translateY(0px); }
            }

            /* 未读消息红标样式 */
            .unread-badge {
                position: absolute;
                top: -5px;
                right: -5px;
                background: #ff4757;
                color: white;
                border-radius: 50%;
                min-width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 11px;
                font-weight: bold;
                z-index: 1001;
                box-shadow: 0 2px 8px rgba(255, 71, 87, 0.4);
                border: 2px solid white;
                animation: badgePulse 2s ease-in-out infinite;
            }

            .unread-count {
                padding: 0 4px;
                min-width: 12px;
                text-align: center;
            }

            @keyframes badgePulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }

            @keyframes avatarCharacterRunAround {
                0% { transform: translateX(0px) translateY(0px) rotate(0deg) scale(1); }
                12.5% { transform: translateX(30px) translateY(-15px) rotate(45deg) scale(1.5); }
                25% { transform: translateX(40px) translateY(-25px) rotate(90deg) scale(1.8); }
                37.5% { transform: translateX(30px) translateY(-35px) rotate(135deg) scale(1.5); }
                50% { transform: translateX(0px) translateY(-40px) rotate(180deg) scale(1); }
                62.5% { transform: translateX(-30px) translateY(-35px) rotate(225deg) scale(1.5); }
                75% { transform: translateX(-40px) translateY(-25px) rotate(270deg) scale(1.8); }
                87.5% { transform: translateX(-30px) translateY(-15px) rotate(315deg) scale(1.5); }
                100% { transform: translateX(0px) translateY(0px) rotate(360deg) scale(1); }
            }

            @keyframes usakiRunAround {
                0% { transform: translateX(0px) translateY(0px) rotate(0deg) scale(1); }
                12.5% { transform: translateX(30px) translateY(-15px) rotate(45deg) scale(1.5); }
                25% { transform: translateX(40px) translateY(-25px) rotate(90deg) scale(1.8); }
                37.5% { transform: translateX(30px) translateY(-35px) rotate(135deg) scale(1.5); }
                50% { transform: translateX(0px) translateY(-40px) rotate(180deg) scale(1); }
                62.5% { transform: translateX(-30px) translateY(-35px) rotate(225deg) scale(1.5); }
                75% { transform: translateX(-40px) translateY(-25px) rotate(270deg) scale(1.8); }
                87.5% { transform: translateX(-30px) translateY(-15px) rotate(315deg) scale(1.5); }
                100% { transform: translateX(0px) translateY(0px) rotate(360deg) scale(1); }
            }

            /* 悬停时的动画 */
            .notification-icon:hover .avatar-character {
                animation: avatarCharacterHover 0.5s ease-in-out;
            }

            .notification-icon:hover .usaki-character {
                animation: usakiHover 0.5s ease-in-out;
            }

            @keyframes avatarCharacterHover {
                0% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-3px) rotate(5deg); }
                100% { transform: translateY(0px) rotate(0deg); }
            }

            @keyframes usakiHover {
                0% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-3px) rotate(5deg); }
                100% { transform: translateY(0px) rotate(0deg); }
            }

            /* 右上角消息提示样式 */
            .message-toast {
                position: fixed;
                top: 20px;
                right: 80px;
                z-index: 10000;
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                border: 2px solid #00ff88;
                border-radius: 12px;
                padding: 12px 16px;
                box-shadow: 0 8px 32px rgba(0, 255, 136, 0.3);
                backdrop-filter: blur(10px);
                transform: translateX(100%);
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .message-toast.show {
                transform: translateX(0);
            }

            .toast-content {
                display: flex;
                align-items: center;
                gap: 8px;
                color: #00ff88;
                font-size: 14px;
                font-weight: 600;
            }

            .toast-content i {
                font-size: 16px;
                animation: robotIconPulse 1s ease-in-out infinite;
            }

            @keyframes robotIconPulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }


            .notification-icon.dragging {
                cursor: grabbing;
                transform: scale(1.1) rotate(5deg);
                box-shadow: 0 12px 30px rgba(255, 215, 0, 0.6);
                transition: none !important;
                animation: dragShake 0.1s ease-in-out infinite;
            }

            .notification-icon.drag-start {
                animation: dragStartBounce 0.3s ease-out;
            }

            .notification-icon.drag-end {
                animation: dragEndBounce 0.5s ease-out;
            }

            .notification-icon.dragging .avatar-character {
                animation: dragCharacterWiggle 0.3s ease-in-out infinite;
            }

            .notification-icon.dragging .usaki-character {
                animation: dragUsakiWiggle 0.3s ease-in-out infinite;
            }

            .notification-icon.dragging .character-accessories .sparkle {
                animation: dragSparkleSpin 0.5s linear infinite;
            }

            .notification-icon.dragging .character-wings {
                animation: dragWingFlap 0.2s ease-in-out infinite;
            }

            .notification-icon.dragging .character-heart {
                animation: dragHeartPulse 0.4s ease-in-out infinite;
            }

            .notification-icon.dragging .usaki-ear {
                animation: dragEarWiggle 0.3s ease-in-out infinite;
            }

            .notification-icon.dragging .usaki-tail {
                animation: dragTailWag 0.2s ease-in-out infinite;
            }

            /* 拖动时的粒子效果 */
            .notification-icon.dragging::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 60px;
                height: 60px;
                background: radial-gradient(circle, rgba(255, 215, 0, 0.3) 0%, transparent 70%);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                animation: dragParticleGlow 0.5s ease-in-out infinite;
                z-index: -1;
            }

            .notification-icon.dragging::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 80px;
                height: 80px;
                background: radial-gradient(circle, rgba(255, 107, 157, 0.2) 0%, transparent 70%);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                animation: dragParticleGlow 0.7s ease-in-out infinite reverse;
                z-index: -2;
            }

            /* 拖动时的拖尾效果 */
            .notification-icon.dragging .character-head::before {
                content: '';
                position: absolute;
                top: 50%;
                left: -10px;
                width: 8px;
                height: 8px;
                background: rgba(255, 215, 0, 0.6);
                border-radius: 50%;
                animation: dragTrail 0.3s ease-in-out infinite;
            }

            .notification-icon.dragging .character-head::after {
                content: '';
                position: absolute;
                top: 50%;
                left: -15px;
                width: 6px;
                height: 6px;
                background: rgba(255, 107, 157, 0.4);
                border-radius: 50%;
                animation: dragTrail 0.4s ease-in-out infinite;
            }

            .notification-icon:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
            }


            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }

            .notification-dropdown {
                position: absolute;
                top: 60px;
                right: 0;
                width: 350px;
                max-height: 400px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                border: 1px solid #e9ecef;
                overflow: hidden;
            }

            .notification-header {
                background: #f8f9fa;
                padding: 15px;
                border-bottom: 1px solid #e9ecef;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .notification-header h3 {
                margin: 0;
                font-size: 16px;
                color: #333;
            }

            .clear-all-btn {
                background: #6c757d;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                cursor: pointer;
                transition: background-color 0.2s;
            }

            .clear-all-btn:hover {
                background: #5a6268;
            }

            .drag-hint {
                background: #e9ecef;
                padding: 8px 15px;
                border-bottom: 1px solid #dee2e6;
                text-align: center;
            }

            .drag-hint small {
                color: #6c757d;
                font-size: 11px;
            }

            .notification-list {
                max-height: 300px;
                overflow-y: auto;
            }

            .notification-item {
                padding: 12px 15px;
                border-bottom: 1px solid #f1f3f4;
                cursor: pointer;
                transition: background-color 0.2s;
            }

            .notification-item:hover {
                background: #f8f9fa;
            }

            .notification-item:last-child {
                border-bottom: none;
            }

            .notification-content {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
            }

            .notification-info {
                flex: 1;
            }

            .notification-sender {
                font-weight: bold;
                color: #007bff;
                font-size: 14px;
                margin-bottom: 4px;
            }

            .notification-message {
                color: #666;
                font-size: 13px;
                line-height: 1.4;
                margin-bottom: 4px;
            }

            .notification-time {
                color: #999;
                font-size: 11px;
            }

            .notification-room {
                color: #28a745;
                font-size: 12px;
                font-weight: 500;
            }

            .no-notifications {
                padding: 30px;
                text-align: center;
                color: #999;
                font-size: 14px;
            }

            .notification-count {
                background: #007bff;
                color: white;
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 11px;
                min-width: 16px;
                text-align: center;
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(notificationArea);
    }

    bindEvents() {
        const icon = document.getElementById('notification-icon');
        const dropdown = document.getElementById('notification-dropdown');
        const clearAllBtn = document.getElementById('clear-all-notifications');
        const manager = document.getElementById('chat-notification-manager');

        // 加载保存的位置
        this.loadPosition();

        // 简化的拖拽事件处理
        let startX, startY, hasMoved = false;
        
        icon.addEventListener('mousedown', (e) => {
            this.isDragging = true;
            hasMoved = false;
            startX = e.clientX - this.xOffset;
            startY = e.clientY - this.yOffset;
            
            icon.style.cursor = 'grabbing';
            manager.classList.add('dragging');
            icon.classList.add('drag-start');
            
            // 移除开始动画类
            setTimeout(() => {
                icon.classList.remove('drag-start');
            }, 300);
            
            e.preventDefault();
            e.stopPropagation();
        });

        document.addEventListener('mousemove', (e) => {
            if (!this.isDragging) return;

            hasMoved = true;
            e.preventDefault();
            
            this.currentX = e.clientX - startX;
            this.currentY = e.clientY - startY;
            
            this.xOffset = this.currentX;
            this.yOffset = this.currentY;
            
            this.setTranslate(this.currentX, this.currentY);
        });

        document.addEventListener('mouseup', () => {
            if (this.isDragging) {
                this.isDragging = false;
                icon.style.cursor = 'move';
                manager.classList.remove('dragging');
                icon.classList.add('drag-end');
                
                // 移除结束动画类
                setTimeout(() => {
                    icon.classList.remove('drag-end');
                }, 500);
                
                this.savePosition();
                
                // 如果有移动，延迟一点时间再允许点击
                if (hasMoved) {
                    setTimeout(() => {
                        // 重置移动标志
                        hasMoved = false;
                    }, 100);
                }
            }
        });

        // 点击图标切换显示/隐藏（只有在没有拖拽时才触发）
        icon.addEventListener('click', (e) => {
            e.stopPropagation();
            if (!this.isDragging && !hasMoved) {
                this.toggleDropdown();
            }
        });

        // 双击重置位置
        icon.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            this.resetPosition();
        });

        // 点击其他地方关闭下拉框
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.chat-notification-manager')) {
                this.hideDropdown();
            }
        });

        // 清除所有通知
        clearAllBtn.addEventListener('click', () => {
            this.clearAllNotifications();
        });
    }

    setTranslate(xPos, yPos) {
        const manager = document.getElementById('chat-notification-manager');
        manager.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
    }

    savePosition() {
        localStorage.setItem('chatNotificationPosition', JSON.stringify({
            x: this.currentX,
            y: this.currentY
        }));
    }

    loadPosition() {
        const savedPosition = localStorage.getItem('chatNotificationPosition');
        if (savedPosition) {
            const position = JSON.parse(savedPosition);
            this.currentX = position.x;
            this.currentY = position.y;
            this.xOffset = this.currentX;
            this.yOffset = this.currentY;
            this.setTranslate(this.currentX, this.currentY);
        }
    }

    resetPosition() {
        this.currentX = 0;
        this.currentY = 0;
        this.xOffset = 0;
        this.yOffset = 0;
        this.setTranslate(0, 0);
        localStorage.removeItem('chatNotificationPosition');
        
        // 显示提示
        const icon = document.getElementById('notification-icon');
        icon.style.transform = 'scale(1.2)';
        setTimeout(() => {
            icon.style.transform = '';
        }, 200);
    }

    startPolling() {
        // 立即获取一次
        this.fetchNotifications();
        
        // 每5秒轮询一次
        this.pollInterval = setInterval(() => {
            this.fetchNotifications();
        }, 5000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async fetchNotifications() {
        try {
            const response = await fetch('/tools/api/notifications/summary/', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    if (data.success) {
                        this.updateNotificationCount(data.total_unread);
                        
                        // 如果下拉框是打开的，获取详细通知
                        if (this.isVisible) {
                            this.fetchDetailedNotifications();
                        }
                    }
                } else {
                    // 通知API返回了非JSON响应，可能用户未登录
                    console.log('通知API返回非JSON响应，用户可能未登录');
                }
            } else if (response.status === 401) {
                // 用户未登录，隐藏通知管理器
                console.log('用户未登录，隐藏通知管理器');
                this.destroy();
            } else if (response.status === 403) {
                // 通知API访问被拒绝
                console.log('通知API访问被拒绝');
            }
        } catch (error) {
            // 获取通知摘要失败
            console.log('获取通知摘要失败:', error);
        }
    }

    async fetchDetailedNotifications() {
        try {
            const response = await fetch('/tools/api/notifications/unread/', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    if (data.success) {
                        this.notifications = data.notifications;
                        this.updateNotificationList();
                    }
                } else {
                    // 详细通知API返回了非JSON响应，可能用户未登录
                    console.log('详细通知API返回非JSON响应，用户可能未登录');
                }
            } else if (response.status === 401) {
                // 用户未登录，隐藏通知管理器
                console.log('用户未登录，隐藏通知管理器');
                this.destroy();
            } else if (response.status === 403) {
                // 详细通知API访问被拒绝
                console.log('详细通知API访问被拒绝');
            }
        } catch (error) {
            // 获取详细通知失败
            console.log('获取详细通知失败:', error);
        }
    }

    updateNotificationCount(count) {
        const previousCount = this.unreadCount;
        this.unreadCount = count;
        const messageElement = document.getElementById('notification-message');
        const robot = document.getElementById('usaki-character') || document.getElementById('avatar-character');
        const toast = document.getElementById('message-toast');
        const messageCount = document.querySelector('.message-count');
        
        // 更新红标显示
        const unreadBadge = document.getElementById('unread-badge');
        const unreadCount = document.querySelector('.unread-count');
        
        if (count > 0) {
            // 显示红标
            if (unreadBadge && unreadCount) {
                unreadBadge.style.display = 'flex';
                unreadCount.textContent = count > 99 ? '99+' : count;
            }
            
            // 如果有新消息（数量增加），触发机器人跑圈动画、振动和右上角提示
            if (count > previousCount) {
                const icon = document.getElementById('notification-icon');
                
                // 触发机器人跑圈动画
                if (robot) {
                    robot.classList.add('new-message');
                    setTimeout(() => {
                        robot.classList.remove('new-message');
                    }, 3000);
                }
                
                // 触发振动效果
                if (icon) {
                    icon.classList.add('vibrate');
                    setTimeout(() => {
                        icon.classList.remove('vibrate');
                    }, 500);
                }
                
                // 显示右上角消息提示
                const toast = document.getElementById('message-toast');
                if (toast) {
                    toast.classList.add('show');
                    
                    // 3秒后自动隐藏
                    setTimeout(() => {
                        toast.classList.remove('show');
                    }, 3000);
                }
                
                // 播放通知声音（如果浏览器支持）
                this.playNotificationSound();
            }
        } else {
            // 隐藏红标
            if (unreadBadge) {
                unreadBadge.style.display = 'none';
            }
        }
    }

    playNotificationSound() {
        try {
            // 创建简单的通知音效
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.2);
        } catch (error) {
            // 如果音频播放失败，静默处理
            console.log('通知音效播放失败:', error);
        }
    }

    updateNotificationList() {
        const list = document.getElementById('notification-list');
        
        if (this.notifications.length === 0) {
            list.innerHTML = '<div class="no-notifications">暂无未读消息</div>';
            return;
        }

        const html = this.notifications.map(notification => `
            <div class="notification-item" onclick="window.chatNotificationManager && window.chatNotificationManager.openChatRoom('${notification.room_id}', '${notification.message_type || ''}', '${notification.id}')">
                <div class="notification-content">
                    <div class="notification-info">
                        <div class="notification-room">${notification.room_name}</div>
                        <div class="notification-sender">${notification.sender_username}</div>
                        <div class="notification-message">${notification.message_preview}</div>
                        <div class="notification-time">${this.formatTime(notification.created_at)}</div>
                    </div>
                </div>
            </div>
        `).join('');

        list.innerHTML = html;
    }

    toggleDropdown() {
        if (this.isVisible) {
            this.hideDropdown();
        } else {
            this.showDropdown();
        }
    }

    showDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        dropdown.style.display = 'block';
        this.isVisible = true;
        
        // 获取详细通知
        this.fetchDetailedNotifications();
    }

    hideDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        dropdown.style.display = 'none';
        this.isVisible = false;
    }

    async openChatRoom(roomId, messageType = null, notificationId = null) {
        // 标记特定通知为已读
        if (notificationId) {
            await this.markNotificationAsRead(notificationId);
        } else {
            // 如果没有通知ID，则标记整个聊天室为已读（向后兼容）
            await this.markRoomAsRead(roomId);
        }
        
        // 根据消息类型进行不同的跳转
        if (messageType === 'system') {
            // 系统通知 - 检查是否有跳转链接信息
            const notification = this.notifications.find(n => n.room_id === roomId);
            if (notification) {
                // 检查是否有metadata中的跳转信息
                if (notification.metadata && notification.metadata.jump_url) {
                    // 使用metadata中的跳转链接
                    window.location.href = notification.metadata.jump_url;
                    return;
                }
                
                // 从消息内容中提取跳转链接
                const jumpUrlMatch = notification.message_preview.match(/🔗 跳转链接: (https?:\/\/[^\s]+|\/[^\s]+)/);
                if (jumpUrlMatch) {
                    window.location.href = jumpUrlMatch[1];
                    return;
                }
                
                // 检查是否是任务完成通知
                if (notification.message_preview.includes('任务完成') || 
                    notification.message_preview.includes('后台任务已完成') ||
                    notification.message_preview.includes('测试用例生成')) {
                    // 跳转到任务管理器页面
                    window.location.href = '/tools/task_manager/';
                    return;
                }
                
                // 检查是否是任务结束通知
                if (notification.message_preview.includes('任务结束')) {
                    // 跳转到任务管理器页面
                    window.location.href = '/tools/task_manager/';
                    return;
                }
            }
        }
        
        // 检查是否是ShipBao商品咨询通知
        const notification = this.notifications.find(n => n.room_id === roomId);
        if (notification && (notification.room_name.includes('商品') || notification.message_preview.includes('商品'))) {
            // ShipBao商品咨询 - 跳转到对应的聊天室
            window.location.href = `/tools/heart_link/chat/${roomId}/`;
            return;
        }
        
        // 默认跳转到聊天室
        window.location.href = `/tools/heart_link/chat/${roomId}/`;
    }

    async markNotificationAsRead(notificationId) {
        try {
            const response = await fetch('/tools/api/notifications/mark-read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                credentials: 'same-origin',
                body: JSON.stringify({ notification_ids: [notificationId] })
            });

            if (response.ok) {
                // 刷新通知
                this.fetchNotifications();
            }
        } catch (error) {
            // 标记已读失败
            console.error('标记通知已读失败:', error);
        }
    }

    async markRoomAsRead(roomId) {
        try {
            const response = await fetch('/tools/api/notifications/mark-read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                credentials: 'same-origin',
                body: JSON.stringify({ room_id: roomId })
            });

            if (response.ok) {
                // 刷新通知
                this.fetchNotifications();
            }
        } catch (error) {
            // 标记已读失败
            console.error('标记聊天室已读失败:', error);
        }
    }

    async clearAllNotifications() {
        try {
            const response = await fetch('/tools/api/notifications/clear-all/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                this.updateNotificationCount(0);
                this.notifications = [];
                this.updateNotificationList();
                this.hideDropdown();
            }
        } catch (error) {
            // 清除通知失败
        }
    }

    formatTime(timeString) {
        const date = new Date(timeString);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return '刚刚';
        if (minutes < 60) return `${minutes}分钟前`;
        if (hours < 24) return `${hours}小时前`;
        if (days < 7) return `${days}天前`;
        
        return date.toLocaleDateString();
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // 测试头像检测
    testAvatarDetection() {
        console.log('=== 头像检测测试 ===');
        const avatarSelectors = [
            '.top-ui-avatar img',
            '.user-avatar img',
            '.avatar img',
            '.profile-avatar img',
            '.user-profile img',
            '[class*="avatar"] img',
            'img[src*="avatar"]',
            'img[src*="media"]',
            '.top-ui-bar img',
            '.user-info img'
        ];
        
        console.log('页面中所有图片元素:');
        const allImages = document.querySelectorAll('img');
        allImages.forEach((img, index) => {
            console.log(`图片 ${index + 1}:`, {
                src: img.src,
                className: img.className,
                id: img.id,
                parentElement: img.parentElement?.className || img.parentElement?.tagName
            });
        });
        
        console.log('尝试各个选择器:');
        avatarSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            console.log(`选择器 "${selector}": 找到 ${elements.length} 个元素`);
            elements.forEach((el, index) => {
                console.log(`  元素 ${index + 1}:`, {
                    src: el.src,
                    className: el.className,
                    id: el.id
                });
            });
        });
        
        const detectedAvatar = this.getUserAvatar();
        console.log('最终检测结果:', detectedAvatar);
        return detectedAvatar;
    }

    // 测试机器人动画效果
    testRobotAnimation() {
        const robot = document.getElementById('usaki-character') || document.getElementById('avatar-character');
        const icon = document.getElementById('notification-icon');
        const toast = document.getElementById('message-toast');
        const unreadBadge = document.getElementById('unread-badge');
        const unreadCount = document.querySelector('.unread-count');
        
        if (robot && icon) {
            // 显示红标
            if (unreadBadge && unreadCount) {
                unreadBadge.style.display = 'flex';
                unreadCount.textContent = '5';
            }
            
            // 触发机器人跑圈动画
            robot.classList.add('new-message');
            setTimeout(() => {
                robot.classList.remove('new-message');
            }, 3000);
            
            // 触发振动效果
            icon.classList.add('vibrate');
            setTimeout(() => {
                icon.classList.remove('vibrate');
            }, 500);
            
            // 显示右上角消息提示
            if (toast) {
                toast.classList.add('show');
                setTimeout(() => {
                    toast.classList.remove('show');
                }, 3000);
            }
            
            this.playNotificationSound();
        }
    }

    destroy() {
        this.stopPolling();
        const element = document.getElementById('chat-notification-manager');
        if (element) {
            element.remove();
        }
    }
}

// 全局实例
let chatNotificationManager = null;

// 全局测试函数
window.testAndroidRobot = function() {
    if (window.chatNotificationManager) {
        window.chatNotificationManager.testRobotAnimation();
    } else {
        console.log('通知管理器未初始化');
    }
};

// 测试头像检测
window.testAvatarDetection = function() {
    if (window.chatNotificationManager) {
        return window.chatNotificationManager.testAvatarDetection();
    } else {
        console.log('ChatNotificationManager 未初始化');
        return null;
    }
};

// 重新创建通知UI（用于测试）
window.recreateNotificationUI = function() {
    if (window.chatNotificationManager) {
        window.chatNotificationManager.createNotificationUI();
        console.log('通知UI已重新创建');
    } else {
        console.log('ChatNotificationManager 未初始化');
    }
};

// 初始化通知管理器
document.addEventListener('DOMContentLoaded', function() {
    // 只在登录用户才启用通知
    if (document.querySelector('[name=csrfmiddlewaretoken]')) {
        // 检查是否已经初始化，避免重复初始化
        if (!window.chatNotificationManager) {
            chatNotificationManager = new ChatNotificationManager();
            // 同时设置为全局变量
            window.chatNotificationManager = chatNotificationManager;
        }
    }
});

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (chatNotificationManager) {
        chatNotificationManager.destroy();
    }
});
