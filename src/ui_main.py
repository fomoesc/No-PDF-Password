"""
UI主窗口 - 严格按设计图实现
左侧导航 + 右侧内容区，qtawesome专业图标
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QProgressBar, QFileDialog, QMessageBox, QFrame, QStackedWidget,
    QAbstractItemView
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QPainterPath

import qtawesome as qta

from .config_manager import ConfigManager
from .pdf_decryptor import (
    scan_pdf_files, process_single_pdf,
    PDFStatus, PDFResult
)
from .icons import PDFIconWidget


# ============================================================
# 颜色常量
# ============================================================
BG = "#f0f2f5"
WHITE = "#ffffff"
PRIMARY = "#1677ff"
PRIMARY_LIGHT = "#e6f4ff"
PRIMARY_HOVER = "#4096ff"
PRIMARY_PRESSED = "#0958d9"
PRIMARY_DISABLED = "#91caff"
SUCCESS = "#52c41a"
SUCCESS_LIGHT = "#f6ffed"
ERROR = "#ff4d4f"
ERROR_LIGHT = "#fff2f0"
TEXT = "#262626"
TEXT_SEC = "#8c8c8c"
TEXT_LIGHT = "#bfbfbf"
BORDER = "#e8e8e8"
HOVER_BG = "#f5f5f5"
SIDEBAR_W = 200


# ============================================================
# 左侧导航栏
# ============================================================
class SidebarWidget(QFrame):
    nav_clicked = Signal(int)  # 0=解密, 1=密码库

    def __init__(self):
        super().__init__()
        self.setFixedWidth(SIDEBAR_W)
        self.setStyleSheet(f"""
            SidebarWidget {{
                background: {WHITE};
                border-right: 1px solid {BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(0)

        # ---------- Logo ----------
        logo_row = QHBoxLayout()
        logo_row.setSpacing(10)

        # 蓝色圆角方形 + 白色锁
        logo_pixmap = QPixmap(40, 40)
        logo_pixmap.fill(Qt.GlobalColor.transparent)
        lp = QPainter(logo_pixmap)
        lp.setRenderHint(QPainter.RenderHint.Antialiasing)
        lp.setBrush(QColor(PRIMARY))
        lp.setPen(Qt.PenStyle.NoPen)
        lp.drawRoundedRect(0, 0, 40, 40, 10, 10)
        lp.end()
        # 画白色锁在上面
        lock_icon = qta.icon("fa6s.lock", color="white")
        lock_pixmap = lock_icon.pixmap(20, 20)
        p2 = QPainter(logo_pixmap)
        p2.setRenderHint(QPainter.RenderHint.Antialiasing)
        p2.drawPixmap(10, 10, lock_pixmap)
        p2.end()

        logo_label = QLabel()
        logo_label.setPixmap(logo_pixmap)
        logo_row.addWidget(logo_label)

        txt = QVBoxLayout()
        txt.setSpacing(1)
        t1 = QLabel("No PDF Password")
        t1.setFont(QFont("Microsoft YaHei", 13, QFont.Bold))
        t1.setStyleSheet(f"color:{TEXT};")
        txt.addWidget(t1)
        t2 = QLabel("轻松解密，安全无忧")
        t2.setFont(QFont("Microsoft YaHei", 9))
        t2.setStyleSheet(f"color:{TEXT_SEC};")
        txt.addWidget(t2)
        logo_row.addLayout(txt)
        logo_row.addStretch()
        layout.addLayout(logo_row)

        # ---------- 导航 ----------
        layout.addSpacing(36)

        self.nav_btns = []

        # 解密
        self.nav_decrypt = self._nav_item("fa6s.table-cells", "解密", active=True, idx=0)
        self.nav_btns.append(self.nav_decrypt)
        layout.addWidget(self.nav_decrypt)
        layout.addSpacing(4)

        # 密码库
        self.nav_password = self._nav_item("fa6s.key", "密码库", active=False, idx=1)
        self.nav_btns.append(self.nav_password)
        layout.addWidget(self.nav_password)

        layout.addStretch()

        # ---------- 安全提示卡片 ----------
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {PRIMARY_LIGHT};
                border-radius: 8px;
            }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 14, 14, 14)
        cl.setSpacing(6)

        shield_row = QHBoxLayout()
        shield_row.setSpacing(6)
        shield_icon = qta.icon("fa6s.shield-halved", color=PRIMARY)
        si = QLabel()
        si.setPixmap(shield_icon.pixmap(16, 16))
        shield_row.addWidget(si)
        st = QLabel("安全 & 隐私")
        st.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        st.setStyleSheet(f"color:{PRIMARY};background:transparent;")
        shield_row.addWidget(st)
        shield_row.addStretch()
        cl.addLayout(shield_row)

        sd = QLabel("所有操作仅在本地完成，\n文件不上传，保障您的隐私安全。")
        sd.setFont(QFont("Microsoft YaHei", 9))
        sd.setStyleSheet(f"color:{TEXT_SEC};background:transparent;")
        sd.setWordWrap(True)
        cl.addWidget(sd)

        layout.addWidget(card)

        # ---------- 版本号 ----------
        layout.addSpacing(12)
        ver = QLabel("v1.0.0")
        ver.setFont(QFont("Microsoft YaHei", 9))
        ver.setStyleSheet(f"color:{TEXT_LIGHT};")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver)

    def _nav_item(self, icon_name: str, text: str, active: bool, idx: int) -> QWidget:
        w = QWidget()
        w.setCursor(Qt.CursorShape.PointingHandCursor)
        w.setFixedHeight(42)

        hl = QHBoxLayout(w)
        hl.setContentsMargins(14, 0, 14, 0)
        hl.setSpacing(10)

        color = PRIMARY if active else TEXT_SEC
        ic = QLabel()
        ic.setPixmap(qta.icon(icon_name, color=color).pixmap(18, 18))
        ic.setFixedSize(18, 18)
        hl.addWidget(ic)

        lb = QLabel(text)
        lb.setFont(QFont("Microsoft YaHei", 11))
        fw = "bold" if active else "normal"
        lb.setStyleSheet(f"color:{color};font-weight:{fw};background:transparent;")
        hl.addWidget(lb)
        hl.addStretch()

        if active:
            w.setStyleSheet(f"QWidget {{ background: {PRIMARY_LIGHT}; border-radius: 8px; }}")
        else:
            w.setStyleSheet(f"""
                QWidget {{ background: transparent; border-radius: 8px; }}
                QWidget:hover {{ background: {HOVER_BG}; }}
            """)

        # 存储状态
        w._idx = idx
        w._active = active
        w._icon_name = icon_name
        w._text = text

        # 点击事件
        w.mousePressEvent = lambda e, i=idx: self.nav_clicked.emit(i)

        return w

    def set_active(self, idx: int):
        """设置激活的导航项"""
        for i, btn in enumerate(self.nav_btns):
            is_active = (i == idx)
            color = PRIMARY if is_active else TEXT_SEC
            # 更新图标
            icon_lbl = btn.findChildren(QLabel)[0]
            icon_lbl.setPixmap(qta.icon(btn._icon_name, color=color).pixmap(18, 18))
            # 更新文字
            text_lbl = btn.findChildren(QLabel)[1]
            fw = "bold" if is_active else "normal"
            text_lbl.setStyleSheet(f"color:{color};font-weight:{fw};background:transparent;")
            # 更新背景
            if is_active:
                btn.setStyleSheet(f"QWidget {{ background: {PRIMARY_LIGHT}; border-radius: 8px; }}")
            else:
                btn.setStyleSheet(f"""
                    QWidget {{ background: transparent; border-radius: 8px; }}
                    QWidget:hover {{ background: {HOVER_BG}; }}
                """)


