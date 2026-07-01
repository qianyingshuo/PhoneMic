import json
import multiprocessing
import threading
import time
from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi.testclient import TestClient
from websockets.sync.client import connect as ws_connect

from phonemic.bridge_queue import QueueEventBridge
from phonemic.server.api import (app, run_server, set_bridge, start_server,
                                stop_server)


def assert_first_msg_connect(queue):
    msg_type, text = queue.get(timeout=1)
    assert msg_type == "connect"
    assert text == None
# ---------- 测试 WebSocket 消息处理 ----------
def test_websocket_message_parsing():
    """验证 WebSocket 消息能正确解析并推送到队列"""
    bridge = QueueEventBridge(multiprocessing.Queue())
    set_bridge(bridge)
    queue = bridge.queue

    client = TestClient(app)
    # 使用 FastAPI 的 TestClient 测试 WebSocket 端点
    with client.websocket_connect("/ws") as websocket:
        assert_first_msg_connect(queue)
        # 发送 preview 消息
        websocket.send_json({"type": "preview", "text": "hello"})
        # 等待队列消息
        msg_type, text = queue.get(timeout=1)
        assert msg_type == "preview"
        assert text == "hello"

        # 发送 send 消息
        websocket.send_json({"type": "send", "text": "world"})
        msg_type, text = queue.get(timeout=1)
        assert msg_type == "send"
        assert text == "world"

def test_websocket_invalid_json():
    """无效 JSON 不应崩溃，应继续接收后续消息"""
    bridge = QueueEventBridge(multiprocessing.Queue())
    set_bridge(bridge)
    queue = bridge.queue

    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        assert_first_msg_connect(queue)
        # 发送非法 JSON
        websocket.send_text("this is not json")
        # 再发送合法消息
        websocket.send_json({"type": "preview", "text": "after bad"})

        msg_type, text = queue.get(timeout=1)
        assert msg_type == "preview"
        assert text == "after bad"

def test_connection_lifecycle():
    """测试连接/断开事件是否正确推送"""
    bridge = QueueEventBridge(multiprocessing.Queue())
    set_bridge(bridge)
    queue = bridge.queue

    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        # 连接事件
        event, _ = queue.get(timeout=1)
        assert event == "connect"

    # 断开后应收到 disconnect 事件
    event, _ = queue.get(timeout=1)
    assert event == "disconnect"

def test_only_one_active_connection():
    """新连接应自动替换旧连接"""
    bridge = QueueEventBridge(multiprocessing.Queue())
    set_bridge(bridge)
    queue = bridge.queue

    client1 = TestClient(app)
    client2 = TestClient(app)

    ws1 = client1.websocket_connect("/ws")
    ws1.__enter__()
    # 确认第一个连接成功
    event, _ = queue.get(timeout=1)
    assert event == "connect"

    # 第二个连接
    ws2 = client2.websocket_connect("/ws")
    ws2.__enter__()
    # 应该收到旧连接的断开事件和新连接的连接事件
    events = []
    for _ in range(2):
        event, _ = queue.get(timeout=1)
        events.append(event)
    # 顺序可能为 disconnect -> connect 或 connect（新）-> disconnect（旧）
    # 但必须包含 disconnect 和 connect
    assert "disconnect" in events
    assert "connect" in events

    ws1.__exit__(None, None, None)
    ws2.__exit__(None, None, None)

# ---------- 测试 HTTP 路由 ----------
def test_get_root_returns_html():
    """GET / 应返回 HTML 响应（如果 mobile.html 存在）"""
    # 注意：如果 mobile.html 不存在，会返回 404 错误页面，测试需适配
    client = TestClient(app)
    response = client.get("/")
    # 由于测试环境可能缺少模板文件，我们只检查响应类型
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        assert "text/html" in response.headers["content-type"]
    else:
        assert "mobile.html not found" in response.text

