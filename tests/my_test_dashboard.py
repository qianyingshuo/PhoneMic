#!/usr/bin/env python3
# test_dashboard_manual.py
import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from phonemic.gui.dashboard import Dashboard

def main():
    app = QApplication(sys.argv)
    # 创建主界面，传入测试 IP 和端口
    window = Dashboard("192.168.1.100", 12000)
    window.show()

    # 模拟连接状态变化：3秒后变为“已连接”，再过3秒变回“未连接”
    def switch_to_connected():
        window.update_connection_status(True)
        print("状态切换为：已连接")

    def switch_to_disconnected():
        window.update_connection_status(False)
        print("状态切换为：未连接")

    QTimer.singleShot(3000, switch_to_connected)
    QTimer.singleShot(6000, switch_to_disconnected)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()