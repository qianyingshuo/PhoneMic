import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtCore import Qt

from phonemic.utils.settings_manager import SettingsManager
from phonemic.utils.key_mappings_manager import KeyMappingsManager
from phonemic.gui.key_mappings_dialog import KeyMappingsDialog, KeyMappingEditDialog

@pytest.fixture(autouse=True)
def suppress_message_box(monkeypatch):
    """全局 mock 弹窗，防止测试时阻塞"""
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "critical", lambda *args, **kwargs: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)

@pytest.fixture
def reset_settings(tmp_path):
    SettingsManager._instance = None
    from phonemic.utils import paths
    def fake_writable_location():
        return tmp_path
    with patch("phonemic.utils.paths._get_local_app_data", fake_writable_location):
        sm = SettingsManager.instance()
        sm.set("key_mappings", None) # 重新初始化 key_mappings
        yield sm
    SettingsManager._instance = None

def test_dialog_loads_mappings(qtbot, reset_settings):
    """测试列表框是否加载并正确渲染了默认按键映射项"""
    dialog = KeyMappingsDialog()
    qtbot.addWidget(dialog)
    
    # 默认应该有 3 个映射项
    assert dialog.list_widget.count() == 3
    # 第一项应该是“无 (不追加)”
    assert "无 (不追加)" in dialog.list_widget.item(0).text()
    
    dialog.close()

def test_edit_dialog_validation(qtbot, reset_settings):
    """测试编辑/新增对话框的输入限制与校验"""
    # 1. 名字为空被拦截
    edit_dialog = KeyMappingEditDialog(parent=None)
    qtbot.addWidget(edit_dialog)
    
    edit_dialog.name_input.setText("")
    edit_dialog.keys_input.setText("enter")
    
    # 点击保存应该返回 rejected (被拦截)
    edit_dialog.btn_save.click()
    assert edit_dialog.result() != QDialog.Accepted

    # 2. 限制输入非法按键
    edit_dialog.name_input.setText("合法名称")
    edit_dialog.keys_input.setText("invalid_key_123")
    edit_dialog.btn_save.click()
    assert edit_dialog.result() != QDialog.Accepted

    # 3. 输入合法按键时应该能够 Accepted
    edit_dialog.name_input.setText("合法名称")
    edit_dialog.keys_input.setText("enter")
    edit_dialog.btn_save.click()
    assert edit_dialog.result() == QDialog.Accepted
    
    edit_dialog.close()

def test_add_key_mapping(qtbot, reset_settings):
    """测试在列表页中点击新增并成功添加"""
    dialog = KeyMappingsDialog()
    qtbot.addWidget(dialog)
    
    # 模拟新增对话框的输入
    def handle_edit_dialog(item_id=None):
        KeyMappingsManager().add_key_mapping("新建测试", "ctrl+alt+a")
        dialog._load_list()
        return QDialog.Accepted

    # 通过 patch 让 show_edit_dialog 能被测试控制
    with patch.object(KeyMappingsDialog, "_show_edit_dialog", side_effect=handle_edit_dialog) as mock_show:
        dialog.btn_add.click()
        mock_show.assert_called_once()
        
    assert dialog.list_widget.count() == 4
    assert "新建测试" in dialog.list_widget.item(3).text()
    dialog.close()

def test_none_item_actions_disabled(qtbot, reset_settings):
    """测试当选中'无 (不追加)'项时，修改和删除按钮是否被置灰"""
    dialog = KeyMappingsDialog()
    qtbot.addWidget(dialog)
    
    # 选中第一项 (none)
    dialog.list_widget.setCurrentRow(0)
    
    assert dialog.btn_edit.isEnabled() is False
    assert dialog.btn_delete.isEnabled() is False
    
    # 新增一项并选中它，看按钮是否恢复可用
    KeyMappingsManager().add_key_mapping("自定义1", "enter")
    dialog._load_list() # 重新加载 UI
    
    # 选中新加的第 4 项
    dialog.list_widget.setCurrentRow(3)
    assert dialog.btn_edit.isEnabled() is True
    assert dialog.btn_delete.isEnabled() is True
    
    dialog.close()
