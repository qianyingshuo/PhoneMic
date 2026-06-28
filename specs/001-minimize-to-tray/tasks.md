# Tasks: Windows 窗口最小化与关闭至系统托盘

**Input**: Design documents from `/specs/001-minimize-to-tray/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: 测试是强制的 (TDD 铁律) - 必须在编写任何生产代码前，先在测试文件中编写 Failing 测试，并确保其运行报错，然后再编写极简代码使之全绿。

**Organization**: 任务完全按照用户故事阶段进行分组，以支持每个故事的独立实施和验证。

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: 可并行执行的任务（修改不同文件，无未完成的依赖任务）
- **[Story]**: 任务所属的用户故事编号（如 US1, US2, US3, US4）
- 描述中必须包含完整且精确的文件路径。

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 准备测试基础框架和环境

- [x] T001 配置基础测试环境并在 tests/ 目录下准备新建的单元测试文件 tests/test_dashboard_tray.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 准备跨平台与宿主机验证环境

- [x] T002 确认宿主机 GUI 自动化验证脚本已同步至共享挂载路径下 /mnt/s/WSL/wsl_windows_test/test_windows_host_gui.py

---

## Phase 3: User Story 4 - 宿主机自动化 GUI 验证脚本 (Priority: P1) 🎯 MVP

**Goal**: 实现可在宿主机直接对测试版窗口进行事件投递与状态断言的验证脚本

**Independent Test**: 在宿主机运行该脚本，其必须能够成功搜寻窗口句柄，并正确因为新逻辑尚未编写而触发失败报错。

### Implementation for User Story 4

- [x] T003 [US4] 验证宿主机测试脚本 tests/test_windows_host_gui.py 在修改主程序前能正常执行并拦截报错

---

## Phase 4: User Story 1 - 窗口最小化隐藏 (Priority: P1)

**Goal**: 主窗口点击“最小化”后，窗口彻底隐藏（脱离任务栏与 Alt+Tab），且清除最小化物理状态标志

**Independent Test**: 运行单元测试断言，以及实机上最小化后任务栏为0。

### Tests for User Story 1 (MANDATORY - TDD Phase) ⚠️
- [x] T004 [P] [US1] 在 tests/test_dashboard_tray.py 中编写最小化隐藏的 Failing 单元测试（断言 isHidden 状态和 WindowNoState）

### Implementation for User Story 1
- [x] T005 [US1] 在 phonemic/gui/dashboard.py 中重写 changeEvent 并实现 isMinimized 状态下的隐藏和状态清除
- [x] T006 [US1] 运行 pytest 单元测试命令 poetry run pytest tests/test_dashboard_tray.py -k test_minimize 确保测试全绿通过

---

## Phase 5: User Story 2 - 窗口关闭转换为隐藏 (Priority: P2)

**Goal**: 点击右上角关闭 (X) 按钮时拦截事件并隐藏窗口，不退出进程

**Independent Test**: 单元测试中关闭事件被 ignore，且窗口可见性变为隐藏。

### Tests for User Story 2 (MANDATORY - TDD Phase) ⚠️
- [x] T007 [P] [US2] 在 tests/test_dashboard_tray.py 中编写关闭拦截的 Failing 单元测试（断言关闭事件被 ignore 且窗口隐藏）

### Implementation for User Story 2
- [x] T008 [US2] 在 phonemic/gui/dashboard.py 中重写 closeEvent 并引入 _force_quit = False 标志，实现非强制退出的隐藏逻辑
- [x] T009 [US2] 运行 pytest 单元测试命令 poetry run pytest tests/test_dashboard_tray.py -k test_close 确保测试全绿通过

---

## Phase 6: User Story 3 - 托盘菜单彻底退出 (Priority: P3)

**Goal**: 托盘菜单右键选择“退出”时，能绕过关闭拦截，允许进程安全终止并释放端口

**Independent Test**: 单元测试中在 _force_quit 开启时，关闭事件被 accept，进程顺利结束。

### Tests for User Story 3 (MANDATORY - TDD Phase) ⚠️
- [x] T010 [P] [US3] 在 tests/test_dashboard_tray.py 中编写托盘彻底退出的 Failing 单元测试（断言开启强制退出标志后 closeEvent 被 accept）

### Implementation for User Story 3
- [x] T011 [US3] 在 phonemic/gui/tray.py 中新增 quit_application 槽函数，在退出前将 dashboard._force_quit 置为 True 并绑定托盘退出菜单
- [x] T012 [US3] 运行 pytest 单元测试命令 poetry run pytest tests/test_dashboard_tray.py -k test_force_quit 确保测试全绿通过

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 进行实机回归测试与交付报告生成

- [x] T013 运行宿主机 GUI 自动化验证脚本 tests/test_windows_host_gui.py 进行 Windows 实机回归并确保测试全绿
- [x] T014 按照 specs/001-minimize-to-tray/quickstart.md 校验并输出 specs/001-minimize-to-tray/walkthrough.md 交付报告

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1) & Foundational (Phase 2)**: 必须最先完成，无其它依赖。
- **User Story 4 (Phase 3)**: 依赖 Foundational 阶段完成，提供宿主机第一套验证工具。
- **User Story 1 (Phase 4)**: 依赖 US4 完成，可与其它 User Story 并行。
- **User Story 2 (Phase 5)**: 依赖 US4 完成，可与其它 User Story 并行。
- **User Story 3 (Phase 6)**: 依赖 US1、US2 的改动完成，用于验证托盘退出覆盖拦截的行为。
- **Polish (Phase 7)**: 依赖所有 User Story 阶段完成。

---

## Parallel Opportunities

- 所有的 Failing 单元测试编写任务（`T004`, `T007`, `T010`）均可并行执行。
- `User Story 1` (最小化) 与 `User Story 2` (关闭隐藏) 的生产逻辑开发可由不同开发者独立并行实施。
