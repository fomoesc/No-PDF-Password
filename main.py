"""
No PDF Password - PDF批量解锁工具
主入口文件
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QIcon
from src.ui_main import MainWindow


def get_resource_path(relative_path):
    """获取资源文件路径，兼容PyInstaller打包"""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("No PDF Password")
    app.setOrganizationName("星图传媒")

    # 设置应用图标
    icon_path = get_resource_path("icon.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = MainWindow()
    window.setWindowIcon(app.windowIcon())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
