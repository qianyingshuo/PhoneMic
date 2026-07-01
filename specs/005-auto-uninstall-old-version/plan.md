# Implementation Plan: 安装时自动检测并提示卸载旧版本

**Branch**: `005-auto-uninstall-old-version` | **Date**: 2026-07-01 | **Spec**: [spec.md](file:///home/coding/workspace/PhoneMic/specs/005-auto-uninstall-old-version/spec.md)

## Summary

本计划用于在 PhoneMic 编译打包阶段（NSIS 安装包脚本 [makesetup.nsi](file:///home/coding/workspace/PhoneMic/makesetup.nsi)）引入旧版本检测和同步自动卸载逻辑。

当用户运行新版本的安装包时：
1. **进程拦截**：首先利用 `FindWindow` API 检测旧版的 `PhoneMic.exe` 是否在后台运行。如果正在运行，弹出错误窗前置阻断，提示用户关闭后退出，实现单次弹窗保护。
2. **版本检测**：进程检测通过后，读取注册表以检测是否存在旧版本。若存在旧版本，提示用户确认是否卸载旧版本进行干净的升级安装（同时说明此操作会保留其个人配置）。
3. **静默卸载**：如果用户确认，同步调用旧版卸载器并使用 `_?=` 确保同步等待，直到旧版完全清空，再继续执行新版写入。
4. **异常容错**：如果旧版卸载器丢失或执行失败，弹出明确的指引窗提示用户手动清理安装目录，并截断（终止）当前新版的安装。

---

## Technical Context

**Language/Version**: NSIS (Nullsoft Scriptable Install System) v3.x

**Primary Dependencies**: NSIS 编译器 (makensis)

**Storage**: Windows 注册表 (`HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\PhoneMic`) 

**Testing**: 手动验证（由于 NSIS 脚本执行深度绑定 Windows 注册表和系统环境，无法在 Linux 开发环境下开展 pytest 单元测试，因此使用多场景端到端手动验证）。

**Target Platform**: Windows 7 / 10 / 11

**Project Type**: setup-installer / desktop-app

**Performance Goals**: 进程检测和卸载调度在 5 秒内完成，且必须为同步等待。

**Constraints**: 需要管理员权限（`RequestExecutionLevel admin`）。

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 宪章原则 | 检查状态 | 说明 |
| :--- | :--- | :--- |
| **原则 I. 核心逻辑解耦与 API-First** | **Passed (免检)** | 本特性为安装部署包构建控制，不涉及 Python 业务层级及 FastAPI 接口逻辑。 |
| **原则 II. 平台差异抽象与可打桩设计**| **Passed (免检)** | 修改纯属 Windows 端的 NSIS 安装逻辑，与 Python 运行时的跨平台测试无交集。 |
| **原则 III. 测试驱动开发 (TDD 铁律)** | **Violation** | **由于环境限制无法实施 TDD 单元测试**。NSIS 构建脚本原生在 Windows 下编译和执行，无法在 Linux 容器/开发机中通过 pytest 编写和运行单元测试。 |
| **原则 IV. 多端安全防护与输入防御** | **Passed** | 卸载与安装调用均通过注册表拿到的绝对路径进行（无拼接外部注入入参），且进行了安装路径安全校验，防止提权与系统注入。 |

---

## Project Structure

### Documentation (this feature)

```text
specs/005-auto-uninstall-old-version/
├── plan.md              # This file
├── research.md          # Technical research and Decisions
├── data-model.md        # System states and Registry entities
└── quickstart.md        # End-to-End manual verification guide
```

### Source Code (repository root)

```text
makesetup.nsi            # [MODIFY] NSIS 安装程序配置文件，需在此处新增 .onInit 逻辑
```

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 缺乏 TDD 单元测试 | NSIS 构建脚本非 Python 代码，且运行时强耦合 Windows 操作系统环境、句柄搜索与注册表读写。Linux 开发机环境下无法为 Windows 安装包编写自动化测试。 | 无。安装部署逻辑的变更只能通过端到端手动运行场景用例进行彻底覆盖。 |
