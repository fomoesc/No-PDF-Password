"""
UI主窗口模块
严格按设计图实现：左侧导航 + 右侧内容区，自定义矢量图标
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QProgressBar, QFileDialog, QMessageBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen, QBrush

from .config_manager import ConfigManager
from .pdf_decryptor import (
    scan_pdf_files, process_single_pdf,
    PDFStatus, PDFResult
)
from .icons import (
    _draw_lock_icon, _draw_folder_icon, _draw_grid_icon, _draw_key_icon,
    _draw_pdf_icon, _draw_check_circle, _draw_x_circle,
    _draw_small_lock, _draw_trash_icon, _draw_shield_icon
)


# ============================================================
# 颜色常量
# ============================================================
C_BG = "#f0f2f5"
C_WHITE = "#ffffff"
C_PRIMARY = "#1677ff"
C_PRIMARY_LIGHT = "#e6f4ff"
C_PRIMARY_HOVER = "#4096ff"
C_PRIMARY_PRESSED = "#0958d9"
C_PRIMARY_DISABLED = "#91caff"
C_SUCCESS = "#52c41a"
C_SUCCESS_BG = "#f6ffed"
C_WARNING = "#faad14"
C_ERROR = "#ff4d4f"
C_ERROR_BG = "#fff2f0"
C_TEXT = "#262626"
C_TEXT_SEC = "#8c8c8c"
C_TEXT_LIGHT = "#bfbfbf"
C_BORDER = "#e8e8e8"
C_HOVER = "#f5f5f5"
C_SIDEBAR_W = 220


# ============================================================
# 左侧导航栏
# ============================================================
class SidebarWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(C_SIDEBAR_W)
        self.setStyleSheet(f"""
            SidebarWidget {{
                background: {C_WHITE};
                border-right: 1px solid {C_BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 28, 20, 16)
        layout.setSpacing(0)

        # ---------- Logo ----------
        logo_row = QHBoxLayout()
        logo_row.setSpacing(12)

        logo_icon = _PaintedIcon("lock", 40)
        logo_icon.setFixedSize(40, 40)
        logo_row.addWidget(logo_icon)

        txt = QVBoxLayout()
        txt.setSpacing(2)
        t1 = QLabel("No PDF Password")
        t1.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        t1.setStyleSheet(f"color:{C_TEXT};")
        txt.addWidget(t1)
        t2 = QLabel("轻松解密，安全无忧")
        t2.setFont(QFont("Microsoft YaHei", 9))
        t2.setStyleSheet(f"color:{C_TEXT_SEC};")
        txt.addWidget(t2)
        logo_row.addLayout(txt)
        logo_row.addStretch()
        layout.addLayout(logo_row)

        # ---------- 导航 ----------
        layout.addSpacing(44)

        self.nav_decrypt = self._make_nav("grid", "解密", active=True)
        layout.addWidget(self.nav_decrypt)
        layout.addSpacing(8)
        self.nav_password = self._make_nav("key", "密码库", active=False)
        layout.addWidget(self.nav_password)

        layout.addStretch()

        # ---------- 安全提示卡片 ----------
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {C_PRIMARY_LIGHT};
                border-radius: 8px;
            }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 14, 14, 14)
        cl.setSpacing(6)

        shield_row = QHBoxLayout()
        shield_row.setSpacing(6)
        shield_icon = _PaintedIcon("shield", 18)
        shield_icon.setFixedSize(18, 18)
        shield_row.addWidget(shield_icon)
        st = QLabel("安全 & 隐私")
        st.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        st.setStyleSheet(f"color:{C_PRIMARY};background:transparent;")
        shield_row.addWidget(st)
        shield_row.addStretch()
        cl.addLayout(shield_row)

        sd = QLabel("所有操作仅在本地完成，\n文件不上传，保障您的隐私安全。")
        sd.setFont(QFont("Microsoft YaHei", 9))
        sd.setStyleSheet(f"color:{C_TEXT_SEC};background:transparent;")
        sd.setWordWrap(True)
        cl.addWidget(sd)

        layout.addWidget(card)

        # ---------- 版本号 ----------
        layout.addSpacing(12)
        ver = QLabel("v1.0.0")
        ver.setFont(QFont("Microsoft YaHei", 9))
        ver.setStyleSheet(f"color:{C_TEXT_LIGHT};")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver)

    def _make_nav(self, icon_type: str, text: str, active: bool) -> QWidget:
        w = QWidget()
        w.setCursor(Qt.CursorShape.PointingHandCursor)
        w.setFixedHeight(44)

        hl = QHBoxLayout(w)
        hl.setContentsMargins(16, 0, 16, 0)
        hl.setSpacing(10)

        ic = _PaintedIcon(icon_type, 20)
        ic.setFixedSize(20, 20)
        if active:
            ic.set_icon_color(C_PRIMARY)
        else:
            ic.set_icon_color(C_TEXT_SEC)
        hl.addWidget(ic)

        lb = QLabel(text)
        lb.setFont(QFont("Microsoft YaHei", 11))
        if active:
            lb.setStyleSheet(f"color:{C_PRIMARY};font-weight:bold;background:transparent;")
        else:
            lb.setStyleSheet(f"color:{C_TEXT_SEC};background:transparent;")
        hl.addWidget(lb)
        hl.addStretch()

        if active:
            w.setStyleSheet(f"""
                QWidget {{
                    background: {C_PRIMARY_LIGHT};
                    border-radius: 8px;
                }}
            """)
        else:
            w.setStyleSheet(f"""
                QWidget {{ background: transparent; border-radius: 8px; }}
                QWidget:hover {{ background: {C_HOVER}; }}
            """)
        return w


