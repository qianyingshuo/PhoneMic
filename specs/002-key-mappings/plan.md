# Implementation Plan: 手机网页端快捷按键映射选择与执行

**Branch**: `002-key-mappings` | **Date**: 2026-06-28 | **Spec**: [spec.md](file:///home/coding/workspace/PhoneMic/specs/002-key-mappings/spec.md)

**Input**: Feature specification from `/specs/002-key-mappings/spec.md`

---

## Summary

实现手机网页端向 PC 客户端发送语音或打字文本时，能够自动追加特定的按键映射序列（如回车、Tab 等）。
* **技术路线**: 
  - 在 PC 端使用 UUIDv4 统一管理按键映射配置列表，持久化写入 `settings.json` 的新字段 `"key_mappings"` 中。
  - PC 端提供 `KeyMappingsDialog` 进行可视化 CRUD 维护。
  - 通过 WebSocket 长连接实现配置的初始化下发和变更广播（局部热更新），以及 reload 兜底重载控制。
  - 手机端采用 LocalStorage 缓存用户选择的 UUID，并在发送文本时将 UUID 代表的 `key_sequence` 一同打包发回 PC。
  - PC 端在调用 `flash_insert` 粘贴完文本后，调用已有的 `keyboard.send_keys(key_sequence)` 模拟对应的按键，并对非法 UUID 或失效 ID 实施安全降级（仅粘贴，不触发模拟，并回发警告通知）。

---

## Technical Context

* **Language/Version**: Python >=3.10, <3.15 (核心逻辑为 Python 3.10+) | HTML5 + CSS + JavaScript (手机网页端)
* **Primary Dependencies**: FastAPI (Web 及 WebSocket 路由), PySide6 (GUI 框架), pyautogui & keyboard (按键模拟与输入校验)
* **Storage**: 本地 JSON 文件 (`settings.json`) 持久化，无需数据库
* **Testing**: pytest, pytest-qt, pytest-asyncio, pytest-mock (TDD 单元测试框架)
* **Target Platform**: Windows 操作系统（模拟按键），Linux/headless（开发与单元测试环境）
* **Project Type**: 具有 Web/WS 服务端和 GUI 面板的桌面端应用程序
* **Performance Goals**: 
  - 发送加模拟按键执行的总延迟在 150 毫秒以内。
  - 网页端列表的局域网同步延迟小于 300 毫秒。
* **Constraints**: 模拟按键须在前台活动窗口执行。PC端保存按键映射时必须对显示名称进行唯一性校验（不可重名）与长度限制（最多12字符），且进行合法按键白名单格式校验；对已失效的旧 ID 请求拒绝执行按键模拟。
* **Scale/Scope**: 单用户局域网点对点长连接。

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **原则 I. 核心逻辑解耦与 API-First**: ✅ 通关。按键映射管理器 `KeyMappingsManager` 完全解耦，是一个独立的纯 Python 类，不掺杂任何 GUI 元素，可通过独立 API 进行完整测试。
2. **原则 II. 平台差异抽象与可打桩设计 (Mockability)**: ✅ 通关。单元测试将完全使用 mock 屏蔽 `pyautogui` 和 `win32` 原生按键事件，确保所有测试能无障碍在 Linux 自动化容器中全绿跑通。
3. **原则 III. 测试驱动开发 (TDD 铁律)**: ✅ 通关。实施前须遵循 TDD 规范，先在 `tests/` 中编写失败的测试用例（如传入包含按键序列的字典时，验证 `send_keys` 触发），然后再编写核心代码使其通过。
4. **原则 IV. 多端安全防护与输入防御**: ✅ 通关。对用户的输入进行格式匹配校验，仅接受 valid keyboard keys ；对未知/非法的 ID 请求强制执行安全降级，不予模拟按键，并回发警告信息通知。

---

## Project Structure

### Documentation (this feature)

```text
specs/002-key-mappings/
├── spec.md              # 需求规格说明书
├── plan.md              # 实施计划 (本文件)
├── research.md          # 选型与决策文档
├── data-model.md        # 配置数据模型定义
├── quickstart.md        # 端到端快速验证指南
├── contracts/
│   └── websocket-contracts.md # WebSocket 通信合同
└── checklists/
    └── requirements.md  # 规约质量自检清单
```

### Source Code (repository root)

```text
phonemic/
├── PhoneMic.py           # 主入口 (拦截 send 事件，支持 payload 字典解析与 send_keys 触发)
├── server/
│   └── api.py            # 后端服务 (连接成功下发配置，监听配置广播，WS 解析 key_sequence 转发)
├── utils/
│   ├── key_mappings_manager.py  # [NEW] 按键映射管理器，处理 key_mappings.json / settings.json 的读写
│   └── settings_manager.py
├── gui/
│   ├── dashboard.py      # 主界面 (设置菜单挂载 Action)
│   ├── keyboard.py       # 按键模拟模块 (send_keys 实现)
│   └── key_mappings_dialog.py   # [NEW] 按键映射管理界面 Dialog
└── resources/
    ├── mobile.html       # 手机网页端 (左侧设置 Drawer 容器，LocalStorage 缓存与 WS 消息打包)
    └── locales/
        ├── zh_CN.json    # 中文国际化资源
        └── en_US.json    # 英文国际化资源
```

**Structure Decision**: 采用单体项目结构，所有 Python 逻辑位于 `phonemic/` 包内，网页模板及 Favicon 等静态资源放置于其子目录 `resources/` 下。各层职责明确、依赖路径清晰。
