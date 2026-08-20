"""
自定义图标绘制模块
使用 QPainter 绘制专业矢量图标，替代廉价的 Emoji
"""

from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QBrush, QFont
from PySide6.QtCore import Qt, QRect, QRectF, QPointF
from PySide6.QtWidgets import QWidget
import math


def _draw_lock_icon(painter: QPainter, x: int, y: int, size: int,
                    bg_color: str = "#1677ff", icon_color: str = "white"):
    """绘制锁图标（圆形背景 + 白色锁）"""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 圆形背景
    painter.setBrush(QColor(bg_color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(x, y, size, size)

    # 锁体
    cx = x + size / 2
    cy = y + size / 2
    s = size / 24  # 基准单位

    # 锁梁（半圆弧）
    painter.setPen(QPen(QColor(icon_color), max(1, int(s * 1.8)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    arc_rect = QRectF(cx - s * 3.5, cy - s * 5, s * 7, s * 7)
    painter.drawArc(arc_rect, 0, 180 * 16)

    # 锁体（圆角矩形）
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(icon_color))
    body_rect = QRectF(cx - s * 4, cy - s * 0.5, s * 8, s * 7)
    painter.drawRoundedRect(body_rect, s * 1.5, s * 1.5)

    # 钥匙孔
    painter.setBrush(QColor(bg_color))
    painter.drawEllipse(QPointF(cx, cy + s * 1.2), s * 1.2, s * 1.2)
    painter.drawRect(QRectF(cx - s * 0.6, cy + s * 1.2, s * 1.2, s * 2.5))

    painter.restore()


def _draw_folder_icon(painter: QPainter, x: int, y: int, size: int,
                      color: str = "#faad14"):
    """绘制文件夹图标"""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    s = size / 24
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color))
    painter.drawRoundedRect(QRectF(x + s * 1, y + s * 5, s * 22, s * 17), s * 2, s * 2)

    # 文件夹标签
    painter.setBrush(QColor("#f5c034"))
    path = QPainterPath()
    path.moveTo(x + s * 1, y + s * 5)
    path.lineTo(x + s * 1, y + s * 3)
    path.quadTo(x + s * 1, y + s * 1, x + s * 3, y + s * 1)
    path.lineTo(x + s * 10, y + s * 1)
    path.lineTo(x + s * 12, y + s * 5)
    path.closeSubpath()
    painter.drawPath(path)

    painter.restore()


def _draw_grid_icon(painter: QPainter, x: int, y: int, size: int,
                    color: str = "#1677ff"):
    """绘制网格图标（解密导航用）"""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    s = size / 24
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color))

    # 四个圆角矩形
    gap = s * 2
    w = (s * 24 - gap * 3) / 2
    h = (s * 24 - gap * 3) / 2

    for row in range(2):
        for col in range(2):
            rx = x + s * 2 + col * (w + gap)
            ry = y + s * 2 + row * (h + gap)
            painter.drawRoundedRect(QRectF(rx, ry, w, h), s * 2, s * 2)

    painter.restore()


def _draw_key_icon(painter: QPainter, x: int, y: int, size: int,
                   color: str = "#8c8c8c"):
    """绘制钥匙图标（密码库导航用）"""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    s = size / 24
    pen = QPen(QColor(color), max(1, int(s * 2)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    cx = x + size / 2
    cy = y + size / 2

    # 钥匙头（圆形）
    head_rect = QRectF(cx - s * 7, cy - s * 7, s * 9, s * 9)
    painter.drawEllipse(head_rect)

    # 钥匙杆
    painter.drawLine(QPointF(cx - s * 2.5, cy + s * 2), QPointF(cx + s * 9, cy + s * 9))

    # 钥匙齿
    painter.drawLine(QPointF(cx + s * 3, cy + s * 5.5), QPointF(cx + s * 3, cy + s * 8.5))
    painter.drawLine(QPointF(cx + s * 5.5, cy + s * 7), QPointF(cx + s * 5.5, cy + s * 10))

    painter.restore()


def _draw_pdf_icon(painter: QPainter, x: int, y: int, size: int):
    """绘制PDF文件图标（红色矩形 + 折角 + PDF文字）"""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    s = size / 32
    w = s * 22
    h = s * 28

    # 折角路径
    fold = s * 6

    # 纸张主体
    path = QPainterPath()
    path.moveTo(x + s * 5, y)
    path.lineTo(x + s * 5 + w - fold, y)
    path.lineTo(x + s * 5 + w, y + fold)
    path.lineTo(x + s * 5 + w, y + h)
    path.lineTo(x + s * 5, y + h)
    path.closeSubpath()

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#fff1f0"))
    painter.drawPath(path)

    # 折角
    fold_path = QPainterPath()
    fold_path.moveTo(x + s * 5 + w - fold, y)
    fold_path.lineTo(x + s * 5 + w - fold, y + fold)
    fold_path.lineTo(x + s * 5 + w, y + fold)
    fold_path.closeSubpath()

    painter.setBrush(QColor("#ffccc7"))
    painter.drawPath(fold_path)

    # 边框
    painter.setPen(QPen(QColor("#ffa39e"), s * 0.5))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path)

    # PDF 文字
    font = QFont("Arial", max(6, int(s * 7)), QFont.Bold)
    painter.setFont(font)
    painter.setPen(QColor("#ff4d4f"))
    text_rect = QRectF(x + s * 5, y + h - s * 12, w, s * 10)
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "PDF")

    painter.restore()


