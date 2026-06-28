import pytest
from unittest.mock import patch, MagicMock
from phonemic.utils.settings_manager import SettingsManager
from phonemic.utils.key_mappings_manager import KeyMappingsManager

@pytest.fixture
def reset_settings(tmp_path):
    """临时重置 SettingsManager 并配置测试用的路径"""
    SettingsManager._instance = None
    mock_app_config = tmp_path / "PhoneMic/config"
    mock_app_config.mkdir(parents=True, exist_ok=True)
    
    from phonemic.utils import paths
    def fake_writable_location():
        return tmp_path

    with patch("phonemic.utils.paths._get_local_app_data", fake_writable_location):
        sm = SettingsManager.instance()
        # 清空/重置 key_mappings 保证测试的干净
        sm.set("key_mappings", None)
        yield sm
    SettingsManager._instance = None

def test_default_key_mappings_injection(reset_settings):
    """测试当 key_mappings 未配置时，自动注入默认映射项"""
    manager = KeyMappingsManager()
    mappings = manager.get_key_mappings()
    assert len(mappings) == 3
    assert mappings[0]["id"] == "none"
    assert mappings[0]["name"] == "无 (不追加)"
    assert mappings[0]["keys"] == ""
    
    assert mappings[1]["name"] == "回车 (Enter)"
    assert mappings[1]["keys"] == "enter"
    
    assert mappings[2]["name"] == "制表符 (Tab)"
    assert mappings[2]["keys"] == "tab"

def test_add_key_mapping_success(reset_settings):
    """测试成功添加按键映射"""
    manager = KeyMappingsManager()
    new_item = manager.add_key_mapping("测试映射", "ctrl+alt+t")
    
    assert new_item["id"] != "none"
    assert new_item["name"] == "测试映射"
    assert new_item["keys"] == "ctrl+alt+t"
    
    # 验证确实保存到了 mappings
    mappings = manager.get_key_mappings()
    assert len(mappings) == 4
    assert mappings[3]["name"] == "测试映射"

def test_add_key_mapping_validation(reset_settings):
    """测试添加按键映射时的参数验证"""
    manager = KeyMappingsManager()
    
    # 1. 名字长度限制 (1-12)
    with pytest.raises(ValueError, match="名称长度必须在 1-12 字符之间"):
        manager.add_key_mapping("", "enter")
    with pytest.raises(ValueError, match="名称长度必须在 1-12 字符之间"):
        manager.add_key_mapping("这是一个超过十二个字符的名字了啊", "enter")
        
    # 2. 名字重名校验
    with pytest.raises(ValueError, match="名称已存在"):
        manager.add_key_mapping("回车 (Enter)", "space")
        
    # 3. 按键序列合法性校验
    with pytest.raises(ValueError, match="按键序列"):
        manager.add_key_mapping("合法名称", "invalid_key_name_123")

def test_update_key_mapping_success(reset_settings):
    """测试成功更新按键映射"""
    manager = KeyMappingsManager()
    item = manager.add_key_mapping("更新前", "enter")
    
    updated = manager.update_key_mapping(item["id"], "更新后", "space")
    assert updated["name"] == "更新后"
    assert updated["keys"] == "space"
    
    # 验证已存入
    retrieved = manager.get_key_mapping(item["id"])
    assert retrieved["name"] == "更新后"
    assert retrieved["keys"] == "space"

def test_update_key_mapping_validation(reset_settings):
    """测试更新时的参数校验"""
    manager = KeyMappingsManager()
    item1 = manager.add_key_mapping("项1", "enter")
    item2 = manager.add_key_mapping("项2", "space")
    
    # 不能更新 "none" 项
    with pytest.raises(ValueError, match="默认项不可修改"):
        manager.update_key_mapping("none", "修改默认", "enter")
        
    # 名字长度限制
    with pytest.raises(ValueError, match="名称长度必须在 1-12 字符之间"):
        manager.update_key_mapping(item1["id"], "", "space")
        
    # 重名冲突
    with pytest.raises(ValueError, match="名称已存在"):
        manager.update_key_mapping(item1["id"], "项2", "space")
        
    # 非法按键
    with pytest.raises(ValueError, match="按键序列"):
        manager.update_key_mapping(item1["id"], "新项", "invalid_key")

def test_delete_key_mapping(reset_settings):
    """测试删除按键映射"""
    manager = KeyMappingsManager()
    item = manager.add_key_mapping("待删除", "enter")
    
    # 不能删除 "none"
    with pytest.raises(ValueError, match="默认无动作不可删除"):
        manager.delete_key_mapping("none")
        
    # 删除自定义项
    deleted = manager.delete_key_mapping(item["id"])
    assert deleted is True
    
    # 验证已删除
    assert manager.get_key_mapping(item["id"]) is None
