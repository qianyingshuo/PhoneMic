from typing import Callable
import os
import subprocess
import sys

import qrcode
from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QFrame, QMenuBar, QMessageBox
)

from phonemic.gui.settings_dialog import SettingsDialog
from phonemic.gui.commands_dialog import CommandsDialog
from phonemic.utils.paths import get_app_root, get_build_info
from phonemic.utils.i18n import I18n

class Dashboard(QMainWindow):
    def __init__(self, ip: str, port: int, parent=None):
        super().__init__(parent)
        self.i18n = I18n.instance()
        self.setWindowTitle(self.i18n.tr("dashboard.title") + " (Dev)")
        self.setFixedSize(400, 450)
        self.setWindowFlags(self.windowFlags() & (~Qt.WindowMaximizeButtonHint) | Qt.WindowCloseButtonHint)
        self._force_quit = False
        self._setup_ui(ip, port)
        self._setup_menu()

    def _setup_ui(self, ip, port) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ----- 二维码（修复倾斜问题）-----
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignCenter)

        qr_url = f"http://{ip}:{port}"
        pil_img = qrcode.make(qr_url)
        pil_img = pil_img.resize((250, 250))
        qimage = ImageQt(pil_img)
        pixmap = QPixmap.fromImage(qimage)
        qr_label.setPixmap(pixmap)
        layout.addWidget(qr_label)

        # ----- 分隔线 -----
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        ip_label = QLabel(self.i18n.tr("dashboard.ip_label") + f": {ip}:{port}")
        ip_label.setAlignment(Qt.AlignCenter)
        ip_label.setWordWrap(True)
        layout.addWidget(ip_label)

        info_label = QLabel(self.i18n.tr("dashboard.info"))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: blue; font-size: 10px;")
        layout.addWidget(info_label)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.update_connection_status(False)
        layout.addWidget(self.status_label)
        layout.addStretch()

    def _setup_menu(self):
        menubar = self.menuBar()
        # 使用原生菜单栏，避免占用额外空间
        menubar.setNativeMenuBar(False)  # 确保在 Windows 上显示在窗口内

        settings_menu = menubar.addMenu(self.i18n.tr("dashboard.menu_settings"))
        help_menu = menubar.addMenu(self.i18n.tr("dashboard.menu_help"))

        # 设置动作
        settings_action = QAction(self.i18n.tr("dashboard.menu_action"), self)
        settings_action.triggered.connect(self._open_settings)
        settings_menu.addAction(settings_action)
        # 添加“工具”菜单
        commands_action = QAction(self.i18n.tr("dashboard.menu_command"), self)
        commands_action.triggered.connect(self._open_commands_dialog)
        settings_menu.addAction(commands_action)

        help_action = QAction(self.i18n.tr("dashboard.menu_help_guide"), self)
        help_action.triggered.connect(self.open_user_guide)
        help_menu.addAction(help_action)

        # 关于动作
        about_action = QAction(self.i18n.tr("dashboard.menu_about"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()
        
    def _open_commands_dialog(self):
        dlg = CommandsDialog(self)
        dlg.exec_()
        
    def show_about(self):
        version, commit, _ = get_build_info()
        content = self.i18n.tr("about.content", version=version, commit=commit)
        QMessageBox.about(self, self.i18n.tr("about.title"), content)

    # ====================== 新增：打开帮助文档函数 ======================
    def open_user_guide(self):        
        guide_path = get_app_root() / "USER_GUIDE.md"
        
        if guide_path.exists():
            # 用系统默认程序打开md文件
            if sys.platform == "win32":
                subprocess.Popen(["notepad.exe", str(guide_path)], 
                                 shell=False, 
                                 creationflags=subprocess.CREATE_NO_WINDOW)
                #os.startfile(str(guide_path))
            else:
                subprocess.run(["open", str(guide_path)] if sys.platform == "darwin" else ["xdg-open", str(guide_path)])
        else:
            QMessageBox.warning(self, self.i18n.tr("help.warning"), 
                              self.i18n.tr("help.file_not_found"))
    # ==================================================================

    def update_connection_status(self, connected: bool) -> None:
        self.connected = connected
        if connected:
            self.status_label.setText('<span style="color:green;">●</span> ' + self.i18n.tr("dashboard.status_connected"))
        else:
            self.status_label.setText('<span style="color:red;">●</span> ' + self.i18n.tr("dashboard.status_disconnected"))

    def closeEvent(self, event):
        if getattr(self, "_force_quit", False):
            event.accept()
        else:
            self.hide()
            event.ignore()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                self.hide()
                self.setWindowState(Qt.WindowNoState)
                event.ignore()
                return
        super().changeEvent(event)