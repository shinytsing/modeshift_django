// Chat Enhanced.js - 增强聊天功能JavaScript文件
// 这个文件用于处理增强聊天相关的功能

// Chat Enhanced.js loaded

// 聊天增强功能
class ChatEnhanced {
    constructor() {
        this.roomId = window.roomId;
        this.isConnected = false;
        this.messageQueue = [];
        this.init();
    }

    init() {
        // 初始化增强聊天功能
        this.setupEventListeners();
        this.connectWebSocket();
    }

    setupEventListeners() {
        // 设置消息发送事件监听器
        const sendButton = document.getElementById('send-button');
        const messageInput = document.getElementById('message-input');
        
        if (sendButton && messageInput) {
            sendButton.addEventListener('click', () => this.sendMessage());
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }
    }

    connectWebSocket() {
        if (!this.roomId) {
            // 房间ID未设置
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.roomId}/`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                // WebSocket连接已建立
                this.isConnected = true;
                this.processMessageQueue();
            };
            
            this.websocket.onmessage = (event) => {
                this.handleMessage(event.data);
            };
            
            this.websocket.onclose = () => {
                // WebSocket连接已关闭
                this.isConnected = false;
                // 尝试重连
                setTimeout(() => this.connectWebSocket(), 3000);
            };
            
            this.websocket.onerror = (error) => {
                // WebSocket错误
            };
            
        } catch (error) {
            // WebSocket连接失败
        }
    }

    sendMessage() {
        const messageInput = document.getElementById('message-input');
        if (!messageInput) return;
        
        const content = messageInput.value.trim();
        if (!content) return;
        
        const message = {
            type: 'chat_message',
            content: content,
            room_id: this.roomId
        };
        
        if (this.isConnected) {
            this.websocket.send(JSON.stringify(message));
        } else {
            this.messageQueue.push(message);
        }
        
        messageInput.value = '';
    }

    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            // 收到消息
            // 这里可以添加消息处理逻辑
        } catch (error) {
            // 消息解析错误
        }
    }

    processMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.websocket.send(JSON.stringify(message));
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    if (window.roomId) {
        window.chatEnhanced = new ChatEnhanced();
    }
});

// 导出类供其他模块使用
window.ChatEnhanced = ChatEnhanced;
