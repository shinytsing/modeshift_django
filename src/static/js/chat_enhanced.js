// Chat Enhanced.js - 增强聊天功能JavaScript文件
// 这个文件用于处理增强聊天相关的功能

console.log('Chat Enhanced.js loaded');

// 聊天增强功能
class ChatEnhanced {
    constructor() {
        this.roomId = window.roomId;
        this.isConnected = false;
        this.messageQueue = [];
        this.init();
    }

    init() {
        console.log('初始化增强聊天功能，房间ID:', this.roomId);
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
            console.error('房间ID未设置');
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.roomId}/`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket连接已建立');
                this.isConnected = true;
                this.processMessageQueue();
            };
            
            this.websocket.onmessage = (event) => {
                this.handleMessage(event.data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket连接已关闭');
                this.isConnected = false;
                // 尝试重连
                setTimeout(() => this.connectWebSocket(), 3000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket错误:', error);
            };
            
        } catch (error) {
            console.error('WebSocket连接失败:', error);
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
            console.log('收到消息:', message);
            // 这里可以添加消息处理逻辑
        } catch (error) {
            console.error('消息解析错误:', error);
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
