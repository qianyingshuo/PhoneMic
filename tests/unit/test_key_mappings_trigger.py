import pytest
from unittest.mock import MagicMock, patch
from phonemic.PhoneMic import handle_send_event

@pytest.fixture
def mock_managers():
    # Mock command_interceptor 和 key_mappings_manager
    interceptor = MagicMock()
    interceptor.process_send_text.return_value = False # 默认不匹配指令
    
    manager = MagicMock()
    # 模拟 PC 端现有的 key_mappings 列表
    manager.get_key_mapping.side_effect = lambda item_id: {
        "none": {"id": "none", "name": "无 (不追加)", "keys": ""},
        "uuid-enter": {"id": "uuid-enter", "name": "回车 (Enter)", "keys": "enter"},
    }.get(item_id)
    
    return interceptor, manager

@patch("phonemic.PhoneMic.flash_insert")
@patch("phonemic.PhoneMic.send_keys")
def test_handle_send_event_success(mock_send_keys, mock_flash_insert, mock_managers):
    """测试正常发送，成功粘贴并模拟按键"""
    interceptor, manager = mock_managers
    payload = {
        "text": "你好",
        "key_mapping_id": "uuid-enter",
        "key_sequence": "enter"
    }
    
    handle_send_event(payload, interceptor, manager)
    
    mock_flash_insert.assert_called_once_with("你好")
    mock_send_keys.assert_called_once_with("enter")

@patch("phonemic.PhoneMic.flash_insert")
@patch("phonemic.PhoneMic.send_keys")
def test_handle_send_event_none_mapping(mock_send_keys, mock_flash_insert, mock_managers):
    """测试不追加任何按键时"""
    interceptor, manager = mock_managers
    payload = {
        "text": "你好",
        "key_mapping_id": "none",
        "key_sequence": ""
    }
    
    handle_send_event(payload, interceptor, manager)
    
    mock_flash_insert.assert_called_once_with("你好")
    mock_send_keys.assert_not_called()

@patch("phonemic.PhoneMic.flash_insert")
@patch("phonemic.PhoneMic.send_keys")
def test_handle_send_event_warning_fallback(mock_send_keys, mock_flash_insert, mock_managers):
    """测试当 ID 不存在时，安全降级（仅粘贴），且发送警告通知"""
    interceptor, manager = mock_managers
    payload = {
        "text": "失效测试",
        "key_mapping_id": "invalid-uuid",
        "key_sequence": "enter"
    }
    
    warning_callback = MagicMock()
    handle_send_event(payload, interceptor, manager, ws_warning_callback=warning_callback)
    
    mock_flash_insert.assert_called_once_with("失效测试")
    mock_send_keys.assert_not_called()
    warning_callback.assert_called_once()
    assert "已在电脑端被删除" in warning_callback.call_args[0][0]

@patch("phonemic.PhoneMic.flash_insert")
@patch("phonemic.PhoneMic.send_keys")
def test_handle_send_event_compatible_old_payload(mock_send_keys, mock_flash_insert, mock_managers):
    """测试对旧版本 payload (纯 string) 的向下兼容"""
    interceptor, manager = mock_managers
    payload = "旧版本纯文本"
    
    handle_send_event(payload, interceptor, manager)
    
    mock_flash_insert.assert_called_once_with("旧版本纯文本")
    mock_send_keys.assert_not_called()
