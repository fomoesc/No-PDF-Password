# -*- coding: utf-8 -*-
import qtawesome as qta
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt, QSize
import sys

app = QApplication(sys.argv)

# 创建不同尺寸的图标
sizes = [16, 32, 48, 64, 128, 256]
icons_dir = "icons"
import os
os.makedirs(icons_dir, exist_ok=True)

for size in sizes:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 蓝色圆角背景
    painter.setBrush(QColor("#1677ff"))
    painter.setPen(Qt.PenStyle.NoPen)
    radius = size * 0.2
    painter.drawRoundedRect(0, 0, size, size, radius, radius)
    
    # 白色锁图标
    icon_size = int(size * 0.45)
    lock_icon = qta.icon("fa6s.lock", color="white")
    lock_pixmap = lock_icon.pixmap(icon_size, icon_size)
    x = (size - icon_size) // 2
    y = (size - icon_size) // 2
    painter.drawPixmap(x, y, lock_pixmap)
    
    painter.end()
    pixmap.save(f"{icons_dir}/icon_{size}.png")
    print(f"Created icon_{size}.png")

# 生成.ico文件（Windows图标）
ico_pixmap = QPixmap(256, 256)
ico_pixmap.fill(Qt.GlobalColor.transparent)
painter = QPainter(ico_pixmap)
painter.setRenderHint(QPainter.RenderHint.Antialiasing)

# 蓝色圆角背景
painter.setBrush(QColor("#1677ff"))
painter.setPen(Qt.PenStyle.NoPen)
painter.drawRoundedRect(0, 0, 256, 256, 51, 51)

# 白色锁图标
lock_icon = qta.icon("fa6s.lock", color="white")
lock_pixmap = lock_icon.pixmap(115, 115)
painter.drawPixmap(70, 70, lock_pixmap)

painter.end()
ico_pixmap.save("icon.ico", "ICO")
print("Created icon.ico")

# 生成.icns需要的PNG（macOS用）
ico_pixmap.save("icon.png", "PNG")
print("Created icon.png")

print("All icons created!")
