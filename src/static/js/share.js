// Share.js - 分享功能JavaScript文件
// 这个文件用于处理分享相关的功能

console.log('Share.js loaded');

// 分享功能
function shareContent(url, title, description) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: description,
            url: url
        }).then(() => {
            console.log('分享成功');
        }).catch((error) => {
            console.log('分享失败:', error);
        });
    } else {
        // 降级处理：复制链接到剪贴板
        copyToClipboard(url);
    }
}

// 复制到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            console.log('链接已复制到剪贴板');
        }).catch((error) => {
            console.log('复制失败:', error);
        });
    } else {
        // 降级处理
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        console.log('链接已复制到剪贴板');
    }
}

// 导出函数供其他模块使用
window.shareContent = shareContent;
window.copyToClipboard = copyToClipboard;
