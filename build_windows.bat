@echo off
REM Windows 打包脚本
REM 使用方法：双击运行 build_windows.bat

echo 正在安装依赖...
pip install -r requirements.txt

echo 正在打包 Windows 版本...
pyinstaller --onefile --windowed ^
    --name "No PDF Password" ^
    --add-data "config.json;." ^
    --add-data "src;src" ^
    main.py

echo 打包完成！
echo 可执行文件位于：dist\No PDF Password.exe
pause
