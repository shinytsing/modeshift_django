#!/bin/bash

# Mac应用打包脚本
# 将Python GUI应用打包成Mac .app文件，方便分发给朋友使用

set -e

echo "=== ClashX Pro 代理管理器 Mac应用打包脚本 ==="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 应用信息
APP_NAME="ClashX代理管理器"
APP_BUNDLE_ID="com.modeshift.clashx-proxy-manager"
APP_VERSION="1.0.0"
APP_ICON="proxy_icon.icns"

# 创建应用包目录结构
APP_DIR="${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

echo "创建应用包目录结构..."
rm -rf "$APP_DIR"
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# 创建Info.plist文件
echo "创建Info.plist..."
cat > "${CONTENTS_DIR}/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>ClashXProxyManager</string>
    <key>CFBundleIdentifier</key>
    <string>${APP_BUNDLE_ID}</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleVersion</key>
    <string>${APP_VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>${APP_VERSION}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
</dict>
</plist>
EOF

# 创建启动脚本
echo "创建启动脚本..."
cat > "${MACOS_DIR}/ClashXProxyManager" << 'EOF'
#!/bin/bash

# ClashX Pro 代理管理器启动脚本
# 检查Python环境并启动应用

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
RESOURCES_DIR="${APP_DIR}/Resources"

# 切换到应用目录
cd "$RESOURCES_DIR"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "Python3 未安装，请先安装Python3\n\n您可以从 https://www.python.org 下载安装" with title "错误" buttons {"确定"} default button "确定"'
    exit 1
fi

# 检查tkinter是否可用
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    osascript -e 'display dialog "tkinter 未安装，请先安装tkinter\n\n在终端中运行: brew install python-tk" with title "错误" buttons {"确定"} default button "确定"'
    exit 1
fi

# 启动应用
python3 ClashXProxyManager.py
EOF

# 设置启动脚本执行权限
chmod +x "${MACOS_DIR}/ClashXProxyManager"

# 复制Python文件到Resources目录
echo "复制应用文件..."
cp ClashXProxyManager.py "$RESOURCES_DIR/"
cp clash_config_example.yaml "$RESOURCES_DIR/"

# 创建应用图标（如果不存在）
if [ ! -f "$APP_ICON" ]; then
    echo "创建应用图标..."
    # 创建一个简单的应用图标
    python3 -c "
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import os

# 创建64x64的图标
size = 64
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 绘制代理图标
draw.rectangle([8, 8, 56, 56], fill='#007AFF', outline='#0056CC', width=2)
draw.rectangle([16, 16, 48, 48], fill='#FFFFFF', outline='#CCCCCC', width=1)
draw.text((20, 20), 'P', fill='#007AFF', font_size=20)
draw.text((32, 20), 'R', fill='#007AFF', font_size=20)
draw.text((20, 36), 'O', fill='#007AFF', font_size=20)
draw.text((32, 36), 'X', fill='#007AFF', font_size=20)

# 保存为PNG
img.save('proxy_icon.png')
print('图标创建完成')
" 2>/dev/null || echo "无法创建图标，将使用默认图标"

    # 如果有PNG图标，转换为ICNS
    if [ -f "proxy_icon.png" ]; then
        # 创建iconset目录
        mkdir -p proxy_icon.iconset
        
        # 生成不同尺寸的图标
        sips -z 16 16 proxy_icon.png --out proxy_icon.iconset/icon_16x16.png
        sips -z 32 32 proxy_icon.png --out proxy_icon.iconset/icon_16x16@2x.png
        sips -z 32 32 proxy_icon.png --out proxy_icon.iconset/icon_32x32.png
        sips -z 64 64 proxy_icon.png --out proxy_icon.iconset/icon_32x32@2x.png
        sips -z 128 128 proxy_icon.png --out proxy_icon.iconset/icon_128x128.png
        sips -z 256 256 proxy_icon.png --out proxy_icon.iconset/icon_128x128@2x.png
        sips -z 256 256 proxy_icon.png --out proxy_icon.iconset/icon_256x256.png
        sips -z 512 512 proxy_icon.png --out proxy_icon.iconset/icon_256x256@2x.png
        sips -z 512 512 proxy_icon.png --out proxy_icon.iconset/icon_512x512.png
        sips -z 1024 1024 proxy_icon.png --out proxy_icon.iconset/icon_512x512@2x.png
        
        # 转换为ICNS
        iconutil -c icns proxy_icon.iconset -o proxy_icon.icns
        
        # 清理临时文件
        rm -rf proxy_icon.iconset proxy_icon.png
    fi
fi

# 复制图标到应用包
if [ -f "$APP_ICON" ]; then
    cp "$APP_ICON" "$RESOURCES_DIR/"
fi

# 创建使用说明文件
echo "创建使用说明..."
cat > "${RESOURCES_DIR}/使用说明.txt" << 'EOF'
ClashX Pro 代理管理器 使用说明
=====================================

这是一个用于管理ClashX Pro代理的Mac应用程序。

功能特点：
- 一键开启/关闭系统代理
- 实时监控代理状态
- 配置文件管理（导入/导出/重置）
- 连接测试和IP检测
- 操作日志记录

使用步骤：
1. 确保已安装ClashX Pro
2. 双击应用图标启动
3. 在"配置管理"选项卡中导入您的ClashX配置文件
4. 在"状态监控"选项卡中点击"开启代理"或"关闭代理"

注意事项：
- 首次使用需要管理员权限来修改系统代理设置
- 配置文件格式为YAML，请确保格式正确
- 如果遇到问题，请查看"操作日志"选项卡

技术支持：
如有问题，请联系开发者。
EOF

# 创建安装脚本
echo "创建安装脚本..."
cat > "install_clashx_manager.sh" << 'EOF'
#!/bin/bash

# ClashX Pro 代理管理器安装脚本

echo "=== ClashX Pro 代理管理器安装脚本 ==="

# 检查是否已安装ClashX Pro
if [ ! -d "/Applications/ClashX Pro.app" ]; then
    echo "❌ 未检测到ClashX Pro，请先安装ClashX Pro"
    echo "下载地址: https://github.com/yichengchen/clashX"
    exit 1
fi

echo "✅ 检测到ClashX Pro已安装"

# 复制应用到Applications目录
APP_NAME="ClashX代理管理器"
if [ -d "${APP_NAME}.app" ]; then
    echo "正在安装到Applications目录..."
    sudo cp -R "${APP_NAME}.app" "/Applications/"
    echo "✅ 安装完成！"
    echo "您可以在Applications文件夹中找到'ClashX代理管理器'应用"
else
    echo "❌ 未找到应用包，请先运行打包脚本"
    exit 1
fi
EOF

chmod +x install_clashx_manager.sh

# 创建分发包
echo "创建分发包..."
DIST_PACKAGE="ClashX代理管理器_分发包.zip"
rm -f "$DIST_PACKAGE"

# 创建临时分发目录
DIST_DIR="ClashX代理管理器_分发包"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# 复制文件到分发目录
cp -R "${APP_NAME}.app" "$DIST_DIR/"
cp install_clashx_manager.sh "$DIST_DIR/"
cp clash_config_example.yaml "$DIST_DIR/"
cp "${RESOURCES_DIR}/使用说明.txt" "$DIST_DIR/"

# 创建分发说明
cat > "${DIST_DIR}/分发说明.md" << 'EOF'
# ClashX Pro 代理管理器 分发包

## 包含文件
- `ClashX代理管理器.app` - 主应用程序
- `install_clashx_manager.sh` - 安装脚本
- `clash_config_example.yaml` - 示例配置文件
- `使用说明.txt` - 使用说明
- `分发说明.md` - 本文件

## 安装步骤
1. 解压此分发包
2. 运行 `install_clashx_manager.sh` 安装应用
3. 双击 `ClashX代理管理器.app` 启动应用

## 系统要求
- macOS 10.13 或更高版本
- Python 3.6 或更高版本
- tkinter（通常随Python一起安装）
- ClashX Pro

## 注意事项
- 首次使用需要管理员权限
- 请确保ClashX Pro已正确安装和配置
- 配置文件需要根据您的实际服务器信息进行修改

## 技术支持
如有问题，请联系开发者。
EOF

# 压缩分发包
echo "压缩分发包..."
zip -r "$DIST_PACKAGE" "$DIST_DIR"

# 清理临时文件
rm -rf "$DIST_DIR"

echo ""
echo "=== 打包完成 ==="
echo "✅ 应用包: ${APP_NAME}.app"
echo "✅ 分发包: ${DIST_PACKAGE}"
echo "✅ 安装脚本: install_clashx_manager.sh"
echo ""
echo "使用方法："
echo "1. 将 ${DIST_PACKAGE} 发送给朋友"
echo "2. 朋友解压后运行 install_clashx_manager.sh"
echo "3. 双击应用图标即可使用"
echo ""
echo "注意事项："
echo "- 确保朋友已安装ClashX Pro"
echo "- 需要Python 3.6+和tkinter"
echo "- 首次使用需要管理员权限"
