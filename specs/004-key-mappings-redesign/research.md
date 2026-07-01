# Research & Technical Decisions: key-mappings-redesign

## 1. 技术决策汇总 (Technical Decisions)

| 决策点 (Decision Point) | 选定方案 (Selected Solution) | 决策理由 (Rationale) | 考虑过的其他备选方案 (Alternatives) |
| :--- | :--- | :--- | :--- |
| **多通道前端逻辑分流** | 在 `UIController` 前端判断 `inputBox.value.trim() === ''` 分流发送 | **轻量、低侵入**：完全由前端做分流，在空输入时发送带 key mapping payload 的空文本，PC 后端逻辑完全无需任何改动，实现最小代码变动。 | 在 Python 后端处理判定：会破坏 FastAPI 路由的高内聚性并增加复杂的逻辑，故放弃。 |
| **状态持久化机制** | 原生 `window.localStorage` 持久化存储 | **简单高效**：使用原生 LocalStorage api 分别存储 `selected_key_mapping_id` 与 `selected_single_key_mapping_id`，浏览器沙箱安全且自动恢复状态。 | 使用 IndexedDB：过于复杂，轻量级状态存储不适用，故放弃。 |
| **界面按钮移除** | 完全移除 `btn-send-mapping` 元素 | **极简设计**：复用底栏发送键和键盘回车，界面不再显示杂乱的冗余控制按钮。 | 保留微型发射图标：界面仍有杂音，不符合极致无噪原则。 |

---

## 2. 核心架构判定
由于本项目已包含完整的 FastAPI + PySide6 双端通信系统，重构时必须严格保障**向下兼容性**：
- 前端向 WebSocket 发送的消息类型仍保持 `send`。
- 如果是单独发送按键，Payload 中 `text` 将传空字符串 `""`，后端读取到空字符串时，会自动忽略剪贴板操作，只触发 `send_keys(key_sequence)` 模拟，无任何破坏性变更。
