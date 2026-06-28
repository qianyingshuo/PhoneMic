#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口与托盘联动逻辑单元测试
运行命令: poetry run pytest tests/test_dashboard_tray.py -v
"""

from unittest.mock import MagicMock
import pytest
from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import QApplication

from phonemic.gui.dashboard import Dashboard
from phonemic.gui.tray import SystemTray


@pytest.fixture(autouse=True)
def suppress_message_box(monkeypatch):
    """遮蔽弹窗防止阻塞测试线程"""
    monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.information", lambda *args, **kwargs: None)
    monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.warning", lambda *args, **kwargs: None)
    monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.critical", lambda *args, **kwargs: None)


@pytest.fixture(scope="session")
def qapp():
    """复用或初始化 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_minimize_hide(qapp, qtbot):
    """测试主窗口最小化后彻底隐藏并重置状态标志"""
    dashboard = Dashboard("127.0.0.1", 12000)
    qtbot.addWidget(dashboard)
    dashboard.show()

    # 模拟触发最小化动作
    dashboard.showMinimized()

    # 未修改前，此断言必失败（因为窗口未调用 hide，只处于 minimized 状态）
    assert dashboard.isHidden() is True
    # 且其 windowState 状态应该被重置为正常
    assert dashboard.windowState() == Qt.WindowNoState


def test_close_intercept_to_hide(qapp, qtbot):
    """测试主窗口关闭动作被拦截并转换为隐藏至托盘"""
    dashboard = Dashboard("127.0.0.1", 12000)
    qtbot.addWidget(dashboard)
    dashboard.show()

    # 模拟用户点击 (X) 发送 close 请求
    closed = dashboard.close()

    # 未修改前，close() 会返回 True（窗口正常关闭被接受）
    # 我们希望拦截后，close() 返回 False (即事件被 ignore)，但窗口进入隐藏状态
    assert closed is False
    assert dashboard.isHidden() is True
    assert not getattr(dashboard, "_force_quit", False)


def test_tray_force_quit(qapp, qtbot, monkeypatch):
    """测试托盘右键退出能够置为强制退出并安全终止程序"""
    # Mock QApplication.quit 以防测试直接终止 pytest 进程
    mock_quit = MagicMock()
    monkeypatch.setattr(QApplication, "quit", mock_quit)

    dashboard = Dashboard("127.0.0.1", 12000)
    qtbot.addWidget(dashboard)
    dashboard.show()

    tray = SystemTray(dashboard, "")
    
    # 未修改前，tray.quit_application 并不存在，调用必报错报错
    tray.quit_application()

    assert getattr(dashboard, "_force_quit", False) is True
    mock_quit.assert_called_once()

    # 在 _force_quit = True 的情况下，调用 close() 应被接受，返回 True
    closed = dashboard.close()
    assert closed is True
