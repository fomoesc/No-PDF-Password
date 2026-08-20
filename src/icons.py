"""
图标模块 - 使用 qtawesome 专业图标库
"""

import qtawesome as qta
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen, QBrush
from PySide6.QtCore import Qt, QRect, QRectF, QPointF, QSize
from PySide6.QtWidgets import QWidget
import qtawesome as qta


def get_icon(name: str, color: str = "#262626", size: int = 24) -> QIcon:
    """获取qtawesome图标"""
    return qta.icon(name, color=color)


def get_pixmap(name: str, color: str = "#262626", size: int = 24) -> QPixmap:
    """获取qtawesome图标为QPixmap"""
    icon = qta.icon(name, color=color)
    return icon.pixmap(size, size)


# ============================================================
# PDF文件图标（自定义绘制 - 红色折角纸张 + PDF文字）
# ============================================================
class PDFIconWidget(QWidget):
    """PDF文件图标Widget"""

    def __init__(self, size: int = 36, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, int(size * 1.2))
        self.setStyleSheet("background:transparent;")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        # 纸张主体（浅红色背景）
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#fff1f0"))
        p.drawRoundedRect(0, 0, w, h, 4, 4)

        # 折角
        fold = int(w * 0.22)
        fold_path = QPainterPath()
        fold_path.moveTo(w - fold, 0)
        fold_path.lineTo(w - fold, fold)
        fold_path.lineTo(w, fold)
        fold_path.closeSubpath()
        p.setBrush(QColor("#ffccc7"))
        p.drawPath(fold_path)

        # 边框
        p.setPen(QPen(QColor("#ffa39e"), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(0, 0, w, h, 4, 4)

        # PDF 文字
        font = QFont("Arial", max(7, int(w * 0.22)), QFont.Bold)
        p.setFont(font)
        p.setPen(QColor("#ff4d4f"))
        p.drawText(QRect(0, int(h * 0.35), w, int(h * 0.4)),
                    Qt.AlignmentFlag.AlignCenter, "PDF")

        p.end()
