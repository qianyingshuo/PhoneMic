<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/004-key-mappings-redesign/plan.md
<!-- SPECKIT END -->

> [!NOTE]
> 本文件仅承载最核心、高 Token 敏感的智能体**运行期操作红线与物理禁区**（以供每次会话自动加载强规则）。  
> 详细的技术实施原则、各生命周期阶段工作流与 HTP 1.1 层级全链路日志追踪协议，请参见项目的宪章文件 [.specify/memory/constitution.md](file:///home/coding/workspace/PhoneMic/.specify/memory/constitution.md)。

# PhoneMic 开发规约与智能体行为限制 (Project AGENT Rules)

所有参与本项目开发与维护的智能体必须无条件遵守本文件所载之强约束规则。

## 1. 测试驱动开发 (TDD 铁律)
- **无失败测试，则无生产代码**：在编写任何功能代码或修复 Bug 前，**必须先有且仅有一个失败的测试用例**。若 Git 提交历史中没有对应的 Failing 测试（RED 阶段）记录，该段生产代码被视为违规代码，必须撤销重做。
- 严格遵循 `RED (编写报错测试) -> GREEN (写极简代码使测试通过) -> REFACTOR (重构并保持全绿)` 的微循环来销掉任务。

## 2. 智能体行为与权限限制
### 2.1 主智能体 (Main Agent) 的限制
- **严禁越权合并与推送**：主智能体在未获得用户在聊天窗口中明确的、包含“同意合并/推送/Merge/Push”等肯定动作指令前，**绝对禁止**执行任何分支合并（`git merge`）与向远程 `main` 或其他保护分支进行推送（`git push`）的操作。在开发或子智能体交付完毕后，主智能体应自动将当前的特性开发分支同步推送（`git push`）至远程仓库以做备份与评审展示。
- **强制评审展示**：在开发或子智能体交付完毕后，必须以 Markdown 格式完整呈现验证报告（`walkthrough.md`），重点展示单元测试通过率及核心代码 Diff，引导用户进行 Code Review。

### 2.2 子智能体 (Subagent) 的限制
- **工作空间与分支封禁**：子智能体只被授予在当前指派的特性分支内修改代码、执行本地验证和本地 Git Commit 的权限。
- **越权动作绝对禁止**：子智能体**绝对禁止**执行 `git checkout` 切换分支、`git merge` 合并分支、以及 `git push` 推送至远程仓库的操作。
- **无条件休眠与打报告**：子智能体在完成所有任务、生成本地 `walkthrough.md` 验证文档并完成本地 commit 后，必须立即停止任何工具调用（进入 Idle 状态），通过 `send_message` 向主智能体报告，绝对不许自行做任何跨阶段的收尾工作。

## 3. 平台差异抽象与可打桩设计
- 针对 Windows 原生 API（`pywin32`）或可能阻塞键盘的 `keyboard`、`pyautogui` 操作，必须使用抽象层进行包装，以保证测试可以在非 Windows/无 GUI 的容器环境（如 Linux 自动化测试环境）中通过打桩（Mock）正常全绿通过。
