import uuid
from typing import List, Optional
from phonemic.utils.settings_manager import SettingsManager
from phonemic.gui.keyboard import validate_key_sequence

DEFAULT_MAPPINGS = [
    {"id": "none", "name": "无 (不追加)", "keys": ""},
    {"id": "a90f7bdf-1b8f-4cb1-8fe7-fb8db2fa3200", "name": "回车 (Enter)", "keys": "enter"},
    {"id": "cb1c7df0-20cf-4688-bc1c-a96d2ff0fa01", "name": "制表符 (Tab)", "keys": "tab"}
]

class KeyMappingsManager:
    """按键映射配置管理器，维护 settings.json 中的 key_mappings 列表"""
    
    def __init__(self) -> None:
        self._settings_manager = SettingsManager.instance()
        self._init_defaults()

    def _init_defaults(self) -> None:
        """如果 settings 中不存在 key_mappings，则注入默认值"""
        mappings = self._settings_manager.get("key_mappings")
        if mappings is None:
            self._settings_manager.set("key_mappings", DEFAULT_MAPPINGS.copy())

    def get_key_mappings(self) -> List[dict]:
        """获取完整的按键映射列表"""
        mappings = self._settings_manager.get("key_mappings")
        if mappings is None:
            return DEFAULT_MAPPINGS.copy()
        return mappings

    def get_key_mapping(self, item_id: str) -> Optional[dict]:
        """根据 ID 获取单个按键映射"""
        mappings = self.get_key_mappings()
        for item in mappings:
            if item["id"] == item_id:
                return item
        return None

    def add_key_mapping(self, name: str, keys: str) -> dict:
        """添加一个新的按键映射"""
        name = name.strip()
        keys = keys.strip()
        
        # 1. 名字长度校验 (1-12)
        if not name or len(name) > 12:
            raise ValueError("名称长度必须在 1-12 字符之间")
            
        # 2. 名字重名校验
        mappings = self.get_key_mappings()
        for item in mappings:
            if item["name"] == name:
                raise ValueError("名称已存在")
                
        # 3. 按键合法性校验
        ok, err = validate_key_sequence(keys)
        if not ok:
            raise ValueError(f"按键序列无效: {err}")
            
        # 4. 创建并保存
        new_item = {
            "id": str(uuid.uuid4()),
            "name": name,
            "keys": keys
        }
        
        updated_mappings = list(mappings)
        updated_mappings.append(new_item)
        self._settings_manager.set("key_mappings", updated_mappings)
        return new_item

    def update_key_mapping(self, item_id: str, name: str, keys: str) -> dict:
        """更新现有的按键映射"""
        if item_id == "none":
            raise ValueError("默认项不可修改")
            
        name = name.strip()
        keys = keys.strip()
        
        # 1. 名字长度校验
        if not name or len(name) > 12:
            raise ValueError("名称长度必须在 1-12 字符之间")
            
        # 2. 重名校验 (排除自身)
        mappings = self.get_key_mappings()
        target_item = None
        for item in mappings:
            if item["id"] == item_id:
                target_item = item
            elif item["name"] == name:
                raise ValueError("名称已存在")
                
        if not target_item:
            raise ValueError("未找到目标按键映射项")
            
        # 3. 按键合法性校验
        ok, err = validate_key_sequence(keys)
        if not ok:
            raise ValueError(f"按键序列无效: {err}")
            
        # 4. 更新并保存
        updated_mappings = []
        for item in mappings:
            if item["id"] == item_id:
                updated_item = {
                    "id": item_id,
                    "name": name,
                    "keys": keys
                }
                updated_mappings.append(updated_item)
            else:
                updated_mappings.append(item)
                
        self._settings_manager.set("key_mappings", updated_mappings)
        return {
            "id": item_id,
            "name": name,
            "keys": keys
        }

    def delete_key_mapping(self, item_id: str) -> bool:
        """根据 ID 删除一个自定义按键映射"""
        if item_id == "none":
            raise ValueError("默认无动作不可删除")
            
        mappings = self.get_key_mappings()
        target_exists = False
        updated_mappings = []
        for item in mappings:
            if item["id"] == item_id:
                target_exists = True
            else:
                updated_mappings.append(item)
                
        if not target_exists:
            return False
            
        self._settings_manager.set("key_mappings", updated_mappings)
        return True