# ============================================================
# PDF列表项 Widget
# ============================================================
class PDFItemWidget(QWidget):
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.file_name = Path(file_path).name
        self.setFixedHeight(48)

        hl = QHBoxLayout(self)
        hl.setContentsMargins(16, 0, 16, 0)
        hl.setSpacing(12)

        # PDF图标
        pdf_icon = _PaintedIcon("pdf", 32)
        pdf_icon.setFixedSize(32, 32)
        hl.addWidget(pdf_icon)

        # 文件名
        self.name_label = QLabel(self.file_name)
        self.name_label.setFont(QFont("Microsoft YaHei", 11))
        self.name_label.setStyleSheet(f"color:{C_TEXT};")
        hl.addWidget(self.name_label, 1)

        # 状态图标
        self.status_icon = _PaintedIcon("check_circle", 18)
        self.status_icon.setFixedSize(18, 18)
        self.status_icon.setVisible(False)
        hl.addWidget(self.status_icon)

        # 状态文字
        self.status_label = QLabel("等待处理...")
        self.status_label.setFont(QFont("Microsoft YaHei", 10))
        self.status_label.setStyleSheet(f"color:{C_TEXT_SEC};")
        hl.addWidget(self.status_label)

        # 删除图标
        self.trash_icon = _PaintedIcon("trash", 18)
        self.trash_icon.setFixedSize(18, 18)
        self.trash_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        hl.addWidget(self.trash_icon)

    def set_status(self, status_text: str, icon_type: str = "", color: str = ""):
        self.status_label.setText(status_text)
        if icon_type:
            self.status_icon.set_icon(icon_type)
            self.status_icon.setVisible(True)
        if color:
            self.status_label.setStyleSheet(f"color:{color};")


