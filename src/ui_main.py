"""
UI主窗口模块
设计风格：左侧导航 + 右侧内容区，圆角卡片，蓝色主题
"""

from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, 
    QListWidget, QListWidgetItem, QProgressBar, 
    QFileDialog, QMessageBox, QFrame, QSpacerItem, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QFont, QColor, QIcon, QPainter, QPainterPath

from .config_manager import ConfigManager
from .pdf_decryptor import (
    scan_pdf_files, process_single_pdf, decrypt_with_password,
    PDFStatus, PDFResult
)


# 颜色常量
COLORS = {
    'bg': '#f0f2f5',           # 页面背景
    'sidebar_bg': '#ffffff',    # 侧边栏背景
    'card_bg': '#ffffff',       # 卡片背景
    'primary': '#1677ff',       # 主色调（蓝色）
    'primary_light': '#e6f4ff', # 浅蓝色背景
    'success': '#52c41a',       # 成功（绿色）
    'warning': '#faad14',       # 警告（黄色）
    'error': '#ff4d4f',         # 错误（红色）
    'text': '#262626',          # 主要文字
    'text_secondary': '#8c8c8c',# 次要文字
    'text_light': '#bfbfbb',    # 浅色文字
    'border': '#e8e8e8',        # 边框
    'hover': '#f5f5f5',         # 悬停效果
    'lock_icon': '#1677ff',     # 锁图标颜色
    'delete_icon': '#bfbfbb',   # 删除图标颜色
}


