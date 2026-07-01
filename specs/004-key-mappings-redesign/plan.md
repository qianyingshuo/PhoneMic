# Implementation Plan: 手机端双按键映射通道重构 (key-mappings-redesign)

**Branch**: `004-key-mappings-redesign` | **Date**: 2026-07-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-key-mappings-redesign/spec.md`

---

## Summary

重构手机端快捷栏，移除多余的火箭发送按钮并新增独立的单独发送按键下拉框。通过前端文本内容判断（非空 vs 空白）在底栏『发送』按钮/输入法回车时进行逻辑分流，完美解耦文本自动追加和单独按键模拟这两个交互通道。

---

## Technical Context

* **Language/Version**: Python >=3.10 | HTML5 + CSS + JavaScript (手机网页端)
* **Primary Dependencies**: FastAPI (静态网页及 WS 路由), PySide6, PyAutoGUI & keyboard (PC 端系统按键模拟)
* **Storage**: 手机端 `window.localStorage` 持久化本地缓存
* **Testing**: pytest
* **Target Platform**: Windows 操作系统 (按键模拟目标环境), Linux / headless (单元测试容器环境)
* **Project Type**: 具有 Web/WS 服务端和 GUI 面板的桌面端应用程序
* **Performance Goals**: 空文本按键映射发送至 PC 模拟响应的端到端延迟小于 150 毫秒。
* **Constraints**: 
  - 当输入框为空且“单独发按键”下拉框值为 `none` 时，系统必须拦截发送行为，不触发网络传输。
  - 手机端控制按钮文字保持静态，不受当前下拉框所选按键状态的干扰。

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **原则 I. 核心逻辑解耦与 API-First**: ✅ 通关。本次重构完全在手机前端 `mobile.html` 这一层展开，后端 API 和核心的按键发送通道（FastAPI Route & Python controllers）完全不动，契合 API-First 规范。
2. **原则 II. 平台差异抽象与可打桩设计 (Mockability)**: ✅ 通关。所有测试通过静态 DOM 检测和 JS 伪代码特征词断言来实现，避开了物理系统键盘事件阻断。
3. **原则 III. 测试驱动开发 (TDD 铁律)**: ✅ 通关。编码前，需先在 `tests/test_backend.py` 编写关于双选择框元素和 JS 分流分支特征词的 Failing 测试（RED），然后编码（GREEN）。
4. **原则 IV. 多端安全防护与输入防御 (LAN Security & Input Defense)**: ✅ 通关。前端在空状态发送时执行严格的前置白名单空拦截，防止非法或者无用数据大量发送到 PC 服务端，规避网络滥用。

---

## Project Structure

### Documentation (this feature)

```text
specs/004-key-mappings-redesign/
├── spec.md              # 需求规格说明书
├── plan.md              # 实施计划 (本文件)
├── research.md          # 技术决策文档
├── data-model.md        # LocalStorage 数据模型
├── quickstart.md        # 端到端快速验证指南
└── contracts/
    └── websocket-contracts.md # WebSocket 传输协议合同
```

### Source Code (repository root)

```text
phonemic/
└── resources/
    └── mobile.html       # [MODIFY] 手机前端页面 (新增 single-key-mapping-select，处理逻辑分流与 LocalStorage 双键持久化)

tests/
└── test_backend.py       # [MODIFY] 单元测试 (新增关于双选择框及分流逻辑断言的测试)
```

**Structure Decision**: 采用单体项目结构，只修改前端视图 `mobile.html` 和测试文件 `test_backend.py`。

---

## Verification Plan

### Automated Tests
- 运行 pytest 针对前端 mobile.html 静态 DOM 进行断言测试：
  `./.venv/bin/pytest tests/test_backend.py -k test_mobile_html_`

### Manual Verification
- 参照 [quickstart.md](quickstart.md) 中定义的 4 组端到端验证用例在真机上进行手势操作、输入状态切换，确保逻辑完美符合预期。
