import logging
import multiprocessing
import sys
import threading
import time
import traceback
from pathlib import Path
from typing import Any

# 配置本地日志目录
LOG_DIR = Path.home() / ".phonemic"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"
CRASH_LOG = LOG_DIR / "crash.log"

# 配置日志，同时输出到文件和终端
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# 配置崩溃捕获
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.critical("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))
    
    try:
        with open(CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n=== Crash at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            f.write(error_msg)
    except Exception as e:
        print(f"Failed to write crash log: {e}", file=sys.stderr)
        
    try:
        # 延迟导入，防止因为 PySide6 导入错误导致弹窗失败
        from PySide6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        QMessageBox.critical(
            None, 
            "PhoneMic 崩溃", 
            f"程序在运行期间发生未捕获异常而崩溃。\n\n"
            f"日志记录至: {LOG_FILE}\n"
            f"崩溃堆栈记录至: {CRASH_LOG}\n\n"
            f"错误信息: {exc_value}"
        )
    except Exception as dialog_err:
        logger.error(f"Failed to show QMessageBox error dialog: {dialog_err}")
        
    sys.exit(1)

sys.excepthook = handle_exception

# 延迟/安全导入第三方模块
import requests
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox

from phonemic.bridge_qt import QtEventBridge
from phonemic.bridge_queue import QueueEventBridge
from phonemic.gui.dashboard import Dashboard
from phonemic.gui.hud import HudWindow, get_hud_signals
from phonemic.gui.ip_selector import IpSelector
from phonemic.gui.keyboard import flash_insert, send_keys
from phonemic.gui.tray import SystemTray
from phonemic.server.api import start_server, stop_server
from phonemic.utils.network import get_all_lan_ips, find_free_port
from phonemic.utils.paths import get_res_path
from phonemic.utils.i18n import I18n
from phonemic.utils.command_processor import CommandInterceptor
from phonemic.utils.key_mappings_manager import KeyMappingsManager

class QueueSignals(QObject):
    event_signal = Signal(str, object)

    def queue_monitor(self, queue: multiprocessing.Queue):
        while True:
            try:
                event, data = queue.get()
                self.event_signal.emit(event, data)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
    def start_thread_pool_queue(self, queue: multiprocessing.Queue):        
        self.monitor_thread = threading.Thread(
            target=self.queue_monitor,
            args=(queue),
            daemon=True
        )
        self.monitor_thread.start()

def handle_send_event(payload: Any, command_interceptor, key_mappings_manager, ws_warning_callback=None):
    """
    处理后端发来的 send 事件负载。
    如果匹配命令则执行命令；
    否则粘贴文本并触发追加的按键序列。
    如果 ID 非法或失效，执行降级且不触发按键模拟，并可通过 callback 触发警告通知。
    """
    # payload 可以是字符串（旧协议兼容）或者字典 {"text": text, "key_mapping_id": key_mapping_id, "key_sequence": key_sequence}
    if isinstance(payload, dict):
        text = payload.get("text", "")
        key_mapping_id = payload.get("key_mapping_id", "none")
        key_sequence = payload.get("key_sequence", "")
    else:
        text = str(payload)
        key_mapping_id = "none"
        key_sequence = ""

    # 先匹配命令，若匹配则返回，不进行粘贴及按键追加
    if command_interceptor.process_send_text(text):
        return

    # 进行 ID 校验
    should_send = True
    if key_mapping_id != "none":
        # 查找 ID
        mapping = key_mappings_manager.get_key_mapping(key_mapping_id)
        if not mapping:
            # 降级：不触发按键
            should_send = False
            # 发送警告通知
            if ws_warning_callback:
                ws_warning_callback("按键映射已在电脑端被删除，已自动重置为“无 (不追加)”")

    # 执行粘贴
    flash_insert(text)

    # 模拟按键序列
    if should_send and key_sequence:
        send_keys(key_sequence)

def wait_for_server(host: str, port: int, timeout: float = 5.0) -> bool:
    """等待服务器就绪，返回是否成功"""
    url = f"http://{host}:{port}/"
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(url, timeout=0.5)
            if resp.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(0.2)
    return False

def main():
    # 尝试获取已有的 QApplication 实例，在pytest-qt的情况下，QApplication通常已经初始化实例
    app = QApplication.instance()
    if app is None:
        # 如果还没有实例，则创建一个新的 (生产环境运行时的正常情况)
        app = QApplication(sys.argv)
    #app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(get_res_path("favicon.ico")))

    i18n = I18n.instance()

    # 1. 获取IP候选
    candidates = get_all_lan_ips()
    if not candidates:
        QMessageBox.critical(None, "错误", "未检测到可用局域网IP，程序将退出。")
        sys.exit(1)
    elif len(candidates) == 1:
        selected_ip = candidates[0].ip
    else:
        selector = IpSelector(candidates)
        if selector.exec() != IpSelector.Accepted:
            sys.exit(0)
        selected_ip = selector.get_selected_ip()
        if not selected_ip:
            sys.exit(0)

    logger.info(f"Selected IP: {selected_ip}")

    # 2. 查找可用端口并启动后端
    actual_port = find_free_port(start_port = 12000)
    if actual_port is None:
        QMessageBox.critical(None, "错误", "未找到可用端口（从 12000 开始），程序将退出。")
        sys.exit(1)
    
    logger.info(f"Using port: {actual_port}")

    # 3. 准备后端通信
    use_queue = False
    if use_queue:
        bridge = QueueEventBridge(multiprocessing.Queue())
    else:
        bridge = QtEventBridge()

    # 启动服务器线程
    start_server(selected_ip, actual_port, bridge)

    if not wait_for_server(selected_ip, actual_port):
        QMessageBox.critical(None, "错误", f"服务器启动超时，请检查端口 {actual_port} 是否可用。")
        sys.exit(1)

    # 4. 创建主界面并连接信号
    dashboard = Dashboard(selected_ip, actual_port)
    
    hud = HudWindow()
    dashboard.show()

    # 5. 初始化系统托盘
    tray = SystemTray(dashboard, get_res_path("favicon.ico"))   # 确保路径正确

    command_interceptor = CommandInterceptor()
    key_mappings_manager = KeyMappingsManager()
    # 6. 启动队列监控
    def on_backend_event(event_type: str, payload: Any):
        if event_type == "preview":
            hud.on_preview_text(payload)   # 需提前获取 hud 实例
        elif event_type == "send":
            from phonemic.server.api import send_warning_notification
            handle_send_event(payload, command_interceptor, key_mappings_manager, ws_warning_callback=send_warning_notification)
            hud.hide()
        elif event_type == "connect":
            dashboard.update_connection_status(True)
            tray.update_connection_status(True)
        elif event_type == "disconnect":
            dashboard.update_connection_status(False)
            tray.update_connection_status(False)
        else:
            logger.warning(f"Unknown event: {event_type}")
    if (use_queue):
        queue_signals = QueueSignals()
        queue_signals.start_thread_pool_queue(bridge.queue)
        queue_signals.event_signal.connect(on_backend_event)
    else:
        bridge.event_signal.connect(on_backend_event)
        pass

    # 5. 退出清理
    def on_quit():
        logger.info("Shutting down...")
        stop_server()
    app.aboutToQuit.connect(on_quit)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()