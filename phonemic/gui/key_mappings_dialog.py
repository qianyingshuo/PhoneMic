import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt

from phonemic.utils.key_mappings_manager import KeyMappingsManager
from phonemic.gui.keyboard import validate_key_sequence
from phonemic.utils.i18n import I18n

logger = logging.getLogger(__name__)

class KeyMappingEditDialog(QDialog):
    """新增或修改按键映射的对话框"""
    
    def __init__(self, parent=None, item_id=None):
        super().__init__(parent)
        self.item_id = item_id # 若为 None 则为新增模式，否则为修改模式
        self.manager = KeyMappingsManager()
        self.i18n = I18n.instance()
        
        self.setWindowTitle(
            self.tr("key_mappings.edit_title_edit", "编辑按键映射") if item_id 
            else self.tr("key_mappings.edit_title_add", "新增按键映射")
        )
        self.resize(320, 160)
        self.init_ui()
        
        if self.item_id:
            self.load_data()

    def tr(self, key: str, default: str) -> str:
        """多语言辅助翻译"""
        val = self.i18n.tr(key)
        return default if val == key else val

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. 名字输入
        name_layout = QHBoxLayout()
        name_label = QLabel(self.tr("key_mappings.label_name", "显示名称:"), self)
        self.name_input = QLineEdit(self)
        self.name_input.setMaxLength(12) # 限制最大12个字符
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 2. 按键序列输入
        keys_layout = QHBoxLayout()
        keys_label = QLabel(self.tr("key_mappings.label_keys", "按键序列:"), self)
        self.keys_input = QLineEdit(self)
        self.keys_input.setPlaceholderText("如: enter 或 ctrl+a, delete")
        keys_layout.addWidget(keys_label)
        keys_layout.addWidget(self.keys_input)
        layout.addLayout(keys_layout)
        
        # 3. 按钮
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton(self.tr("key_mappings.btn_save", "保存"), self)
        self.btn_cancel = QPushButton(self.tr("key_mappings.btn_cancel", "取消"), self)
        
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def load_data(self):
        """编辑模式下载入已有配置数据"""
        item = self.manager.get_key_mapping(self.item_id)
        if item:
            self.name_input.setText(item["name"])
            self.keys_input.setText(item["keys"])

    def accept(self):
        """重写 accept，在关闭对话框前执行参数校验与存盘"""
        name = self.name_input.text().strip()
        keys = self.keys_input.text().strip()
        
        # 1. 限制名称长度 1-12
        if not name or len(name) > 12:
            QMessageBox.warning(self, self.tr("common.error", "错误"), self.tr("key_mappings.err_name_len", "名称长度必须在 1-12 字符之间"))
            return
            
        # 2. 校验名字是否重名
        mappings = self.manager.get_key_mappings()
        for item in mappings:
            if item["id"] != self.item_id and item["name"] == name:
                QMessageBox.warning(self, self.tr("common.error", "错误"), self.tr("key_mappings.err_name_exists", "该名称已存在"))
                return
                
        # 3. 校验按键序列合法性
        ok, err = validate_key_sequence(keys)
        if not ok:
            QMessageBox.warning(self, self.tr("common.error", "错误"), self.tr("key_mappings.err_keys_invalid", f"按键序列无效: {err}"))
            return
            
        # 4. 执行持久化保存
        try:
            if self.item_id:
                self.manager.update_key_mapping(self.item_id, name, keys)
            else:
                self.manager.add_key_mapping(name, keys)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, self.tr("common.error", "错误"), f"保存失败: {e}")


class KeyMappingsDialog(QDialog):
    """按键映射列表展示及管理对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = KeyMappingsManager()
        self.i18n = I18n.instance()
        
        self.setWindowTitle(self.tr("key_mappings.dialog_title", "按键映射管理"))
        self.resize(400, 300)
        self.init_ui()
        self._load_list()

    def tr(self, key: str, default: str) -> str:
        """多语言辅助翻译"""
        val = self.i18n.tr(key)
        return default if val == key else val

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # 左侧列表框
        self.list_widget = QListWidget(self)
        self.list_widget.currentItemChanged.connect(self._on_item_changed)
        main_layout.addWidget(self.list_widget, 3)
        
        # 右侧操作按钮
        btn_layout = QVBoxLayout()
        self.btn_add = QPushButton(self.tr("key_mappings.btn_add", "新增"), self)
        self.btn_edit = QPushButton(self.tr("key_mappings.btn_edit", "修改"), self)
        self.btn_delete = QPushButton(self.tr("key_mappings.btn_delete", "删除"), self)
        self.btn_close = QPushButton(self.tr("key_mappings.btn_close", "关闭"), self)
        
        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_close.clicked.connect(self.close)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        main_layout.addLayout(btn_layout, 1)

    def _load_list(self):
        """重新从配置中加载列表"""
        self.list_widget.clear()
        mappings = self.manager.get_key_mappings()
        for item in mappings:
            display_text = f"{item['name']}"
            if item["keys"]:
                display_text += f" ({item['keys']})"
            
            list_item = QListWidgetItem(display_text, self.list_widget)
            list_item.setData(Qt.UserRole, item["id"])
            self.list_widget.addItem(list_item)
            
        # 默认选中第一项
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _on_item_changed(self, current, previous):
        """选中项发生变更时，若为 none 默认项，置灰“修改”与“删除”按钮"""
        if not current:
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
            return
            
        item_id = current.data(Qt.UserRole)
        if item_id == "none":
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
        else:
            self.btn_edit.setEnabled(True)
            self.btn_delete.setEnabled(True)

    def _on_add(self):
        """点击新增"""
        self._show_edit_dialog()

    def _on_edit(self):
        """点击修改"""
        current = self.list_widget.currentItem()
        if not current:
            return
        item_id = current.data(Qt.UserRole)
        self._show_edit_dialog(item_id)

    def _show_edit_dialog(self, item_id=None):
        """弹起编辑对话框的辅助函数"""
        edit_dialog = KeyMappingEditDialog(self, item_id)
        if edit_dialog.exec() == QDialog.Accepted:
            self._load_list()

    def _on_delete(self):
        """点击删除"""
        current = self.list_widget.currentItem()
        if not current:
            return
        item_id = current.data(Qt.UserRole)
        if item_id == "none":
            return
            
        confirm_title = self.tr("common.confirm", "确认")
        confirm_msg = self.tr("key_mappings.confirm_delete", "确定要删除这条按键映射吗？")
        
        reply = QMessageBox.question(
            self, confirm_title, confirm_msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.manager.delete_key_mapping(item_id):
                self._load_list()
