# Interface Contract: Dashboard & SystemTray 交互协议

本特性属于客户端进程内（In-Process）的两个 UI 核心类——主窗口（Dashboard）和系统托盘（SystemTray）之间的协作契约。

## 协作交互协议 (Interaction Protocol)

```mermaid
sequenceDiagram
    autonumber
    actor User as 用户
    participant DT as Dashboard (主窗口)
    participant ST as SystemTray (托盘)
    participant QA as QApplication (Qt核心应用)

    rect rgb(240, 248, 255)
        note right of User: 场景 1. 点击窗口最小化
        User->>DT: 点击“最小化”按钮
        DT->>DT: 触发 changeEvent (WindowStateChange)
        DT->>DT: 判定 windowState() 包含 Minimized
        DT->>DT: 执行 self.hide() 隐藏窗口
        DT->>DT: 执行 self.setWindowState(Qt.WindowNoState) 清除最小化物理状态
        DT->>DT: 拦截该事件 (event.ignore)
        Note over DT,ST: 结果：窗口消失，无任务栏，仅托盘可见
    end

    rect rgb(255, 245, 238)
        note right of User: 场景 2. 点击窗口 (X) 关闭
        User->>DT: 点击右上角“关闭 (X)”按钮
        DT->>DT: 触发 closeEvent(event)
        DT->>DT: 检查 self._force_quit == False
        DT->>DT: 执行 self.hide() 隐藏窗口
        DT->>DT: 忽略并拦截该事件 (event.ignore)
        Note over DT,ST: 结果：窗口从任务栏和桌面隐藏，后台进程保持活跃
    end

    rect rgb(240, 255, 240)
        note right of User: 场景 3. 从托盘唤醒窗口
        User->>ST: 双击托盘图标 / 托盘菜单选择“显示主界面”
        ST->>DT: 调用 show_main_window()
        DT->>DT: 执行 self.show() 恢复显示
        DT->>DT: 执行 self.raise_() 置于最前
        DT->>DT: 执行 self.activateWindow() 捕获活动焦点
    end

    rect rgb(255, 240, 245)
        note right of User: 场景 4. 从系统托盘菜单彻底退出
        User->>ST: 右键托盘图标 -> 选择“退出”
        ST->>ST: 触发退出绑定槽函数 quit_application()
        ST->>DT: 设置 self.dashboard._force_quit = True
        ST->>QA: 调用 QApplication.quit() 发起退出信号
        QA->>DT: 向各层级窗口分发最终的 closeEvent(event)
        DT->>DT: 检查 self._force_quit == True
        DT->>DT: 接受关闭事件 (event.accept)
        QA->>QA: 清理端口，彻底退出主进程
    end
```

## 数据传输与交互契约说明

1. **Dashboard 变量依赖**：
   * `SystemTray` 必须持有 `Dashboard` 实例的强引用（在 `__init__(self, dashboard, icon_path)` 中传入）。
   * `SystemTray` 在调用退出生命周期时，对 `dashboard._force_quit` 进行属性修改的字段名称必须为 `_force_quit`，以与 `Dashboard` 类中重写的 `closeEvent` 判断严格对齐。
2. **事件忽略与还原约定**：
   * 所有在 `Dashboard` 中因为点击 (X) 或最小化被重定向为隐藏的行为，均必须显式调用 `event.ignore()` 阻止 Qt 平台继续向下游分发销毁/缩放事件。
   * 为了保证多端语音传输不因为界面可见度改变而被 Qt 消息循环挂起（Suspended），在隐藏主窗口后，底层的 WebSocket 连接和异步异步事件队列必须保持正常读写。
