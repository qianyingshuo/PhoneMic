# Tasks: 安装时自动检测并提示卸载旧版本

**Input**: Design documents from `/specs/005-auto-uninstall-old-version/`

**Prerequisites**: [plan.md](file:///home/coding/workspace/PhoneMic/specs/005-auto-uninstall-old-version/plan.md) (required), [spec.md](file:///home/coding/workspace/PhoneMic/specs/005-auto-uninstall-old-version/spec.md) (required), [research.md](file:///home/coding/workspace/PhoneMic/specs/005-auto-uninstall-old-version/research.md), [data-model.md](file:///home/coding/workspace/PhoneMic/specs/005-auto-uninstall-old-version/data-model.md)

**Tests**: 由于 Windows 安装程序（NSIS 脚本）运行于真实的 Windows 系统及注册表环境中，Linux 宿主开发环境无法运行相关的 TDD 自动化测试；验证将通过在 Windows 环境下手动执行 [quickstart.md](file:///home/coding/workspace/PhoneMic/specs/005-auto-uninstall-old-version/quickstart.md) 中的端到端测试用例完成。

**Organization**: 任务按优先级和用户故事划分为不同阶段，以确保每一阶段的功能都是可独立验证和交付的。

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 准备本地 NSIS 构建环境。

- [ ] T001 确保 Windows 测试机的 NSIS 编译器 `makensis` 可用并配置于 `PATH` 中

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 为安全修改脚本做前置工作。

- [ ] T002 创建原始安装配置文件的备份 `makesetup.nsi.bak` 以便回滚

---

## Phase 3: User Story 4 - 运行中进程前置拦截 (Priority: P1)

**Goal**: 在安装包启动的最开头检测 PhoneMic 是否在运行，如果是则强行拦截并退出，防止文件覆盖失败或重复弹窗。

- [ ] T003 [US4] 在 `makesetup.nsi` 的 `.onInit` 函数最开头编写使用 `FindWindow` 检测 `"PhoneMic"` 句柄的逻辑，若运行则弹出警告并 Abort 退出。
- [ ] T004 [US4] 依照 `specs/005-auto-uninstall-old-version/quickstart.md` 中的“场景 2”手动验证进程占用前置拦截，确保在程序运行时仅弹窗一次便安全退出。

---

## Phase 4: User Story 1 & 2 - 自动检测旧版本并选择性升级 (Priority: P1 & P2) 🎯 MVP

**Goal**: 检测注册表以确认是否已安装旧版本；若存在，弹窗提示用户确认卸载。选择“是”则同步静默调用旧卸载器，选择“否”则退出。

- [ ] T005 [US1] 在 `makesetup.nsi` 的 `.onInit` 进程检测通过后，增加读取注册表 `HKLM` 检测旧版 `UninstallString` 和 `InstallLocation` 的逻辑。
- [ ] T006 [US1] 在 `.onInit` 中增加 `MessageBox MB_YESNO` 弹窗提示，当用户选择“是”时，使用 `ExecWait` 配合 `_?=` 语法同步且静默地运行旧版 `uninst.exe`。
- [ ] T007 [US2] 在 `.onInit` 中编写用户选择“否”的分支，弹出提示“升级安装已取消”并调用 `Abort` 退出。
- [ ] T008 [US1] 依照 `specs/005-auto-uninstall-old-version/quickstart.md` 验证“场景 1”、“场景 3”和“场景 4”，确保正常升级完成且个人配置文件未被删除，拒绝升级时安装能正确取消。

---

## Phase 5: User Story 3 - 卸载器丢失与失败故障容错 (Priority: P3)

**Goal**: 在旧版卸载器丢失或执行失败时进行安全拦截和提示，不强行覆盖。

- [ ] T009 [US3] 在 `makesetup.nsi` 决定卸载旧版后，前置校验 `uninst.exe` 是否存在。若丢失，弹窗指导用户手动删除安装路径，并调用 `Abort` 退出。
- [ ] T010 [US3] 在 `makesetup.nsi` 运行静默卸载后，再次利用 `IfFileExists` 检验 `uninst.exe` 是否已消失。若依然存在（表示卸载失败），弹出警告并 Abort。
- [ ] T011 [US3] 依照 `specs/005-auto-uninstall-old-version/quickstart.md` 验证“场景 5”，在手动删除 `uninst.exe` 但注册表残留时，确保安装包能给出具体路径的删除指引并安全终止。

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 收尾与彻底的交叉验证。

- [ ] T012 清除 `makesetup.nsi.bak` 备份文件并整理 `makesetup.nsi` 的最终代码格式
- [ ] T013 执行 [quickstart.md](file:///home/coding/workspace/PhoneMic/specs/005-auto-uninstall-old-version/quickstart.md) 中所有 5 大验证场景的最终回归测试
- [ ] T014 编写并输出 [walkthrough.md](file:///home/coding/workspace/PhoneMic/specs/005-auto-uninstall-old-version/walkthrough.md) 最终验证报告

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (Phase 1)**: 无依赖，率先准备好环境。
2. **Foundational (Phase 2)**: 依赖 Setup 完成，主要是文件备份，必须在正式改动代码前完成。
3. **User Stories (Phases 3~5)**: 依赖 Foundational 完成。
   - 顺序：运行中进程拦截 (Phase 3) → 升级/取消升级主流程 (Phase 4) → 丢失卸载器故障拦截 (Phase 5)。
4. **Polish (Phase 6)**: 依赖所有 User Stories 开发并单测/手测通过后开始。

### Parallel Opportunities

- 由于安装逻辑都在 `makesetup.nsi` 的 `.onInit` 内逐步编写，前后任务有逻辑递进关系，故本特性的具体代码编写应以**串行顺序**进行，手测验证也建议顺次执行。

---

## Implementation Strategy

### MVP First (User Story 1 & 4)

1. 完成 Phase 1 (环境准备) 与 Phase 2 (备份)。
2. 完成 Phase 3 (进程前置拦截) 并做本地拦截测试。
3. 完成 Phase 4 (主升级流程) 并做正常升级/取消升级测试。确保 MVP 功能安全上线。
4. 在 MVP 稳定后，再进行 Phase 5 (异常与卸载器丢失容错) 的补充开发。