# ============================================================
# 可绘制图标的 QWidget
# ============================================================
class _PaintedIcon(QWidget):
    def __init__(self, icon_type: str = "lock", size: int = 24, parent=None):
        super().__init__(parent)
        self._icon_type = icon_type
        self._icon_color = None  # None = 用默认颜色
        self.setFixedSize(size, size)

    def set_icon(self, icon_type: str):
        self._icon_type = icon_type
        self._icon_color = None
        self.update()

    def set_icon_color(self, color: str):
        self._icon_color = color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        sz = self.width()

        fn_map = {
            "lock": _draw_lock_icon,
            "lock_small": _draw_small_lock,
            "folder": _draw_folder_icon,
            "grid": _draw_grid_icon,
            "key": _draw_key_icon,
            "pdf": _draw_pdf_icon,
            "check_circle": _draw_check_circle,
            "x_circle": _draw_x_circle,
            "trash": _draw_trash_icon,
            "shield": _draw_shield_icon,
        }
        fn = fn_map.get(self._icon_type)
        if fn:
            if self._icon_color and self._icon_type in ("grid", "key", "lock_small", "shield", "trash"):
                fn(p, 0, 0, sz, color=self._icon_color)
            else:
                fn(p, 0, 0, sz)


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

    # ---- 初始化 ----
    def _init_ui(self):
        self.setWindowTitle("No PDF Password")
        self.setMinimumSize(900, 620)
        self.resize(1020, 660)

        self.setStyleSheet(f"QMainWindow {{ background: {C_BG}; }}")

        central = QWidget()
        central.setStyleSheet(f"background:{C_BG};")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 左侧
        self.sidebar = SidebarWidget()
        root.addWidget(self.sidebar)

        # 右侧内容
        content = QWidget()
        content.setStyleSheet(f"background:{C_BG};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(24, 24, 24, 20)
        cl.setSpacing(16)

        # 扫描路径卡片
        self._build_scan_card(cl)

        # PDF列表卡片
        self._build_list_card(cl)

        # 底部统计栏
        self._build_stats_bar(cl)

        root.addWidget(content, 1)

    # ---- 扫描路径卡片 ----
    def _build_scan_card(self, parent: QVBoxLayout):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {C_WHITE};
                border-radius: 12px;
            }}
        """)
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 20)
        vl.setSpacing(16)

        # 标题行
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        folder_icon = _PaintedIcon("folder", 22)
        folder_icon.setFixedSize(22, 22)
        title_row.addWidget(folder_icon)
        tl = QLabel("扫描路径")
        tl.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        tl.setStyleSheet(f"color:{C_TEXT};")
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
                background: {C_BG};
                border: 1px solid {C_BORDER};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                color: {C_TEXT};
            }}
        """)
        input_row.addWidget(self.path_edit, 1)

        self.btn_browse = QPushButton("  选择文件夹")
        self.btn_browse.setFixedHeight(44)
        self.btn_browse.setMinimumWidth(130)
        self.btn_browse.setIconSize(self.btn_browse.iconSize())
        self.btn_browse.setStyleSheet(f"""
            QPushButton {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                color: {C_TEXT};
            }}
            QPushButton:hover {{
                border-color: {C_PRIMARY};
                color: {C_PRIMARY};
            }}
        """)
        self.btn_browse.clicked.connect(self._browse_folder)
        input_row.addWidget(self.btn_browse)

        self.btn_start = QPushButton("  开始解密")
        self.btn_start.setFixedHeight(44)
        self.btn_start.setMinimumWidth(130)
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background: {C_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-size: 13px;
                font-weight: bold;
                color: white;
            }}
            QPushButton:hover {{ background: {C_PRIMARY_HOVER}; }}
            QPushButton:pressed {{ background: {C_PRIMARY_PRESSED}; }}
            QPushButton:disabled {{ background: {C_PRIMARY_DISABLED}; }}
        """)
        self.btn_start.clicked.connect(self._start_decrypt)
        input_row.addWidget(self.btn_start)

        vl.addLayout(input_row)
        parent.addWidget(card)

    # ---- PDF列表卡片 ----
    def _build_list_card(self, parent: QVBoxLayout):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {C_WHITE};
                border-radius: 12px;
            }}
        """)
        vl = QVBoxLayout(card)
        vl.setContentsMargins(24, 20, 24, 16)
        vl.setSpacing(0)

        self.list_title = QLabel("待解密PDF (0)")
        self.list_title.setFont(QFont("Microsoft YaHei", 13, QFont.Bold))
        self.list_title.setStyleSheet(f"color:{C_TEXT};padding-bottom:8px;")
        vl.addWidget(self.list_title)

        self.pdf_list = QListWidget()
        self.pdf_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background: transparent;
                border-bottom: 1px solid {C_BORDER};
                padding: 0;
            }}
            QListWidget::item:selected {{
                background: {C_PRIMARY_LIGHT};
            }}
            QListWidget::item:hover {{
                background: {C_HOVER};
            }}
        """)
        vl.addWidget(self.pdf_list, 1)
        parent.addWidget(card, 1)

    # ---- 底部统计栏 ----
    def _build_stats_bar(self, parent: QVBoxLayout):
        bar = QFrame()
        bar.setFixedHeight(56)
        bar.setStyleSheet(f"""
            QFrame {{
                background: {C_WHITE};
                border-radius: 12px;
            }}
        """)
        hl = QHBoxLayout(bar)
        hl.setContentsMargins(24, 0, 24, 0)
        hl.setSpacing(20)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {C_BORDER};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {C_PRIMARY};
                border-radius: 3px;
            }}
        """)
        hl.addWidget(self.progress_bar, 1)

        # 统计项
        self.stat_success = self._stat_widget("check_circle", "0", "已成功", C_SUCCESS)
        self.stat_no_pwd = self._stat_widget("lock_small", "0", "无需处理", C_PRIMARY)
        self.stat_failed = self._stat_widget("x_circle", "0", "失败", C_ERROR)

        hl.addWidget(self.stat_success)
        hl.addWidget(self.stat_no_pwd)
        hl.addWidget(self.stat_failed)

        parent.addWidget(bar)

    def _stat_widget(self, icon_type: str, value: str, label: str, color: str) -> QWidget:
        w = QWidget()
        hl = QHBoxLayout(w)
        hl.setContentsMargins(12, 0, 12, 0)
        hl.setSpacing(8)

        ic = _PaintedIcon(icon_type, 22)
        ic.setFixedSize(22, 22)
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
        lbl.setStyleSheet(f"color:{C_TEXT_SEC};background:transparent;")
        vl.addWidget(lbl)

        hl.addLayout(vl)

        # 保存引用
        w._value_label = val
        return w

    # ---- 业务逻辑 ----
    def _load_last_path(self):
        last = self.config.get_last_scan_path()
        if last and Path(last).exists():
            self.path_edit.setText(last)

    def _browse_folder(self):
        last = self.config.get_last_scan_path()
        folder = QFileDialog.getExistingDirectory(self, "选择要扫描的文件夹", last)
        if folder:
            self.path_edit.setText(folder)
            self.config.set_last_scan_path(folder)

    def _start_decrypt(self):
        folder = self.path_edit.text()
        if not folder:
            QMessageBox.warning(self, "提示", "请先选择要扫描的文件夹！")
            return
        path = Path(folder)
        if not path.exists():
            QMessageBox.warning(self, "提示", "选择的文件夹不存在！")
            return

        self.btn_start.setEnabled(False)
        self.btn_browse.setEnabled(False)
        self.pdf_list.clear()
        self.pdf_results.clear()
        self.progress_bar.setValue(0)

        pdf_files = scan_pdf_files(path)
        if not pdf_files:
            QMessageBox.information(self, "提示", "未找到任何PDF文件！")
            self.btn_start.setEnabled(True)
            self.btn_browse.setEnabled(True)
            return

        self.list_title.setText(f"待解密PDF ({len(pdf_files)})")

        for pdf_path in pdf_files:
            w = PDFItemWidget(str(pdf_path))
            item = QListWidgetItem()
            item.setSizeHint(w.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, str(pdf_path))
            self.pdf_list.addItem(item)
            self.pdf_list.setItemWidget(item, w)

        self.progress_bar.setMaximum(len(pdf_files))

        passwords = self.config.get_passwords()
        self.worker = DecryptWorker(pdf_files, passwords)
        self.worker.progress.connect(self._on_progress)
        self.worker.result_ready.connect(self._on_result)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, current: int, total: int):
        self.progress_bar.setValue(current)

    def _on_result(self, result: PDFResult):
        self.pdf_results.append(result)

        for i in range(self.pdf_list.count()):
            item = self.pdf_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == str(result.file_path):
                w = self.pdf_list.itemWidget(item)
                if w:
                    if result.status == PDFStatus.NO_PASSWORD:
                        w.set_status("无密码", "lock_small", C_PRIMARY)
                    elif result.status == PDFStatus.DECRYPTED:
                        w.set_status("已删除密码", "check_circle", C_SUCCESS)
                    elif result.status == PDFStatus.NEED_MANUAL:
                        w.set_status("待手动处理", "x_circle", C_ERROR)
                break

        self._refresh_stats()

    def _refresh_stats(self):
        ok = sum(1 for r in self.pdf_results if r.status == PDFStatus.DECRYPTED)
        nop = sum(1 for r in self.pdf_results if r.status == PDFStatus.NO_PASSWORD)
        fail = sum(1 for r in self.pdf_results if r.status == PDFStatus.NEED_MANUAL)
        self.stat_success._value_label.setText(str(ok))
        self.stat_no_pwd._value_label.setText(str(nop))
        self.stat_failed._value_label.setText(str(fail))

    def _on_finished(self, decrypted: int, no_password: int, need_manual: int):
        self.btn_start.setEnabled(True)
        self.btn_browse.setEnabled(True)
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
