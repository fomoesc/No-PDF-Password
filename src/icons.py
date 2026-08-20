"""
图标模块 - 使用 qtawesome 专业图标库
"""

import qtawesome as qta
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen, QBrush
from PySide6.QtCore import Qt, QRect, QRectF, QPointF, QSize
from PySide6.QtWidgets import QWidget


def get_icon(name: str, color: str = "#262626", size: int = 24) -> QIcon:
    return qta.icon(name, color=color)


def get_pixmap(name: str, color: str = "#262626", size: int = 24) -> QPixmap:
    icon = qta.icon(name, color=color)
    return icon.pixmap(size, size)


class PDFIconWidget(QWidget):
    """PDF文件图标 - 白色纸张+红色折角+PDF文字"""

    def __init__(self, size: int = 36, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, int(size * 1.15))
        self.setStyleSheet("background:transparent;")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        # 白色纸张主体
        p.setPen(QPen(QColor("#e8e8e8"), 1))
        p.setBrush(QColor("#ffffff"))
        p.drawRoundedRect(1, 1, w - 2, h - 2, 3, 3)

        # 红色顶部横条
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#ff4d4f"))
        p.drawRoundedRect(1, 1, w - 2, int(h * 0.28), 3, 3)
        # 修复底部圆角被覆盖
        p.drawRect(1, int(h * 0.2) - 1, w - 2, int(h * 0.1))

        # 折角
        fold = int(w * 0.2)
        fold_path = QPainterPath()
        fold_path.moveTo(w - fold - 1, 1)
        fold_path.lineTo(w - 1 - 1, fold + 1)
        fold_path.lineTo(w - 1 - 1, 1)
        fold_path.closeSubpath()
        p.setBrush(QColor("#f0f0f0"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(fold_path)

        # PDF 文字
        font = QFont("Arial", max(6, int(w * 0.2)), QFont.Bold)
        p.setFont(font)
        p.setPen(QColor("#ffffff"))
        text_y = int(h * 0.02)
        text_h = int(h * 0.28)
        p.drawText(QRect(0, text_y, w, text_h),
                    Qt.AlignmentFlag.AlignCenter, "PDF")

        p.end()