def _draw_check_circle(painter: QPainter, x: int, y: int, size: int,
                       color: str = "#52c41a"):
    """绘制成功图标（绿色圆圈 + 白色勾）"""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 绿色圆
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color))
    painter.drawEllipse(x, y, size, size)

    # 白色勾
    s = size / 24
    pen = QPen(QColor("white"), max(1, int(s * 2.2)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(QPointF(x + s * 7, y + s * 12), QPointF(x + s * 10.5, y + s * 16))
    painter.drawLine(QPointF(x + s * 10.5, y + s * 16), QPointF(x + s * 17, y + s * 8))

    painter.restore()


def _draw_x_circle(painter: QPainter, x: int, y: int, size: int,
                   color: str = "#ff4d4f"):
    """绘制失败图标（红色圆圈 + 白色叉）"""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color))
    painter.drawEllipse(x, y, size, size)

    s = size / 24
    pen = QPen(QColor("white"), max(1, int(s * 2.2)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.drawLine(QPointF(x + s * 8, y + s * 8), QPointF(x + s * 16, y + s * 16))
    painter.drawLine(QPointF(x + s * 16, y + s * 8), QPointF(x + s * 8, y + s * 16))

    painter.restore()


def _draw_small_lock(painter: QPainter, x: int, y: int, size: int,
                     color: str = "#1677ff"):
    """绘制小型锁图标"""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    s = size / 24
    pen = QPen(QColor(color), max(1, int(s * 2)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    cx = x + size / 2
    cy = y + size / 2

    # 锁梁
    arc_rect = QRectF(cx - s * 4, cy - s * 6, s * 8, s * 8)
    painter.drawArc(arc_rect, 0, 180 * 16)

    # 锁体
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color))
    painter.drawRoundedRect(QRectF(cx - s * 5, cy + s * 0.5, s * 10, s * 8), s * 1.5, s * 1.5)

    # 钥匙孔
    painter.setBrush(QColor("white"))
    painter.drawEllipse(QPointF(cx, cy + s * 3), s * 1, s * 1)
    painter.drawRect(QRectF(cx - s * 0.5, cy + s * 3, s * 1, s * 3))

    painter.restore()


def _draw_trash_icon(painter: QPainter, x: int, y: int, size: int,
                     color: str = "#bfbfbf"):
    """绘制垃圾桶图标"""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    s = size / 24
    pen = QPen(QColor(color), max(1, int(s * 1.5)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    cx = x + size / 2

    # 盖子
    painter.drawLine(QPointF(cx - s * 8, y + s * 4), QPointF(cx + s * 8, y + s * 4))
    # 提手
    painter.drawLine(QPointF(cx - s * 4, y + s * 4), QPointF(cx - s * 4, y + s * 2))
    painter.drawLine(QPointF(cx + s * 4, y + s * 4), QPointF(cx + s * 4, y + s * 2))
    # 桶身
    painter.drawLine(QPointF(cx - s * 6, y + s * 6), QPointF(cx - s * 5, y + s * 21))
    painter.drawLine(QPointF(cx + s * 6, y + s * 6), QPointF(cx + s * 5, y + s * 21))
    # 底部
    painter.drawLine(QPointF(cx - s * 5, y + s * 21), QPointF(cx + s * 5, y + s * 21))
    # 垃圾线
    painter.drawLine(QPointF(cx - s * 2, y + s * 9), QPointF(cx - s * 2, y + s * 17))
    painter.drawLine(QPointF(cx, y + s * 9), QPointF(cx, y + s * 17))
    painter.drawLine(QPointF(cx + s * 2, y + s * 9), QPointF(cx + s * 2, y + s * 17))

    painter.restore()


def _draw_shield_icon(painter: QPainter, x: int, y: int, size: int,
                      color: str = "#1677ff"):
    """绘制盾牌图标"""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    s = size / 24
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color))

    path = QPainterPath()
    cx = x + size / 2
    path.moveTo(cx, y + s * 2)
    path.lineTo(x + size - s * 3, y + s * 5)
    path.lineTo(x + size - s * 3, y + s * 12)
    path.quadTo(cx, y + size - s * 2, cx, y + size - s * 2)
    path.quadTo(cx, y + size - s * 2, x + s * 3, y + s * 12)
    path.lineTo(x + s * 3, y + s * 5)
    path.closeSubpath()
    painter.drawPath(path)

    # 对勾
    pen = QPen(QColor("white"), max(1, int(s * 2)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawLine(QPointF(cx - s * 3, y + s * 10), QPointF(cx - s * 0.5, y + s * 14))
    painter.drawLine(QPointF(cx - s * 0.5, y + s * 14), QPointF(cx + s * 4, y + s * 7))

    painter.restore()


class IconWidget(QWidget):
    """通用图标绘制Widget"""

    def __init__(self, icon_type: str, size: int = 24, parent=None):
        super().__init__(parent)
        self.icon_type = icon_type
        self.icon_size = size
        self.setFixedSize(size, size)

    def set_icon(self, icon_type: str):
        self.icon_type = icon_type
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        draw_map = {
            "lock": lambda: _draw_lock_icon(painter, 0, 0, self.icon_size),
            "lock_small": lambda: _draw_small_lock(painter, 0, 0, self.icon_size),
            "folder": lambda: _draw_folder_icon(painter, 0, 0, self.icon_size),
            "grid": lambda: _draw_grid_icon(painter, 0, 0, self.icon_size),
            "key": lambda: _draw_key_icon(painter, 0, 0, self.icon_size),
            "pdf": lambda: _draw_pdf_icon(painter, 0, 0, self.icon_size),
            "check_circle": lambda: _draw_check_circle(painter, 0, 0, self.icon_size),
            "x_circle": lambda: _draw_x_circle(painter, 0, 0, self.icon_size),
            "trash": lambda: _draw_trash_icon(painter, 0, 0, self.icon_size),
            "shield": lambda: _draw_shield_icon(painter, 0, 0, self.icon_size),
        }

        draw_fn = draw_map.get(self.icon_type)
        if draw_fn:
            draw_fn()
