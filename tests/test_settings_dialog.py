"""
SettingsDialog 单元测试
运行: pytest tests/test_settings_dialog.py -v
"""

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication

from phonemic.gui.settings_dialog import SettingsDialog
from phonemic.utils.i18n import I18n
from phonemic.utils.settings_manager import SettingsManager

@pytest.fixture(autouse=True)
def suppress_message_box(monkeypatch):
    monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.information", lambda *args, **kwargs: None)
    monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.warning", lambda *args, **kwargs: None)
    monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.critical", lambda *args, **kwargs: None)

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_config_path(tmp_path):
    """临时替换配置目录"""
    mock_app_config = tmp_path / "PhoneMic"
    mock_app_config.mkdir()

    def mock_writable_location(location):
        if location == QStandardPaths.AppConfigLocation:
            return str(tmp_path)
        return QStandardPaths.writableLocation(location)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(QStandardPaths, "writableLocation", mock_writable_location)
        yield mock_app_config


@pytest.fixture
def reset_singleton():
    SettingsManager._instance = None
    yield
    SettingsManager._instance = None


@pytest.fixture
def settings_manager(mock_config_path, reset_singleton):
    sm = SettingsManager.instance()
    sm.set("hud_timeout_sec", 5)
    sm.set("hud_font_size", 14)
    sm.set("hud_escape_enabled", True)
    sm.set("mobile_max_records", 10)
    sm.set("language", "zh_CN")
    return sm
@pytest.fixture
def mock_languages(monkeypatch):
    monkeypatch.setattr(
        "phonemic.utils.i18n.get_available_languages",
        lambda: [("en_US", "English (en_US)"), ("zh_CN", "简体中文 (zh_CN)")]
    )

def test_language_combo_populated(qtbot, mock_languages, settings_manager):
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    # 假设 dialog 中有一个 lang_combo
    assert dialog.lang_combo.count() == 2
    assert dialog.lang_combo.itemData(0) == "en_US"
    assert dialog.lang_combo.itemText(0) == "English (en_US)"

def test_language_combo_empty(mocker, qtbot, settings_manager):
    mocker.patch("phonemic.utils.i18n.get_available_languages", return_value=[])
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    assert dialog.lang_combo.count() == 0

def test_dialog_loads_current_settings(qtbot, settings_manager, mock_languages):
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    assert dialog.timeout_spin.value() == 5
    assert dialog.font_combo.currentText() == "14"
    assert dialog.max_records_spin.value() == 10
    assert dialog.lang_combo.currentText() == "简体中文 (zh_CN)"

    dialog.close()


def test_dialog_saves_settings_on_accept(qtbot, settings_manager):
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    dialog.timeout_spin.setValue(10)
    dialog.max_records_spin.setValue(20)

    # 直接调用 accept 触发保存
    dialog.accept()

    assert settings_manager.get("hud_timeout_sec") == 10
    assert settings_manager.get("mobile_max_records") == 20

    assert not dialog.isVisible()


def test_dialog_cancel_does_not_save(qtbot, settings_manager):
    original_timeout = settings_manager.get("hud_timeout_sec")
    original_font = settings_manager.get("hud_font_size")
    original_records = settings_manager.get("mobile_max_records")
    original_lang = settings_manager.get("language")

    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    dialog.timeout_spin.setValue(99)
    dialog.set_combo_index(dialog.font_combo, 20);
    dialog.max_records_spin.setValue(30)
    dialog.set_combo_index(dialog.lang_combo, "en_US");

    # 直接调用 reject 取消
    dialog.reject()

    assert settings_manager.get("hud_timeout_sec") == original_timeout
    assert settings_manager.get("hud_font_size") == original_font
    assert settings_manager.get("mobile_max_records") == original_records
    assert settings_manager.get("language") == original_lang

    assert not dialog.isVisible()


def test_font_size_conversion(qtbot, settings_manager):
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    dialog.set_combo_index(dialog.font_combo, 18);
    dialog._save_settings()
    assert settings_manager.get("hud_font_size") == 18

    dialog.set_combo_index(dialog.font_combo, "system");
    dialog._save_settings()
    assert settings_manager.get("hud_font_size") == "system"

    dialog.close()


def test_language_conversion(qtbot, settings_manager, mock_languages):
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)

    dialog.set_combo_index(dialog.lang_combo, "en_US");
    dialog._save_settings()
    assert settings_manager.get("language") == "en_US"

    dialog.set_combo_index(dialog.lang_combo, "zh_CN");
    dialog._save_settings()
    assert settings_manager.get("language") == "zh_CN"

    dialog.close()


def test_dialog_respects_existing_system_font_setting(qtbot, settings_manager):
    settings_manager.set("hud_font_size", "system")
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    assert dialog.font_combo.currentData() == "system"
    dialog.close()


def test_dialog_respects_existing_int_font_setting(qtbot, settings_manager):
    settings_manager.set("hud_font_size", 20)
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    assert dialog.font_combo.currentText() == "20"
    dialog.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])