"""
图标模块 - 使用 qtawesome 专业图标库
"""

import qtawesome as qta
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt


def get_icon(name: str, color: str = "#262626", size: int = 24) -> QIcon:
    return qta.icon(name, color=color)


def get_pixmap(name: str, color: str = "#262626", size: int = 24) -> QPixmap:
    icon = qta.icon(name, color=color)
    return icon.pixmap(size, size)


class PDFIconWidget(QLabel):
    """PDF文件图标 - 直接用 QLabel 显示"""

    def __init__(self, size: int = 36, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setStyleSheet("background:transparent;")
        # 用 qtawesome 生成红色PDF图标
        icon = qta.icon("fa6s.file-pdf", color="#ff4d4f")
        self.setPixmap(icon.pixmap(size, size))
