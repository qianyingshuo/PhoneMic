# 方案设计：Windows 窗口最小化与关闭至系统托盘

本设计文档详细描述了如何修改主窗口（Dashboard）的最小化与关闭行为。通过该设计，当用户最小化或关闭主窗口时，程序不会退出，而是隐藏在任务栏和 Alt+Tab 任务切换视图中，仅保留在右下角的系统托盘中；同时，确保系统托盘中的“退出”功能能够正常并彻底地退出应用程序。

## 变更背景与目标

当前版本的 PhoneMic 在点击右上角“最小化”按钮时，会在任务栏中保留图标，且会在 Alt+Tab 任务切换时出现，干扰用户日常使用。点击“关闭”按钮则会直接结束进程。
本方案的目标是：
1. **最小化隐藏**：点击主窗口“最小化”时，窗口彻底隐藏（不占任务栏、不在 Alt+Tab 显示），仅保留托盘图标。
2. **关闭隐藏**：点击主窗口“关闭 (X)”时，同样将其隐藏至托盘，不退出程序。
3. **安全退出**：系统托盘右键菜单中的“退出”能够不受拦截地彻底关闭程序。

---

## 详细变更设计

为了实现上述功能，需要分别修改 `Dashboard` 窗口类和 `SystemTray` 托盘类。因为“关闭窗口”与“托盘退出”都会向主窗口分发关闭事件，我们通过在 `Dashboard` 中引入一个内部标志位来区分这两者。

### 1. 修改主窗口 [gui/dashboard.py](file:///home/coding/workspace/PhoneMic/phonemic/gui/dashboard.py)

在 `Dashboard` 类中重写事件处理函数并增加用于控制退出的内部状态：

* **添加强制退出标志位**：
  在 `__init__` 函数内初始化 `self._force_quit = False`。
* **重写关闭事件 (`closeEvent`)**：
  若 `self._force_quit` 为 `True`，接受事件并退出；否则，仅调用 `self.hide()` 隐藏窗口并忽略事件。
* **重写窗口状态改变事件 (`changeEvent`)**：
  当捕捉到窗口最小化事件（`QEvent.WindowStateChange` 且 `self.isMinimized()` 为 `True`）时，调用 `self.hide()` 隐藏窗口。并在隐藏后重置窗口状态为正常状态（`Qt.WindowNoState`），以便下次双击托盘时能正常弹出窗口。

#### 代码设计片段：
```python
from PySide6.QtCore import QEvent, Qt

class Dashboard(QMainWindow):
    def __init__(self, ip: str, port: int, parent=None):
        super().__init__(parent)
        self._force_quit = False
        # ... 原有初始化代码 ...

    def closeEvent(self, event):
        # 仅当托盘触发退出并设置强制退出标志时才真正退出，否则仅隐藏到托盘
        if getattr(self, "_force_quit", False):
            event.accept()
        else:
            self.hide()
            event.ignore()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                self.hide()
                # 必须重置最小化状态，否则之后调用 show() 时窗口依然会是最小化状态
                self.setWindowState(Qt.WindowNoState)
                event.ignore()
                return
        super().changeEvent(event)
```

---

### 2. 修改托盘菜单 [gui/tray.py](file:///home/coding/workspace/PhoneMic/phonemic/gui/tray.py)

在 `SystemTray` 类中，由于要实现彻底退出的动作，需要修改菜单项的连接逻辑：

* **添加自定义退出函数**：
  新增 `quit_application(self)` 方法。该方法内部将绑定的 `self.dashboard._force_quit` 设为 `True`，随后调用 `QApplication.quit()` 以发起程序退出的整个生命周期流程。
* **修改托盘右键菜单绑定**：
  在 `_create_tray_menu` 方法中，将原先直接绑定的 `lambda: QApplication.quit()` 修改为绑定我们新增的 `self.quit_application`。

#### 代码设计片段：
```python
class SystemTray(QObject):
    # ... 原有代码 ...

    def quit_application(self):
        """执行真正的退出程序流程"""
        if self.dashboard:
            self.dashboard._force_quit = True
        QApplication.quit()

    def _create_tray_menu(self):
        menu = QMenu()
        menu.addAction(self.i18n.tr("tray.menu_show")).triggered.connect(self.show_main_window)
        menu.addSeparator()
        menu.addAction(self.i18n.tr("tray.menu_settings")).triggered.connect(self._open_settings)
        menu.addAction(self.i18n.tr("dashboard.menu_command")).triggered.connect(self._open_commands_dialog)
        menu.addSeparator()
        menu.addAction(self.i18n.tr("tray.menu_about")).triggered.connect(self.dashboard.show_about)
        # 将原直接调用 quit 替换为调用 quit_application
        menu.addAction(self.i18n.tr("tray.menu_quit")).triggered.connect(self.quit_application)
        return menu
```

---

## 验证与测试建议

完成此设计方案的开发后，需执行以下测试步骤：
1. **测试最小化行为**：
   运行程序，点击主窗口右上角的“最小化”按钮。
   * *预期结果*：窗口从桌面消失，任务栏没有 PhoneMic 图标，按下 `Alt+Tab` 键无法在窗口列表中找到 PhoneMic；右下角系统托盘处仍保留带有红点或绿点的 PhoneMic 托盘图标。
2. **测试恢复显示行为**：
   单击或双击托盘图标，或通过右键菜单选择“显示主界面”。
   * *预期结果*：主窗口以正常大小正常还原弹出，并处于激活前端状态。
3. **测试关闭行为**：
   在显示窗口的状态下，点击主窗口右上角的“关闭 (X)”按钮。
   * *预期结果*：行为与最小化相同，主窗口完全隐藏且不退出程序，且后台服务（手机扫码连接输入等）功能依然正常可用。
4. **测试托盘退出行为**：
   右键点击右下角的系统托盘图标，选择“退出”。
   * *预期结果*：程序及关联的 FastAPI 后台服务器彻底结束，系统托盘图标消失。
