"""
UI主窗口模块
实现主窗口 + 两个选项卡（解密/密码库）
"""

from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QLineEdit, QPushButton, 
    QListWidget, QListWidgetItem, QProgressBar, 
    QFileDialog, QMessageBox, QInputDialog, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from .config_manager import ConfigManager
from .pdf_decryptor import (
    scan_pdf_files, process_single_pdf, decrypt_with_password,
    PDFStatus, PDFResult
)


class DecryptWorker(QThread):
    """解密工作线程"""
    progress = Signal(int, int)  # 当前索引, 总数
    result_ready = Signal(PDFResult)  # 单个文件处理结果
    finished = Signal(int, int, int)  # 已解锁数, 无密码数, 待处理数
    
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


class PasswordInputDialog(QInputDialog):
    """密码输入弹窗"""
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("手动解密")
        self.setLabelText(f"文件：{file_path}\n\n请输入密码：")
        self.setTextEchoMode(QLineEdit.Password)
        self.setOkButtonText("解密")
        self.setCancelButtonText("取消")


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.pdf_results = []  # 存储处理结果
        self.worker: Optional[DecryptWorker] = None
        
        self._init_ui()
        self._load_last_path()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("No PDF Password")
        self.setMinimumSize(700, 550)
        self.resize(800, 600)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建两个选项卡
        self._create_decrypt_tab()
        self._create_password_tab()
    
    def _create_decrypt_tab(self):
        """创建解密选项卡"""
        decrypt_widget = QWidget()
        layout = QVBoxLayout(decrypt_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # 路径选择区域
        path_layout = QHBoxLayout()
        path_layout.setSpacing(8)
        
        path_label = QLabel("📂 扫描路径：")
        path_layout.addWidget(path_label)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("请选择要扫描的文件夹...")
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit, 1)
        
        self.btn_browse = QPushButton("选择文件夹")
        self.btn_browse.setFixedWidth(100)
        self.btn_browse.clicked.connect(self._browse_folder)
        path_layout.addWidget(self.btn_browse)
        
        self.btn_start = QPushButton("开始解密")
        self.btn_start.setFixedWidth(100)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QPushButton:disabled {
                background-color: #93c5fd;
            }
        """)
        self.btn_start.clicked.connect(self._start_decrypt)
        path_layout.addWidget(self.btn_start)
        
        layout.addLayout(path_layout)
        
        # 待解密PDF列表
        list_label = QLabel("待解密PDF")
        list_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(list_label)
        
        self.pdf_list = QListWidget()
        self.pdf_list.setAlternatingRowColors(True)
        self.pdf_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                alternate-background-color: #f9fafb;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e5e7eb;
            }
            QListWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
        """)
        self.pdf_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.pdf_list)
        
        # 进度条区域
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(12)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v/%m")
        progress_layout.addWidget(self.progress_bar, 1)
        
        self.lbl_stats = QLabel("✅0  ⏭0  ❌0")
        self.lbl_stats.setStyleSheet("font-size: 12px; color: #6b7280;")
        progress_layout.addWidget(self.lbl_stats)
        
        layout.addLayout(progress_layout)
        
        self.tab_widget.addTab(decrypt_widget, "解密")
    
    def _create_password_tab(self):
        """创建密码库选项卡"""
        password_widget = QWidget()
        layout = QVBoxLayout(password_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # 标题
        title_label = QLabel("密码列表（按顺序从上到下尝试）")
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        # 密码列表
        self.password_list = QListWidget()
        self.password_list.setAlternatingRowColors(True)
        self.password_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                alternate-background-color: #f9fafb;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e5e7eb;
            }
            QListWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
        """)
        layout.addWidget(self.password_list)
        
        # 添加密码区域
        add_layout = QHBoxLayout()
        add_layout.setSpacing(8)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("输入新密码...")
        self.password_edit.returnPressed.connect(self._add_password)
        add_layout.addWidget(self.password_edit, 1)
        
        self.btn_add = QPushButton("添加")
        self.btn_add.setFixedWidth(80)
        self.btn_add.clicked.connect(self._add_password)
        add_layout.addWidget(self.btn_add)
        
        self.btn_delete = QPushButton("删除选中")
        self.btn_delete.setFixedWidth(80)
        self.btn_delete.clicked.connect(self._delete_password)
        add_layout.addWidget(self.btn_delete)
        
        layout.addLayout(add_layout)
        
        # 密码数量
        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("font-size: 12px; color: #6b7280;")
        layout.addWidget(self.lbl_count)
        
        self.tab_widget.addTab(password_widget, "密码库")
        
        # 加载密码列表
        self._load_passwords()
    
    def _load_passwords(self):
        """加载密码列表到UI"""
        self.password_list.clear()
        passwords = self.config.get_passwords()
        for pwd in passwords:
            self.password_list.addItem(pwd)
        self.lbl_count.setText(f"共 {len(passwords)} 个预设密码")
    
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
        
        # 禁用按钮，清空列表
        self.btn_start.setEnabled(False)
        self.btn_browse.setEnabled(False)
        self.pdf_list.clear()
        self.pdf_results.clear()
        self.progress_bar.setValue(0)
        self.lbl_stats.setText("✅0  ⏭0  ❌0")
        
        # 扫描PDF文件
        pdf_files = scan_pdf_files(path)
        if not pdf_files:
            QMessageBox.information(self, "提示", "未找到任何PDF文件！")
            self.btn_start.setEnabled(True)
            self.btn_browse.setEnabled(True)
            return
        
        # 先显示所有文件（状态为"扫描中"）
        for pdf_path in pdf_files:
            item = QListWidgetItem(f"📄 {pdf_path.name}    ⏳ 等待处理...")
            item.setData(Qt.UserRole, str(pdf_path))
            self.pdf_list.addItem(item)
        
        self.progress_bar.setMaximum(len(pdf_files))
        
        # 获取密码列表
        passwords = self.config.get_passwords()
        
        # 启动工作线程
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
                if result.status == PDFStatus.NO_PASSWORD:
                    item.setText(f"📄 {result.file_path.name}    ⏭ 无密码")
                elif result.status == PDFStatus.DECRYPTED:
                    item.setText(f"📄 {result.file_path.name}    ✅ 已删除密码")
                elif result.status == PDFStatus.NEED_MANUAL:
                    item.setText(f"📄 {result.file_path.name}    ❌ 待手动处理")
                elif result.status == PDFStatus.ERROR:
                    item.setText(f"📄 {result.file_path.name}    ⚠️ 错误：{result.error_msg}")
                break
        
        # 更新统计
        self._update_stats()
    
    def _update_stats(self):
        """更新统计数字"""
        decrypted = sum(1 for r in self.pdf_results if r.status == PDFStatus.DECRYPTED)
        no_pwd = sum(1 for r in self.pdf_results if r.status == PDFStatus.NO_PASSWORD)
        manual = sum(1 for r in self.pdf_results if r.status == PDFStatus.NEED_MANUAL)
        self.lbl_stats.setText(f"✅{decrypted}  ⏭{no_pwd}  ❌{manual}")
    
    def _on_finished(self, decrypted: int, no_password: int, need_manual: int):
        """处理完成"""
        self.btn_start.setEnabled(True)
        self.btn_browse.setEnabled(True)
        self.worker = None
        
        total = decrypted + no_password + need_manual
        msg = f"扫描完成！\n\n✅ 已解锁：{decrypted}\n⏭ 无密码：{no_password}\n❌ 待手动处理：{need_manual}"
        QMessageBox.information(self, "完成", msg)
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """双击列表项"""
        file_path_str = item.data(Qt.UserRole)
        if not file_path_str:
            return
        
        # 检查是否是待手动处理的状态
        if "❌ 待手动处理" not in item.text():
            return
        
        # 弹出密码输入框
        dialog = PasswordInputDialog(file_path_str, self)
        if dialog.exec() == QInputDialog.Accepted:
            password = dialog.textValue()
            if password:
                success, msg = decrypt_with_password(Path(file_path_str), password)
                if success:
                    item.setText(f"📄 {Path(file_path_str).name}    ✅ 已删除密码")
                    # 更新结果
                    for r in self.pdf_results:
                        if str(r.file_path) == file_path_str:
                            r.status = PDFStatus.DECRYPTED
                            r.password_used = password
                            break
                    self._update_stats()
                    QMessageBox.information(self, "成功", "密码已成功删除！")
                else:
                    QMessageBox.warning(self, "失败", msg)
    
    def _add_password(self):
        """添加密码"""
        password = self.password_edit.text().strip()
        if not password:
            return
        
        if self.config.add_password(password):
            self.password_list.addItem(password)
            self.password_edit.clear()
            self.lbl_count.setText(f"共 {self.password_list.count()} 个预设密码")
        else:
            QMessageBox.information(self, "提示", "该密码已存在！")
    
    def _delete_password(self):
        """删除选中的密码"""
        current_item = self.password_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "提示", "请先选择要删除的密码！")
            return
        
        password = current_item.text()
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除密码 \"{password}\" 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config.remove_password(password)
            self.password_list.takeItem(self.password_list.row(current_item))
            self.lbl_count.setText(f"共 {self.password_list.count()} 个预设密码")
    
    def closeEvent(self, event):
        """关闭窗口时取消正在运行的任务"""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(3000)
        event.accept()
