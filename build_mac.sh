#!/bin/bash
# macOS 打包脚本
# 使用方法：chmod +x build_mac.sh && ./build_mac.sh

echo "正在安装依赖..."
pip install -r requirements.txt

echo "正在打包 macOS 版本..."
pyinstaller --onefile --windowed \
    --name "No PDF Password" \
    --add-data "config.json:." \
    --add-data "src:src" \
    main.py

echo "打包完成！"
echo "可执行文件位于：dist/No PDF Password"