# ============================================================
# PDF列表项
# ============================================================
class PDFItemWidget(QWidget):
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.file_name = Path(file_path).name
        self.setFixedHeight(48)

        hl = QHBoxLayout(self)
        hl.setContentsMargins(20, 0, 20, 0)
        hl.setSpacing(12)

        # PDF图标
        pdf_icon = PDFIconWidget(28)
        hl.addWidget(pdf_icon)

        # 文件名
        self.name_label = QLabel(self.file_name)
        self.name_label.setFont(QFont("Microsoft YaHei", 11))
        self.name_label.setStyleSheet(f"color:{TEXT};")
        hl.addWidget(self.name_label, 1)

        # 状态图标
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(18, 18)
        self.status_icon.setVisible(False)
        hl.addWidget(self.status_icon)

        # 状态文字
        self.status_label = QLabel("等待处理...")
        self.status_label.setFont(QFont("Microsoft YaHei", 10))
        self.status_label.setStyleSheet(f"color:{TEXT_SEC};")
        hl.addWidget(self.status_label)

        # 删除图标
        self.trash_icon = QLabel()
        self.trash_icon.setPixmap(qta.icon("fa6s.trash-can", color="#bfbfbf").pixmap(16, 16))
        self.trash_icon.setFixedSize(16, 16)
        self.trash_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        hl.addWidget(self.trash_icon)

    def set_status(self, status_text: str, icon_name: str = "", color: str = ""):
        self.status_label.setText(status_text)
        if icon_name and color:
            self.status_icon.setPixmap(qta.icon(icon_name, color=color).pixmap(18, 18))
            self.status_icon.setVisible(True)
        if color:
            self.status_label.setStyleSheet(f"color:{color};")


