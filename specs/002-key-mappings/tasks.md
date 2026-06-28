# Tasks: 手机网页端快捷按键映射选择与执行

**Input**: Design documents from `/specs/002-key-mappings/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: 测试是强制性的（TDD 铁律三）—— 在实现任何功能代码前，必须先编写对应的失败测试（RED 阶段）。

**Organization**: 任务按用户故事进行分组，以支持每个故事的独立开发、测试与交付。

---

## Format: `[ID] [P?] [Story] Description`

* **[P]**: 可并行执行（修改不同的文件，且对未完成任务无依赖）
* **[Story]**: 任务所属的用户故事标识（如 US1, US2）
* 所有的任务描述均包含具体的文件路径。

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 初始化开发环境和文件骨架

- [X] T001 确认按键映射配置与功能所需的基础文件路径与模块声明符合 specs/002-key-mappings/plan.md 规范

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 核心数据管理类及 CRUD 逻辑开发，这是所有用户故事的前置阻塞项

**⚠️ CRITICAL**: 在本阶段完成前，不得开始任何用户故事的开发

- [X] T002 编写单元测试用例以验证按键映射管理器的 CRUD、默认值注入和配置合法性，位于 tests/test_key_mappings.py (RED)
- [X] T003 实现按键映射管理器 KeyMappingsManager，负责 settings.json 中 key_mappings 列表的数据维护，位于 phonemic/utils/key_mappings_manager.py (GREEN)

**Checkpoint**: 基础模型与数据管理器准备就绪——用户故事开发可以正式开始。

---

## Phase 3: User Story 1 - 手机端发送时自动追加快捷键 (Priority: P1) 🎯 MVP

**Goal**: 实现手机网页端 WebSocket 推送映射列表，本地 LocalStorage 缓存选择，发送时附带快捷键，PC端粘贴后触发 send_keys 模拟及失效降级。

**Independent Test**: 在网页端选择“回车 (Enter)”，手机发送文本，PC端当前活动光标位置粘贴文字后自动回车换行。

### Tests for User Story 1 (MANDATORY - TDD Phase) ⚠️

- [X] T004 [US1] 编写 WebSocket 建立连接时自动同步 key_mappings 列表和接收 send payload 字典的 contract 测试，位于 tests/contract/test_key_mappings_ws.py (RED)
- [X] T005 [US1] 编写 PC 客户端在接收 send 字典时模拟按键执行、UUID 查找以及防错乱安全降级的单元测试，位于 tests/unit/test_key_mappings_trigger.py (RED)

### Implementation for User Story 1

- [X] T006 [US1] 在后端服务中，实现连接建立时下发配置字典、广播映射配置列表、解析 send 携带 key_sequence 字段并转发的逻辑，位于 phonemic/server/api.py (GREEN)
- [X] T007 [US1] 在主事件监听中，实现对 send 消息字典的解析逻辑：粘贴 text 后如果 key_sequence 不为空，则调用 keyboard.send_keys 执行按键序列，同时支持未知 ID 安全降级，位于 phonemic/PhoneMic.py (GREEN)
- [X] T008 [P] [US1] 编写手机网页端左侧设置抽屉（Drawer）的 HTML 结构、半透明遮罩面板以及平滑抽拉过渡的 CSS 样式，位于 phonemic/resources/mobile.html (GREEN)
- [X] T009 [US1] 编写手机网页端 WebSocket 消息侦听（更新 ComboBox 选项）、LocalStorage 选中偏好缓存回显、以及点击发送时合并打包 key_sequence 字段发送的 JS 脚本逻辑，位于 phonemic/resources/mobile.html (GREEN)
- [X] T010 [US1] 补充后端通过 WebSocket 向手机端推送失效警告通知与 reload 兜底重载页面控制协议的支持方法，位于 phonemic/server/api.py (GREEN)

**Checkpoint**: 至此，User Story 1（追加快捷键发送核心功能）已开发完毕，能作为 MVP 版本独立运行和测试。

---

## Phase 4: User Story 2 - PC端按键映射列表自定义管理 (Priority: P2)

**Goal**: 实现 PC 客户端 QMenuBar 动作挂载，拉起按键映射管理弹窗，支持增删改查及显示名称唯一性与12字符长度拦截校验。

**Independent Test**: 在 PC 端新增一个按键映射并校验不重名，保存后观察 settings.json 成功存入，且手机端列表即时完成局部更新渲染。

### Tests for User Story 2 (MANDATORY - TDD Phase) ⚠️

- [X] T011 [US2] 编写 KeyMappingsDialog 界面列表渲染、修改、删除槽函数触发及新增保存校验的测试用例，位于 tests/gui/test_key_mappings_dialog.py (RED)

### Implementation for User Story 2

- [X] T012 [US2] 创建按键映射编辑对话框 KeyMappingEditDialog，实现按键合法性正则匹配验证、显示名称全局唯一（不重名）及最大 12 个字符宽度限制拦截，位于 phonemic/gui/key_mappings_dialog.py (GREEN)
- [X] T013 [US2] 创建按键映射列表展示及删除确认对话框 KeyMappingsDialog，支持保存并同步更新，位于 phonemic/gui/key_mappings_dialog.py (GREEN)
- [X] T014 [US2] 在主窗口菜单栏的“设置”项中新增动作，点击调起 KeyMappingsDialog 进行配置，位于 phonemic/gui/dashboard.py (GREEN)

**Checkpoint**: 此时，User Stories 1 与 2 全数集成完毕。用户在多端均能对按键映射进行自如的管理与选用。

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: 界面优化、国际化语言完善、文档规范更新及端到端交付验证。

- [X] T015 [P] 补全按键映射管理界面、提示、警示通知在多语言模式下所需的中英文词条翻译，位于 phonemic/resources/locales/zh_CN.json 和 en_US.json
- [X] T016 [P] 更新项目用户指南文档，补充“手机端左侧抽屉设置及发送追加按键映射”的说明，位于 USER_GUIDE.md
- [ ] T017 运行 specs/002-key-mappings/quickstart.md 快速验证指南下的四个测试场景以确保通过，生成 specs/002-key-mappings/walkthrough.md 并进行 Git 本地提交

---

## Dependencies & Execution Order

### Phase Dependencies

* **Setup (Phase 1)**: 无任何依赖，可直接执行。
* **Foundational (Phase 2)**: 依赖 Setup 完成，**阻塞**所有用户故事开发。
* **User Stories (Phase 3+)**: 均依赖 Foundational 阶段完成。
  * US1 (Phase 3) 可以完全独立运行测试，是本功能的 MVP。
  * US2 (Phase 4) 可独立运行 UI 部分，但在列表变更局部刷新时，会与 US1 的 WebSocket 推送协议集成。
* **Polish (Phase 5)**: 依赖所有用户故事开发完成。

### Within Each User Story

* 必须先编写 Failing 测试，保证测试能够报错，随后方可编写对应的 production 代码使其通过。
* 数据存储读写（Manager）优先于界面 UI 设计。
* 核心桥接逻辑和按键触发优先于前后台多端联调。

---

## Parallel Example: User Story 1

```bash
# 可并行编写手机网页端前端 UI (T008) 与 PC 客户端的事件拦截触发 (T007):
Task: "编写手机网页端左侧设置抽屉（Drawer）的 HTML 结构与样式在 phonemic/resources/mobile.html"
Task: "实现主事件监听中 send 事件 payload 字典的解析与 send_keys 触发逻辑在 phonemic/PhoneMic.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. 完成 Phase 1: Setup。
2. 完成 Phase 2: Foundational。
3. 完成 Phase 3: User Story 1。
4. **验证与测试**: 启动 PC 客户端与手机端，手动在 LocalStorage 存入特定按键发送进行验证，跑通 US1 自动化测试。
5. 交付演示。

### Incremental Delivery

1. Setup + Foundational 完成 -> 基础就绪。
2. 添加 User Story 1 -> 独立测试并进行 MVP 展示（直接支持基本的追加按键发送功能）。
3. 添加 User Story 2 -> 支持 PC 端可视化定制按键映射、热更新推送与唯一性防重校验，进行终期功能测试。
4. 完成 Phase 5 抛光与快速验证 -> 发布版本分支。