# ---------- 集成测试：真实启动服务（可选，需要单独的线程）----------
def test_real_server_with_websocket_client():
    """启动真实 Uvicorn 服务，使用同步 WebSocket 客户端连接"""
    bridge = QueueEventBridge(multiprocessing.Queue())
    set_bridge(bridge)
    queue = bridge.queue
    host = "127.0.0.1"
    port = 38888  # 使用临时端口避免冲突

    # 在独立线程中启动服务
    def run():
        run_server(host=host, port=port, bridge=bridge)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    time.sleep(1)  # 等待服务启动

    test_msgs = [
        ["preview", "integration test"],
        ["send", "你好世界 🌍😊 日本語 漢字"],
        
        ("preview", "Hello, PhoneMic!"),
        ("preview", ""),                     # 空字符串应正常处理
        ("preview", "A" * 11000),            # 超长文本 (>10KB)
        ("preview", "🐍✨ 混合符号 ¥€$ 测试"),
        ("preview", "  前后空格  "),          # 空格保留
        ("preview", "\n\t多行文本\n第二行"),  # 转义字符保留

        # 发送消息（上屏）
        ("send", "普通发送"),
        ("send", "超长发送" + "B" * 15000),
        ("send", "表情包 😀😂😍"),
        ("send", ""),                       # 空发送，后端应忽略或按逻辑处理
        ("send", "  修剪测试  "),            # 空格原样传递
    ]

    # 使用 websockets 库连接
    with ws_connect(f"ws://{host}:{port}/ws") as ws:
        assert_first_msg_connect(queue)
        for orig_type, orig_text in test_msgs:
            ws.send(json.dumps({"type": orig_type, "text": orig_text}))
            msg_type, text = queue.get(timeout=2)
            assert msg_type == orig_type
            assert text == orig_text

    thread.join(timeout = 0.2)

    # 断开后应收到 disconnect 事件
    msg_type, _ = queue.get(timeout=2)
    assert msg_type == "disconnect"


def test_server_start_stop():
    """验证 start_server / stop_server 能正常启停且释放端口"""
    host = "127.0.0.1"
    port = 38889  # 临时端口，避免冲突
    bridge = QueueEventBridge(multiprocessing.Queue())

    # 启动服务器
    start_server(host, port, bridge)

    # 等待服务器就绪
    url = f"http://{host}:{port}/"
    timeout = 5.0
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            resp = requests.get(url, timeout=0.5)
            if resp.status_code in (200, 404):
                break
        except requests.RequestException:
            pass
        time.sleep(0.1)
    else:
        pytest.fail("Server did not start within timeout")

    # 停止服务器
    stop_server()
    # 给一点时间让端口释放
    time.sleep(0.5)

    # 验证端口已释放（连接应失败）
    with pytest.raises(requests.ConnectionError):
        requests.get(url, timeout=1.0)


def test_mobile_html_websocket_protocol_adaptation():
    """mobile.html 中的 WebSocket 客户端应当能够自适应安全与非安全连接协议"""
    from phonemic.utils.paths import get_app_root
    mobile_html_path = get_app_root() / "phonemic" / "resources" / "mobile.html"
    assert mobile_html_path.exists(), "mobile.html 模板文件必须存在"
    
    with open(mobile_html_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 断言包含自适应安全连接协议 the 逻辑
    assert "window.location.protocol === 'https:' ? 'wss:' : 'ws:'" in content


def test_mobile_html_key_mappings_redesign():
    """验证 mobile.html 中双下拉框、LocalStorage 持久化缓存以及火箭发送按钮移除的逻辑"""
    from phonemic.utils.paths import get_app_root
    mobile_html_path = get_app_root() / "phonemic" / "resources" / "mobile.html"
    assert mobile_html_path.exists(), "mobile.html 模板文件必须存在"
    
    with open(mobile_html_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 1. 检查是否定义了两个独立的下拉选择框
    assert "key-mapping-select" in content
    assert "single-key-mapping-select" in content
    
    # 2. 检查是否在 LocalStorage 中对这两个选择项进行了独立持久化
    assert "selected_key_mapping_id" in content
    assert "selected_single_key_mapping_id" in content
    
    # 3. 检查旧的 physical rocket 发送按钮 (btn-send-mapping) 是否已被完全移除
    assert "btn-send-mapping" not in content