# ============================================================
# 解密页面
# ============================================================
class DecryptPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self._build_scan_card(layout)
        self._build_list_card(layout)
        self._build_stats_bar(layout)

    def _build_scan_card(self, parent: QVBoxLayout):
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background: {WHITE}; border-radius: 12px; }}")
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 20)
        vl.setSpacing(16)

        # 标题
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        folder_ic = QLabel()
        folder_ic.setPixmap(qta.icon("fa6s.folder", color=PRIMARY).pixmap(20, 20))
        title_row.addWidget(folder_ic)
        tl = QLabel("扫描路径")
        tl.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        tl.setStyleSheet(f"color:{TEXT};")
        title_row.addWidget(tl)
        title_row.addStretch()
        vl.addLayout(title_row)

        # 输入行
        input_row = QHBoxLayout()
        input_row.setSpacing(12)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("请选择要扫描的文件夹...")
        self.path_edit.setReadOnly(True)
        self.path_edit.setFixedHeight(44)
        self.path_edit.setStyleSheet(f"""
            QLineEdit {{
                background: {BG};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                color: {TEXT};
            }}
        """)
        input_row.addWidget(self.path_edit, 1)

        self.btn_browse = QPushButton("  选择文件夹")
        self.btn_browse.setFixedHeight(44)
        self.btn_browse.setMinimumWidth(120)
        browse_ic = qta.icon("fa6s.folder-open", color=TEXT)
        self.btn_browse.setIcon(browse_ic)
        self.btn_browse.setIconSize(QSize(16, 16))
        self.btn_browse.setStyleSheet(f"""
            QPushButton {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 13px;
                color: {TEXT};
            }}
            QPushButton:hover {{ border-color: {PRIMARY}; color: {PRIMARY}; }}
        """)
        input_row.addWidget(self.btn_browse)

        self.btn_start = QPushButton("  开始解密")
        self.btn_start.setFixedHeight(44)
        self.btn_start.setMinimumWidth(130)
        start_ic = qta.icon("fa6s.lock", color="white")
        self.btn_start.setIcon(start_ic)
        self.btn_start.setIconSize(QSize(14, 14))
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-size: 13px;
                font-weight: bold;
                color: white;
            }}
            QPushButton:hover {{ background: {PRIMARY_HOVER}; }}
            QPushButton:pressed {{ background: {PRIMARY_PRESSED}; }}
            QPushButton:disabled {{ background: {PRIMARY_DISABLED}; }}
        """)
        input_row.addWidget(self.btn_start)

        vl.addLayout(input_row)
        parent.addWidget(card)

    def _build_list_card(self, parent: QVBoxLayout):
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background: {WHITE}; border-radius: 12px; }}")
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 12)
        vl.setSpacing(0)

        self.list_title = QLabel("待解密PDF (0)")
        self.list_title.setFont(QFont("Microsoft YaHei", 13, QFont.Bold))
        self.list_title.setStyleSheet(f"color:{TEXT};padding-bottom:8px;")
        vl.addWidget(self.list_title)

        self.pdf_list = QListWidget()
        self.pdf_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.pdf_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background: transparent;
                border-bottom: 1px solid {BORDER};
                padding: 0;
            }}
            QListWidget::item:selected {{
                background: {PRIMARY_LIGHT};
            }}
            QListWidget::item:hover {{
                background: {HOVER_BG};
            }}
            QScrollBar:vertical {{
                width: 6px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: #d0d0d0;
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        vl.addWidget(self.pdf_list, 1)
        parent.addWidget(card, 1)

    def _build_stats_bar(self, parent: QVBoxLayout):
        bar = QFrame()
        bar.setFixedHeight(56)
        bar.setStyleSheet(f"QFrame {{ background: {WHITE}; border-radius: 12px; }}")
        hl = QHBoxLayout(bar)
        hl.setContentsMargins(24, 0, 24, 0)
        hl.setSpacing(24)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m")
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {BORDER};
                border: none;
                border-radius: 3px;
                text-align: center;
                font-size: 10px;
                color: {TEXT_SEC};
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {PRIMARY}, stop:1 {PRIMARY_HOVER});
                border-radius: 3px;
            }}
        """)
        hl.addWidget(self.progress_bar, 1)

        # 统计项
        self.stat_success = self._stat("fa6s.circle-check", "0", "已成功", SUCCESS)
        self.stat_no_pwd = self._stat("fa6s.lock", "0", "无需处理", PRIMARY)
        self.stat_failed = self._stat("fa6s.trash-can", "0", "失败", ERROR)

        hl.addWidget(self.stat_success)
        hl.addWidget(self.stat_no_pwd)
        hl.addWidget(self.stat_failed)

        parent.addWidget(bar)

    def _stat(self, icon_name: str, value: str, label: str, color: str) -> QWidget:
        w = QWidget()
        hl = QHBoxLayout(w)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(8)

        ic = QLabel()
        ic.setPixmap(qta.icon(icon_name, color=color).pixmap(20, 20))
        ic.setFixedSize(20, 20)
        hl.addWidget(ic)

        vl = QVBoxLayout()
        vl.setSpacing(0)
        vl.setContentsMargins(0, 0, 0, 0)
        val = QLabel(value)
        val.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        val.setStyleSheet(f"color:{color};background:transparent;")
        vl.addWidget(val)
        lbl = QLabel(label)
        lbl.setFont(QFont("Microsoft YaHei", 9))
        lbl.setStyleSheet(f"color:{TEXT_SEC};background:transparent;")
        vl.addWidget(lbl)
        hl.addLayout(vl)

        w._value_label = val
        return w


