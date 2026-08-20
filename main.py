"""
No PDF Password - PDF批量解锁工具
主入口文件
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from src.ui_main import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("No PDF Password")
    app.setOrganizationName("星图传媒")

    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
