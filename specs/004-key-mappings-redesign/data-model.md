# Data Model Definition: key-mappings-redesign

本重构功能仅在前端手机网页端存在持久化数据存储，继续沿用 PC 端通过 `settings.json` 管理按键映射列表的既有设计。

## 1. 手机端 LocalStorage 数据模型

手机端通过浏览器的 `window.localStorage` 独立缓存用户在两个下拉框中的选项值，防止刷新或重载页面时丢失选择。

### 1.1 发送时追加缓存 (`selected_key_mapping_id`)
- **存储键名**: `selected_key_mapping_id`
- **存储类型**: String (UUIDv4)
- **取值约束**: 
  - 必须等于后端推送的按键映射列表项中的 `id`。
  - 特殊值 `"none"` 代表不追加（默认值）。
- **更新时机**: 当用户切换 `#key-mapping-select` 下拉选择框时更新。

### 1.2 单独发按键缓存 (`selected_single_key_mapping_id`)
- **存储键名**: `selected_single_key_mapping_id` [NEW]
- **存储类型**: String (UUIDv4)
- **取值约束**: 
  - 必须等于后端推送的按键映射列表项中的 `id`。
  - 特殊值 `"none"` 代表无映射（默认值）。
- **更新时机**: 当用户切换 `#single-key-mapping-select` 下拉选择框时更新。