class SidebarWidget(QFrame):
    """左侧导航栏"""
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setStyleSheet(f"""
            SidebarWidget {{
                background-color: {COLORS['sidebar_bg']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 16)
        layout.setSpacing(0)
        
        # Logo区域
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(12)
        
        # Logo图标（蓝色锁）
        logo_icon = QLabel("🔒")
        logo_icon.setFont(QFont("Segoe UI Emoji", 24))
        logo_layout.addWidget(logo_icon)
        
        logo_text_layout = QVBoxLayout()
        logo_text_layout.setSpacing(2)
        
        logo_title = QLabel("No PDF Password")
        logo_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        logo_title.setStyleSheet(f"color: {COLORS['text']};")
        logo_text_layout.addWidget(logo_title)
        
        logo_subtitle = QLabel("轻松解密，安全无忧")
        logo_subtitle.setFont(QFont("Microsoft YaHei", 9))
        logo_subtitle.setStyleSheet(f"color: {COLORS['text_secondary']};")
        logo_text_layout.addWidget(logo_subtitle)
        
        logo_layout.addLayout(logo_text_layout)
        logo_layout.addStretch()
        layout.addLayout(logo_layout)
        
        # 导航项
        layout.addSpacing(40)
        
        self.nav_items = []
        
        # 解密导航
        self.decrypt_nav = self._create_nav_item("📄", "解密", True)
        self.nav_items.append(self.decrypt_nav)
        
        layout.addSpacing(8)
        
        # 密码库导航
        self.password_nav = self._create_nav_item("🔑", "密码库", False)
        self.nav_items.append(self.password_nav)
        
        layout.addStretch()
        
        # 安全提示
        security_frame = QFrame()
        security_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary_light']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        security_layout = QVBoxLayout(security_frame)
        security_layout.setContentsMargins(12, 12, 12, 12)
        security_layout.setSpacing(6)
        
        security_title = QLabel("🛡 安全 & 隐私")
        security_title.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        security_title.setStyleSheet(f"color: {COLORS['primary']}; background: transparent;")
        security_layout.addWidget(security_title)
        
        security_text = QLabel("所有操作仅在本地完成，\n文件不上传，保障您的隐私安全。")
        security_text.setFont(QFont("Microsoft YaHei", 9))
        security_text.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        security_text.setWordWrap(True)
        security_layout.addWidget(security_text)
        
        layout.addWidget(security_frame)
        
        # 版本号
        layout.addSpacing(16)
        version_label = QLabel("v1.0.0")
        version_label.setFont(QFont("Microsoft YaHei", 9))
        version_label.setStyleSheet(f"color: {COLORS['text_light']};")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
    
    def _create_nav_item(self, icon: str, text: str, is_active: bool) -> QWidget:
        """创建导航项"""
        item_widget = QWidget()
        item_widget.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        icon_label.setFixedWidth(24)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        text_label = QLabel(text)
        text_label.setFont(QFont("Microsoft YaHei", 11))
        layout.addWidget(text_label)
        layout.addStretch()
        
        # 设置样式
        if is_active:
            item_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {COLORS['primary_light']};
                    border-radius: 8px;
                }}
            """)
            text_label.setStyleSheet(f"color: {COLORS['primary']}; font-weight: bold;")
            icon_label.setStyleSheet(f"color: {COLORS['primary']};")
        else:
            item_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: transparent;
                }}
                QWidget:hover {{
                    background-color: {COLORS['hover']};
                }}
            """)
            text_label.setStyleSheet(f"color: {COLORS['text']};")
        
        return item_widget
    
    def set_active_nav(self, index: int):
        """设置激活的导航项"""
        for i, item in enumerate(self.nav_items):
            is_active = (i == index)
            # 重新创建导航项以更新样式
            pass


class PDFListWidgetItem(QWidget):
    """自定义PDF列表项"""
    
    def __init__(self, file_path: str, status: str = "等待处理"):
        super().__init__()
        self.file_path = file_path
        self.file_name = Path(file_path).name
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # PDF图标
        icon_label = QLabel("📄")
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setFixedWidth(32)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: #fff1f0;
                border-radius: 6px;
                padding: 4px;
            }
        """)
        layout.addWidget(icon_label)
        
        # 文件名
        self.name_label = QLabel(self.file_name)
        self.name_label.setFont(QFont("Microsoft YaHei", 11))
        self.name_label.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(self.name_label, 1)
        
        # 状态标签
        self.status_label = QLabel(status)
        self.status_label.setFont(QFont("Microsoft YaHei", 10))
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(self.status_label)
        
        # 状态图标
        self.status_icon = QLabel("")
        self.status_icon.setFont(QFont("Segoe UI Emoji", 14))
        self.status_icon.setFixedWidth(24)
        self.status_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_icon)
        
        # 删除按钮
        delete_btn = QLabel("🗑")
        delete_btn.setFont(QFont("Segoe UI Emoji", 12))
        delete_btn.setFixedWidth(24)
        delete_btn.setAlignment(Qt.AlignCenter)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['delete_icon']};
                padding: 4px;
                border-radius: 4px;
            }}
            QLabel:hover {{
                background-color: {COLORS['error']};
                color: white;
            }}
        """)
        layout.addWidget(delete_btn)
    
    def set_status(self, status: str, icon: str = "", color: str = ""):
        """更新状态"""
        self.status_label.setText(status)
        self.status_icon.setText(icon)
        if color:
            self.status_label.setStyleSheet(f"color: {color};")
            self.status_icon.setStyleSheet(f"color: {color};")


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.pdf_results = []
        self.worker = None
        
        self._init_ui()
        self._load_last_path()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("No PDF Password")
        self.setMinimumSize(900, 600)
        self.resize(1000, 650)
        
        # 设置主背景色
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg']};
            }}
        """)
        
        # 中心部件
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {COLORS['bg']};")
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左侧导航栏
        self.sidebar = SidebarWidget()
        main_layout.addWidget(self.sidebar)
        
        # 右侧内容区
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {COLORS['bg']};")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)
        
        # 扫描路径卡片
        self._create_scan_path_card(content_layout)
        
        # PDF列表卡片
        self._create_pdf_list_card(content_layout)
        
        # 底部统计栏
        self._create_stats_bar(content_layout)
        
        main_layout.addWidget(content_widget, 1)
    
    def _create_scan_path_card(self, layout: QVBoxLayout):
        """创建扫描路径卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)
        
        # 标题
        title_layout = QHBoxLayout()
        title_icon = QLabel("📁")
        title_icon.setFont(QFont("Segoe UI Emoji", 16))
        title_layout.addWidget(title_icon)
        
        title_label = QLabel("扫描路径")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text']};")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        card_layout.addLayout(title_layout)
        
        # 路径输入和按钮
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("请选择要扫描的文件夹...")
        self.path_edit.setReadOnly(True)
        self.path_edit.setMinimumHeight(44)
        self.path_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                color: {COLORS['text']};
            }}
        """)
        input_layout.addWidget(self.path_edit, 1)
        
        self.btn_browse = QPushButton("📁 选择文件夹")
        self.btn_browse.setMinimumHeight(44)
        self.btn_browse.setMinimumWidth(130)
        self.btn_browse.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                color: {COLORS['text']};
            }}
            QPushButton:hover {{
                border-color: {COLORS['primary']};
                color: {COLORS['primary']};
            }}
        """)
        self.btn_browse.clicked.connect(self._browse_folder)
        input_layout.addWidget(self.btn_browse)
        
        self.btn_start = QPushButton("🔒 开始解密")
        self.btn_start.setMinimumHeight(44)
        self.btn_start.setMinimumWidth(130)
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: bold;
                color: white;
            }}
            QPushButton:hover {{
                background-color: #4096ff;
            }}
            QPushButton:pressed {{
                background-color: #0958d9;
            }}
            QPushButton:disabled {{
                background-color: #91caff;
            }}
        """)
        self.btn_start.clicked.connect(self._start_decrypt)
        input_layout.addWidget(self.btn_start)
        
        card_layout.addLayout(input_layout)
        layout.addWidget(card)
    
    def _create_pdf_list_card(self, layout: QVBoxLayout):
        """创建PDF列表卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 12px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)
        
        # 标题
        self.list_title = QLabel("待解密PDF (0)")
        self.list_title.setFont(QFont("Microsoft YaHei", 13, QFont.Bold))
        self.list_title.setStyleSheet(f"color: {COLORS['text']};")
        card_layout.addWidget(self.list_title)
        
        # PDF列表
        self.pdf_list = QListWidget()
        self.pdf_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background-color: transparent;
                border-bottom: 1px solid {COLORS['border']};
                padding: 0;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary_light']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        card_layout.addWidget(self.pdf_list, 1)
        
        layout.addWidget(card, 1)
    
    def _create_stats_bar(self, layout: QVBoxLayout):
        """创建底部统计栏"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(20, 12, 20, 12)
        stats_layout.setSpacing(32)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['border']};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                border-radius: 4px;
            }}
        """)
        stats_layout.addWidget(self.progress_bar, 1)
        
        # 统计数据
        self.lbl_success = self._create_stat_item("✅", "0", "已成功", COLORS['success'])
        self.lbl_no_password = self._create_stat_item("🔒", "0", "无需处理", COLORS['primary'])
        self.lbl_failed = self._create_stat_item("❌", "0", "失败", COLORS['error'])
        
        stats_layout.addWidget(self.lbl_success)
        stats_layout.addWidget(self.lbl_no_password)
        stats_layout.addWidget(self.lbl_failed)
        
        layout.addWidget(stats_frame)
    
    def _create_stat_item(self, icon: str, value: str, label: str, color: str) -> QWidget:
        """创建统计项"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        layout.addWidget(icon_label)
        
        value_layout = QVBoxLayout()
        value_layout.setSpacing(2)
        
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color};")
        value_layout.addWidget(self.value_label)
        
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Microsoft YaHei", 9))
        label_widget.setStyleSheet(f"color: {COLORS['text_secondary']};")
        value_layout.addWidget(label_widget)
        
        layout.addLayout(value_layout)
        
        # 保存引用以便更新
        widget.value_label = self.value_label
        
        return widget
    
    def _load_last_path(self):
        """加载上次扫描路径"""
        last_path = self.config.get_last_scan_path()
        if last_path and Path(last_path).exists():
            self.path_edit.setText(last_path)
    
    def _browse_folder(self):
        """选择文件夹"""
        last_path = self.config.get_last_scan_path()
        folder = QFileDialog.getExistingDirectory(
            self, "选择要扫描的文件夹", last_path
        )
        if folder:
            self.path_edit.setText(folder)
            self.config.set_last_scan_path(folder)
    
    def _start_decrypt(self):
        """开始解密"""
        folder_path = self.path_edit.text()
        if not folder_path:
            QMessageBox.warning(self, "提示", "请先选择要扫描的文件夹！")
            return
        
        path = Path(folder_path)
        if not path.exists():
            QMessageBox.warning(self, "提示", "选择的文件夹不存在！")
            return
        
        # 禁用按钮
        self.btn_start.setEnabled(False)
        self.btn_browse.setEnabled(False)
        self.pdf_list.clear()
        self.pdf_results.clear()
        self.progress_bar.setValue(0)
        
        # 扫描PDF文件
        pdf_files = scan_pdf_files(path)
        if not pdf_files:
            QMessageBox.information(self, "提示", "未找到任何PDF文件！")
            self.btn_start.setEnabled(True)
            self.btn_browse.setEnabled(True)
            return
        
        # 更新标题
        self.list_title.setText(f"待解密PDF ({len(pdf_files)})")
        
        # 显示所有文件
        for pdf_path in pdf_files:
            item_widget = PDFListWidgetItem(str(pdf_path), "等待处理...")
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.UserRole, str(pdf_path))
            self.pdf_list.addItem(item)
            self.pdf_list.setItemWidget(item, item_widget)
        
        self.progress_bar.setMaximum(len(pdf_files))
        
        # 启动工作线程
        passwords = self.config.get_passwords()
        self.worker = DecryptWorker(pdf_files, passwords)
        self.worker.progress.connect(self._on_progress)
        self.worker.result_ready.connect(self._on_result_ready)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()
    
    def _on_progress(self, current: int, total: int):
        """更新进度"""
        self.progress_bar.setValue(current)
    
    def _on_result_ready(self, result: PDFResult):
        """处理单个结果"""
        self.pdf_results.append(result)
        
        # 查找对应的列表项并更新
        for i in range(self.pdf_list.count()):
            item = self.pdf_list.item(i)
            if item.data(Qt.UserRole) == str(result.file_path):
                item_widget = self.pdf_list.itemWidget(item)
                if item_widget:
                    if result.status == PDFStatus.NO_PASSWORD:
                        item_widget.set_status("无密码", "🔒", COLORS['primary'])
                    elif result.status == PDFStatus.DECRYPTED:
                        item_widget.set_status("已删除密码", "✅", COLORS['success'])
                    elif result.status == PDFStatus.NEED_MANUAL:
                        item_widget.set_status("待手动处理", "❌", COLORS['error'])
                break
        
        self._update_stats()
    
    def _update_stats(self):
        """更新统计"""
        decrypted = sum(1 for r in self.pdf_results if r.status == PDFStatus.DECRYPTED)
        no_pwd = sum(1 for r in self.pdf_results if r.status == PDFStatus.NO_PASSWORD)
        need_manual = sum(1 for r in self.pdf_results if r.status == PDFStatus.NEED_MANUAL)
        
        # 更新统计标签
        for i in range(self.pdf_list.count()):
            item = self.pdf_list.item(i)
            item_widget = self.pdf_list.itemWidget(item)
            if item_widget:
                # 找到统计标签并更新
                pass
        
        # 简单的统计显示
        self.lbl_success.findChild(QLabel).text()  # 这里需要更好的方法
    
    def _on_finished(self, decrypted: int, no_password: int, need_manual: int):
        """处理完成"""
        self.btn_start.setEnabled(True)
        self.btn_browse.setEnabled(True)
        self.worker = None
        
        # 更新统计
        total = decrypted + no_password + need_manual
        self.list_title.setText(f"待解密PDF ({total})")
        
        QMessageBox.information(
            self, "完成",
            f"扫描完成！\n\n✅ 已解锁：{decrypted}\n🔒 无需处理：{no_password}\n❌ 待手动处理：{need_manual}"
        )
    
    def closeEvent(self, event):
        """关闭窗口"""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(3000)
        event.accept()


class DecryptWorker(QThread):
    """解密工作线程"""
    progress = Signal(int, int)
    result_ready = Signal(PDFResult)
    finished = Signal(int, int, int)
    
    def __init__(self, pdf_files: list, passwords: list):
        super().__init__()
        self.pdf_files = pdf_files
        self.passwords = passwords
        self._is_cancelled = False
    
    def cancel(self):
        self._is_cancelled = True
    
    def run(self):
        total = len(self.pdf_files)
        decrypted_count = 0
        no_password_count = 0
        need_manual_count = 0
        
        for i, pdf_path in enumerate(self.pdf_files):
            if self._is_cancelled:
                break
            
            result = process_single_pdf(pdf_path, self.passwords)
            self.result_ready.emit(result)
            
            if result.status == PDFStatus.DECRYPTED:
                decrypted_count += 1
            elif result.status == PDFStatus.NO_PASSWORD:
                no_password_count += 1
            elif result.status == PDFStatus.NEED_MANUAL:
                need_manual_count += 1
            
            self.progress.emit(i + 1, total)
        
        self.finished.emit(decrypted_count, no_password_count, need_manual_count)