# ============================================================
# 密码库页面
# ============================================================
class PasswordPage(QWidget):
    def __init__(self, config: ConfigManager):
        super().__init__()
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # 标题卡片
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background: {WHITE}; border-radius: 12px; }}")
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 20)
        vl.setSpacing(16)

        # 标题行
        title_row = QHBoxLayout()
        key_ic = QLabel()
        key_ic.setPixmap(qta.icon("fa6s.key", color=PRIMARY).pixmap(20, 20))
        title_row.addWidget(key_ic)
        tl = QLabel("密码库")
        tl.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        tl.setStyleSheet(f"color:{TEXT};")
        title_row.addWidget(tl)
        title_row.addStretch()
        self.count_label = QLabel("共 0 个密码")
        self.count_label.setFont(QFont("Microsoft YaHei", 10))
        self.count_label.setStyleSheet(f"color:{TEXT_SEC};")
        title_row.addWidget(self.count_label)
        vl.addLayout(title_row)

        # 密码列表
        self.pwd_list = QListWidget()
        self.pwd_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: 1px solid {BORDER};
                border-radius: 8px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px 16px;
                border-bottom: 1px solid {BORDER};
            }}
            QListWidget::item:selected {{
                background: {PRIMARY_LIGHT};
            }}
            QListWidget::item:hover {{
                background: {HOVER_BG};
            }}
        """)
        vl.addWidget(self.pwd_list, 1)

        # 添加密码
        add_row = QHBoxLayout()
        add_row.setSpacing(12)

        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("输入新密码...")
        self.pwd_input.setFixedHeight(44)
        self.pwd_input.setStyleSheet(f"""
            QLineEdit {{
                background: {BG};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                color: {TEXT};
            }}
        """)
        self.pwd_input.returnPressed.connect(self._add_password)
        add_row.addWidget(self.pwd_input, 1)

        self.btn_add = QPushButton("  添加密码")
        self.btn_add.setFixedHeight(44)
        self.btn_add.setMinimumWidth(120)
        add_ic = qta.icon("fa6s.plus", color="white")
        self.btn_add.setIcon(add_ic)
        self.btn_add.setIconSize(QSize(14, 14))
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: bold;
                color: white;
            }}
            QPushButton:hover {{ background: {PRIMARY_HOVER}; }}
            QPushButton:pressed {{ background: {PRIMARY_PRESSED}; }}
        """)
        self.btn_add.clicked.connect(self._add_password)
        add_row.addWidget(self.btn_add)

        vl.addLayout(add_row)

        # 删除按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_delete = QPushButton("  删除选中")
        self.btn_delete.setFixedHeight(36)
        self.btn_delete.setMinimumWidth(110)
        del_ic = qta.icon("fa6s.trash-can", color="white")
        self.btn_delete.setIcon(del_ic)
        self.btn_delete.setIconSize(QSize(14, 14))
        self.btn_delete.setStyleSheet(f"""
            QPushButton {{
                background: {ERROR};
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                color: white;
            }}
            QPushButton:hover {{ background: #ff7875; }}
            QPushButton:pressed {{ background: #d9363e; }}
        """)
        self.btn_delete.clicked.connect(self._delete_password)
        btn_row.addWidget(self.btn_delete)

        vl.addLayout(btn_row)
        parent.addWidget(card)

        # 加载密码
        self._load_passwords()

    def _load_passwords(self):
        self.pwd_list.clear()
        for pwd in self.config.get_passwords():
            self.pwd_list.addItem(pwd)
        self._update_count()

    def _update_count(self):
        count = self.pwd_list.count()
        self.count_label.setText(f"共 {count} 个密码")

    def _add_password(self):
        pwd = self.pwd_input.text().strip()
        if not pwd:
            return
        if self.config.add_password(pwd):
            self.pwd_list.addItem(pwd)
            self.pwd_input.clear()
            self._update_count()
        else:
            QMessageBox.information(self, "提示", "该密码已存在！")

    def _delete_password(self):
        item = self.pwd_list.currentItem()
        if not item:
            QMessageBox.information(self, "提示", "请先选择要删除的密码！")
            return
        pwd = item.text()
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除密码 \"{pwd}\" 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config.remove_password(pwd)
            self.pwd_list.takeItem(self.pwd_list.row(item))
            self._update_count()


