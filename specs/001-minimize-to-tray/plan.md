# Implementation Plan: Windows 窗口最小化与关闭至系统托盘

**Branch**: `001-minimize-to-tray` | **Date**: 2026-06-28 | **Spec**: [specs/001-minimize-to-tray/spec.md](file:///home/coding/workspace/PhoneMic/specs/001-minimize-to-tray/spec.md)

**Input**: Feature specification from `/specs/001-minimize-to-tray/spec.md`

## Summary

实现 PhoneMic 电脑端主窗口点击右上角关闭 (X) 和最小化按钮时，将其隐藏至系统托盘（不再占用任务栏与 Alt+Tab 切窗列表），同时确保通过系统托盘的右键菜单“退出”可以真正并且安全地退出进程与释放端口。此外，在工程共享目录中提供一个可在 Windows 宿主机运行的自动化 GUI 验证脚本。为了与用户正在运行的生产版 PhoneMic 隔离，开发测试版的窗口标题将硬编码或动态附加 `(Dev)` 后缀，且测试脚本将特异性匹配该标题。

## Technical Context

**Language/Version**: Python >= 3.10, < 3.15

**Primary Dependencies**: PySide6 (>=6.11.1), `pywin32` (仅限 Windows 验证脚本端使用)

**Storage**: N/A

**Testing**: pytest, pytest-qt, pytest-mock (WSL环境); pywin32 win32gui/win32con (Windows宿主机环境)

**Target Platform**: Windows (编译与运行环境), Linux / WSL (TDD 单元测试执行环境)

**Project Type**: desktop-app

**Performance Goals**: 
- 从隐藏状态唤醒显示主窗口响应延迟 < 0.5 秒。
- 从系统托盘菜单彻底退出程序、关闭后台 FastAPI 服务并释放网络端口时长 < 2.0 秒。
- 宿主机端自动化 GUI 验证脚本整体运行断言耗时 < 10.0 秒。

**Constraints**:
- 不引入外部配置文件读写和多语言文本定义。
- 自动化单元测试必须能在 WSL / Headless Linux 虚拟容器环境中通过，不允许依赖 Windows 系统 API 或物理 GUI 窗口渲染。

**Scale/Scope**: 
- 修改 2 个源文件（`dashboard.py` 与 `tray.py`）。
  * 在 `dashboard.py` 中，设定标题时，将开发测试状态下的主窗口标题修改为增加 `(Dev)` 后缀，如 `"PhoneMic - 主界面 (Dev)"`。
- 新增 1 个 WSL 单元测试文件（`test_dashboard_tray.py`）覆盖最小化隐藏、关闭拦截及强制退出。
- 新增 1 个 Windows 自动化 GUI 测试验证脚本，匹配带 `(Dev)` 的开发版窗口：
  * 项目路径：`tests/test_windows_host_gui.py`
  * 宿主机共享路径：`/mnt/s/WSL/wsl_windows_test/test_windows_host_gui.py`

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **原则 I. 核心逻辑解耦与 API-First**: 
  - *评估结果*：**PASS**。修改纯粹在 GUI 层的窗口事件管理器（`closeEvent` / `changeEvent`）内进行，后台的 FastAPI WebSocket 服务仍然与 GUI 窗口解耦。
- **原则 II. 平台差异抽象与可打桩设计 (Mockability)**:
  - *评估结果*：**PASS**。由于在 WSL 无 UI 虚拟机环境执行测试，针对托盘图标退出和 MessageBox 等组件，我们使用 `pytest` 提供的打桩和 mock 工具，断言状态变更逻辑而无需在 Linux 上渲染真正的系统托盘和托盘菜单。
- **原则 III. 测试驱动开发 (TDD 铁律)**:
  - *评估结果*：**PASS**。严格遵循 TDD。在编写任何生产代码前，先创建包含失败用例的测试文件。

---

## Project Structure

### Documentation (this feature)

```text
specs/001-minimize-to-tray/
├── plan.md              # 本文档
├── research.md          # 选型决策与 TDD 测试设计
├── data-model.md        # 内存状态变量及窗口生命周期状态机
├── quickstart.md        # 运行与真机黑盒验证指南
└── contracts/
    └── tray_ui_contract.md # Dashboard 与 SystemTray 的交互契约说明
```

### Source Code

```text
phonemic/
└── gui/
    ├── dashboard.py     # 目标修改：重写 closeEvent/changeEvent，引入 _force_quit 标志，标题拼接 " (Dev)"
    └── tray.py          # 目标修改：修改退出项为绑定自定义退出函数以设置 _force_quit=True

tests/
├── test_dashboard_tray.py  # 新增 WSL 测试文件：编写失败测试并驱动功能开发
└── test_windows_host_gui.py # 新增 Windows 自动化验证脚本（匹配 (Dev) 窗口）
```

**Structure Decision**: 采用标准的 Single Project（单项目单测试模块）结构。在修改 `dashboard.py` 与 `tray.py` 的同时，新增 `tests/test_dashboard_tray.py` 自动化测试脚本驱动开发。此外，在 Windows 共享目录下输出 `test_windows_host_gui.py` 供宿主机直接运行。
