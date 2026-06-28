# Research & Decisions: Windows 窗口最小化与关闭至系统托盘

本研究文档详细记录了关于“Windows 主窗口最小化/关闭隐藏至系统托盘”这一特性的技术选型与断言设计的思考。

## 技术选型决策与权衡

### 1. 窗口状态与可见性控制 (Window Visibility & State Control)
* **选型结果**：采用 `hide()` 方法进行彻底隐藏，并在最小化拦截中调用 `setWindowState(Qt.WindowNoState)`。
* **决策理由**：
  * 使用 `hide()` 可以让窗口从操作系统级的任务栏中移除，也确保在 Windows 任务切换器（Alt+Tab）中不被罗列出来。
  * 如果仅仅将窗口最小化（调用 `showMinimized()`），它依然会停留在任务栏。
  * 在 Qt 中，隐藏一个被最小化的窗口时，必须将窗口的状态设置回正常无状态（`Qt.WindowNoState`）。否则，在从系统托盘重新激活调用 `show()` 时，窗口仍会保持之前的“最小化”物理状态，导致恢复失败。
* **其他替代方案**：
  * 改变窗口标志（如设置 `Qt.Tool` 或 `Qt.SubWindow`）：这会改变窗口的边框样式，且容易引发跨平台的界面缩放bug。使用简单的 `hide()` 和 `showNormal()` 是最稳定、对渲染引擎影响最小的路径。

### 2. 区分常规关闭（拦截）与托盘菜单“退出” (Force Quit Flagging)
* **选型结果**：在 `Dashboard` (QMainWindow) 类中引入一个控制变量 `_force_quit: bool`。
* **决策理由**：
  * 主窗口的 (X) 关闭按钮以及通过托盘选择“退出”都会触发主窗口的 `closeEvent`。
  * 当用户在窗口中点击 (X) 时，`_force_quit` 为默认值 `False`，我们将忽略（`ignore`）该关闭事件并将其隐藏。
  * 当用户在系统托盘选择“退出”时，托盘控制逻辑首先将 `dashboard._force_quit` 设为 `True`，再调用 `QApplication.quit()`，此时 `closeEvent` 会被允许（`accept`），程序顺利安全关闭。
* **其他替代方案**：
  * 检测事件的自发性 (`event.spontaneous()`)：该属性在不同平台上的行为表现不一致，且在虚拟的 WSL 环境下测试时难以模拟。使用自定义的 `_force_quit` 标志位能够提供绝对确定和易于单元测试的拦截控制。

---

## TDD 自动化测试打桩设计（ WSL 虚拟机测试环境）

根据项目宪章中“原则 II. 平台差异抽象与可打桩设计”与“原则 III. 测试驱动开发”要求：
由于我们的主要开发与测试机器均运行于无 Windows 系统托盘和无物理 GUI 窗口管理器环境（WSL Linux 容器），因此核心的行为检验必须以**自动化单元测试**方式跑通。

* **测试框架**：采用 `pytest` + `pytest-qt` (`qtbot`) + `pytest-mock`。
* **打桩策略**：
  * Mock 掉 `QMessageBox` 等可能阻塞 GUI 线程的对话框组件。
  * 通过 `QApplication.sendEvent` 或在 `qtbot` 管理的 widget 实例上直接注入 `QWindowStateChangeEvent` 与 `QCloseEvent`，对窗口的 `.isHidden()` 和标志位进行断言，以此在 WSL 环境中验证其隐藏行为。
  * 真机上的多端连接稳定性、系统级切窗隐藏测试由于依赖操作系统原生 API，将放入**手动实机测试（Manual Verification）**流程，在 Windows 物理真机上进行。
