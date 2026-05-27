# tests/test_bridge.py
"""测试事件桥接模块：QueueEventBridge 和 QtEventBridge"""

import multiprocessing
import sys

import pytest
from PySide6.QtCore import QCoreApplication

from phonemic.bridge_queue import QueueEventBridge
from phonemic.bridge_qt import QtEventBridge


class TestQueueEventBridge:
    """测试基于 multiprocessing.Queue 的桥接实现"""

    def test_emit_puts_event_into_queue(self):
        """验证 emit 方法将 (event_type, payload) 正确放入队列"""
        queue = multiprocessing.Queue()
        bridge = QueueEventBridge(queue)

        bridge.emit("test_event", {"key": "value"})

        # 从队列中取出并验证
        event_type, payload = queue.get(timeout=1)
        assert event_type == "test_event"
        assert payload == {"key": "value"}

    def test_emit_multiple_events_order(self):
        """验证多个事件按顺序放入队列"""
        queue = multiprocessing.Queue()
        bridge = QueueEventBridge(queue)

        bridge.emit("first", 1)
        bridge.emit("second", 2)

        assert queue.get(timeout=1) == ("first", 1)
        assert queue.get(timeout=1) == ("second", 2)

    def test_emit_payload_none(self):
        """验证 payload 为 None 时也能正常工作"""
        queue = multiprocessing.Queue()
        bridge = QueueEventBridge(queue)

        bridge.emit("connect", None)
        event_type, payload = queue.get(timeout=1)
        assert event_type == "connect"
        assert payload is None


class TestQtEventBridge:
    """测试基于 Qt 信号/槽的桥接实现（需要 QApplication）"""

    @pytest.fixture(autouse=True)
    def qt_app(self, qapp):
        """pytest-qt 提供的 qapp fixture 会自动创建 QApplication，此处仅确保存在"""
        # qapp 已经是一个 QApplication 实例，无需额外操作
        yield qapp

    def test_emit_triggers_signal(self, qtbot):
        """验证 emit 方法发射 event_signal，并且槽函数被正确调用"""
        bridge = QtEventBridge()
        received = []

        def slot(event_type, payload):
            received.append((event_type, payload))

        # 连接信号到槽
        bridge.event_signal.connect(slot)

        # 发射信号
        bridge.emit("preview", "hello")

        # 使用 qtbot 等待信号处理（保证异步事件被处理）
        qtbot.wait(10)

        assert len(received) == 1
        assert received[0] == ("preview", "hello")

    def test_emit_multiple_signals(self, qtbot):
        """验证多次 emit 都能触发信号"""
        bridge = QtEventBridge()
        received = []

        def slot(event_type, payload):
            received.append((event_type, payload))

        bridge.event_signal.connect(slot)

        bridge.emit("first", 100)
        bridge.emit("second", 200)
        qtbot.wait(10)

        assert received == [("first", 100), ("second", 200)]

    def test_emit_with_none_payload(self, qtbot):
        """验证 payload 为 None 时信号正常发射"""
        bridge = QtEventBridge()
        received = []

        def slot(event_type, payload):
            received.append((event_type, payload))

        bridge.event_signal.connect(slot)

        bridge.emit("disconnect", None)
        qtbot.wait(10)

        assert len(received) == 1
        assert received[0] == ("disconnect", None)

    def test_signal_can_be_disconnected(self, qtbot):
        """验证信号可以正常断开连接"""
        bridge = QtEventBridge()
        received = []

        def slot(event_type, payload):
            received.append((event_type, payload))

        bridge.event_signal.connect(slot)
        bridge.emit("first", 1)
        qtbot.wait(10)
        assert len(received) == 1

        # 断开连接
        bridge.event_signal.disconnect(slot)
        bridge.emit("second", 2)
        qtbot.wait(10)
        # 仍然只有之前的一条记录
        assert len(received) == 1


# 如果直接运行此文件（不使用 pytest），提供简单的调试入口
if __name__ == "__main__":
    # 需要手动创建 QApplication 实例以测试 Qt 部分
    app = QCoreApplication(sys.argv)
    pytest.main([__file__, "-v", "--tb=short"])