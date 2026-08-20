"""
图标模块 - 使用 qtawesome 专业图标库
"""

import qtawesome as qta
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QWidget


def get_icon(name: str, color: str = "#262626", size: int = 24) -> QIcon:
    return qta.icon(name, color=color)


def get_pixmap(name: str, color: str = "#262626", size: int = 24) -> QPixmap:
    icon = qta.icon(name, color=color)
    return icon.pixmap(size, size)


class PDFIconWidget(QWidget):
    """PDF文件图标 - 使用 qtawesome 现成图标"""

    def __init__(self, size: int = 36, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._icon = qta.icon("fa6s.file-pdf", color="#ff4d4f")
        self.setStyleSheet("background:transparent;")

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 居中绘制图标
        icon_size = min(self.width(), self.height()) - 4
        x = (self.width() - icon_size) // 2
        y = (self.height() - icon_size) // 2
        self._icon.paint(p, x, y, icon_size, icon_size)
        p.end()
