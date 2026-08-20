"""
No PDF Password - PDF批量解锁工具
主入口文件
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from src.ui_main import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("No PDF Password")
    app.setOrganizationName("星图传媒")
    
    # 设置应用样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QTabWidget::pane {
            border: 1px solid #d0d0d0;
            background-color: white;
        }
        QTabBar::tab {
            padding: 8px 20px;
            font-size: 13px;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #2563eb;
        }
        QPushButton {
            padding: 6px 16px;
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            background-color: white;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #f0f0f0;
        }
        QPushButton:pressed {
            background-color: #e0e0e0;
        }
        QLineEdit {
            padding: 6px;
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            font-size: 13px;
        }
        QListWidget {
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            background-color: white;
            font-size: 13px;
        }
        QProgressBar {
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            text-align: center;
            font-size: 12px;
        }
        QProgressBar::chunk {
            background-color: #2563eb;
            border-radius: 3px;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
