from PySide6.QtCore import QObject, Signal

class BridgeSignals(QObject):
    """跨线程通信桥接信号（全局单例）"""
    preview_signal = Signal(str)
    send_signal = Signal(str)
    client_connected = Signal()
    client_disconnected = Signal()

# 全局单例（将在 QApplication 创建后立刻实例化，但模块导入时 QApplication 可能还不存在）
# 因此我们不在此处直接实例化，而是提供一个函数 get_bridge() 延迟初始化。
_bridge = None

def get_bridge():
    global _bridge
    if _bridge is None:
        _bridge = BridgeSignals()
    return _bridge