# ============================================================
# 主窗口
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.pdf_results = []
        self.worker = None

        self._init_ui()
        self._load_last_path()
        self._connect_signals()

    def _init_ui(self):
        self.setWindowTitle("No PDF Password")
        self.setMinimumSize(960, 620)
        self.resize(1060, 680)
        self.setStyleSheet(f"QMainWindow {{ background: {BG}; }}")

        central = QWidget()
        central.setStyleSheet(f"background:{BG};")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 左侧导航
        self.sidebar = SidebarWidget()
        root.addWidget(self.sidebar)

        # 右侧内容区
        content = QWidget()
        content.setStyleSheet(f"background:{BG};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(24, 24, 24, 20)
        cl.setSpacing(0)

        # 页面切换
        self.stack = QStackedWidget()
        self.decrypt_page = DecryptPage()
        self.password_page = PasswordPage(self.config)
        self.stack.addWidget(self.decrypt_page)
        self.stack.addWidget(self.password_page)
        cl.addWidget(self.stack, 1)

        root.addWidget(content, 1)

    def _connect_signals(self):
        # 侧边栏导航
        self.sidebar.nav_clicked.connect(self._switch_page)

        # 解密页面信号
        dp = self.decrypt_page
        dp.btn_browse.clicked.connect(self._browse_folder)
        dp.btn_start.clicked.connect(self._start_decrypt)

    def _switch_page(self, idx: int):
        self.stack.setCurrentIndex(idx)
        self.sidebar.set_active(idx)

    def _load_last_path(self):
        last = self.config.get_last_scan_path()
        if last and Path(last).exists():
            self.decrypt_page.path_edit.setText(last)

    def _browse_folder(self):
        last = self.config.get_last_scan_path()
        folder = QFileDialog.getExistingDirectory(self, "选择要扫描的文件夹", last)
        if folder:
            self.decrypt_page.path_edit.setText(folder)
            self.config.set_last_scan_path(folder)

    def _start_decrypt(self):
        folder = self.decrypt_page.path_edit.text()
        if not folder:
            QMessageBox.warning(self, "提示", "请先选择要扫描的文件夹！")
            return
        path = Path(folder)
        if not path.exists():
            QMessageBox.warning(self, "提示", "选择的文件夹不存在！")
            return

        dp = self.decrypt_page
        dp.btn_start.setEnabled(False)
        dp.btn_browse.setEnabled(False)
        dp.pdf_list.clear()
        self.pdf_results.clear()
        dp.progress_bar.setValue(0)

        pdf_files = scan_pdf_files(path)
        if not pdf_files:
            QMessageBox.information(self, "提示", "未找到任何PDF文件！")
            dp.btn_start.setEnabled(True)
            dp.btn_browse.setEnabled(True)
            return

        dp.list_title.setText(f"待解密PDF ({len(pdf_files)})")

        for pdf_path in pdf_files:
            w = PDFItemWidget(str(pdf_path))
            item = QListWidgetItem()
            item.setSizeHint(w.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, str(pdf_path))
            dp.pdf_list.addItem(item)
            dp.pdf_list.setItemWidget(item, w)

        dp.progress_bar.setMaximum(len(pdf_files))

        passwords = self.config.get_passwords()
        self.worker = DecryptWorker(pdf_files, passwords)
        self.worker.progress.connect(self._on_progress)
        self.worker.result_ready.connect(self._on_result)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, current: int, total: int):
        self.decrypt_page.progress_bar.setValue(current)

    def _on_result(self, result: PDFResult):
        self.pdf_results.append(result)
        dp = self.decrypt_page

        for i in range(dp.pdf_list.count()):
            item = dp.pdf_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == str(result.file_path):
                w = dp.pdf_list.itemWidget(item)
                if w:
                    if result.status == PDFStatus.NO_PASSWORD:
                        w.set_status("无密码", "fa6s.lock", PRIMARY)
                    elif result.status == PDFStatus.DECRYPTED:
                        w.set_status("已删除密码", "fa6s.circle-check", SUCCESS)
                    elif result.status == PDFStatus.NEED_MANUAL:
                        w.set_status("待手动处理", "fa6s.trash-can", ERROR)
                break

        self._refresh_stats()

    def _refresh_stats(self):
        ok = sum(1 for r in self.pdf_results if r.status == PDFStatus.DECRYPTED)
        nop = sum(1 for r in self.pdf_results if r.status == PDFStatus.NO_PASSWORD)
        fail = sum(1 for r in self.pdf_results if r.status == PDFStatus.NEED_MANUAL)
        dp = self.decrypt_page
        dp.stat_success._value_label.setText(str(ok))
        dp.stat_no_pwd._value_label.setText(str(nop))
        dp.stat_failed._value_label.setText(str(fail))

    def _on_finished(self, decrypted: int, no_password: int, need_manual: int):
        dp = self.decrypt_page
        dp.btn_start.setEnabled(True)
        dp.btn_browse.setEnabled(True)
        self.worker = None

        QMessageBox.information(
            self, "完成",
            f"扫描完成！\n\n✅ 已解锁：{decrypted}\n🔒 无需处理：{no_password}\n❌ 待手动处理：{need_manual}"
        )

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(3000)
        event.accept()


# ============================================================
# 工作线程
# ============================================================
class DecryptWorker(QThread):
    progress = Signal(int, int)
    result_ready = Signal(PDFResult)
    finished = Signal(int, int, int)

    def __init__(self, pdf_files, passwords):
        super().__init__()
        self.pdf_files = pdf_files
        self.passwords = passwords
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        ok = nop = fail = 0
        total = len(self.pdf_files)
        for i, pdf in enumerate(self.pdf_files):
            if self._cancelled:
                break
            result = process_single_pdf(pdf, self.passwords)
            self.result_ready.emit(result)
            if result.status == PDFStatus.DECRYPTED:
                ok += 1
            elif result.status == PDFStatus.NO_PASSWORD:
                nop += 1
            elif result.status == PDFStatus.NEED_MANUAL:
                fail += 1
            self.progress.emit(i + 1, total)
        self.finished.emit(ok, nop, fail)
