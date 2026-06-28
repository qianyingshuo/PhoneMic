import json
from typing import Any
import pytest
from fastapi.testclient import TestClient
from phonemic.server.api import app, set_bridge
from phonemic.bridge_interface import EventBridge
from phonemic.utils.settings_manager import SettingsManager

class MockEventBridge(EventBridge):
    def __init__(self):
        self.events = []
    def emit(self, event_type: str, payload: Any = None) -> None:
        self.events.append((event_type, payload))

@pytest.fixture
def reset_settings(tmp_path):
    SettingsManager._instance = None
    from phonemic.utils import paths
    def fake_writable_location():
        return tmp_path
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(paths, "_get_local_app_data", fake_writable_location)
        sm = SettingsManager.instance()
        # 确保 key_mappings 重新初始化
        sm.set("key_mappings", None)
        yield sm
    SettingsManager._instance = None

def test_ws_initial_sync_and_send_handling(reset_settings):
    """测试 WebSocket 建立连接时推送 key_mappings 并且接收带 key_sequence 的 send 消息"""
    bridge = MockEventBridge()
    set_bridge(bridge)
    
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        # 1. 应该先收到连接配置推送 "type": "config"
        msg_config = websocket.receive_json()
        assert msg_config["type"] == "config"
        
        # 2. 应该紧接着收到 "type": "key_mappings" 推送
        msg_mappings = websocket.receive_json()
        assert msg_mappings["type"] == "key_mappings"
        assert len(msg_mappings["data"]) == 3
        assert msg_mappings["data"][0]["id"] == "none"
        
        # 3. 发送带 key_mapping_id 和 key_sequence 的 send 消息
        websocket.send_json({
            "type": "send",
            "text": "测试数据",
            "key_mapping_id": "a90f7bdf-1b8f-4cb1-8fe7-fb8db2fa3200",
            "key_sequence": "enter"
        })
        
        # 验证 bridge 收到了转发，payload 应为包含 text 和 key_mapping_id, key_sequence 的字典
        # 我们给一小段时间让接收循环处理
        import time
        time.sleep(0.1)
        
        assert len(bridge.events) > 0
        # 找 event_type == "send"
        send_events = [e for e in bridge.events if e[0] == "send"]
        assert len(send_events) == 1
        event_type, payload = send_events[0]
        assert isinstance(payload, dict)
        assert payload["text"] == "测试数据"
        assert payload["key_mapping_id"] == "a90f7bdf-1b8f-4cb1-8fe7-fb8db2fa3200"
        assert payload["key_sequence"] == "enter"
