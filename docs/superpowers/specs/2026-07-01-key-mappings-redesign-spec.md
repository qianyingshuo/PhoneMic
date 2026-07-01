# PhoneMic 手机端双按键映射通道重构设计 (Spec)

## 1. 需求背景与痛点
原本的按键映射功能存在逻辑冲突：只有一个按键映射选择器。当用户选择某个按键（如 `Tab`）时，每次发送语音或文字都会自动追加该按键。如果用户只想在个别时候单独发送一次 `Tab`，就必须频繁去修改这个下拉框，这导致了“常驻自动追加”与“单独临时触发”功能严重耦合，使用极其不便。

为了彻底解决这一冲突，我们对手机端界面和发送逻辑进行重构，将两种行为在通道上进行**完全解耦**。

---

## 2. 界面排版变动
主界面底部操作栏（输入框上方）重新设计，提供以下两行极简控制选项：

1. **⚡ 发送时追加** (`#key-mapping-select`)
   - 下拉选择框，用于配置正常发送文本时，在文本句尾自动模拟的按键。
   - 默认值为 `none`（无，不追加）。
   - 移除了上一版右侧冗余的“输入时自动追加”提示文本块，让控件宽度自适应，排版更整洁。
2. **🎯 单独发按键** (`#single-key-mapping-select` [NEW])
   - 下拉选择框，用于配置在输入框为空时，点击发送要单独触发的按键。
   - 默认值为 `none`（无，不发送）。
   - **完全不提供任何独立的 `🚀` 物理发送按钮**，纯靠底栏主发送按钮及输入法键盘回车分流触发。

---

## 3. 核心分流控制逻辑
在前端 JavaScript 中，针对『发送』动作（包括点击绿色『发送』按钮、以及在输入框中敲击键盘『Enter』回车）进行如下基于文本状态的逻辑分流：

```javascript
// 发送动作分流伪代码
function onSendAction() {
    const text = inputBox.value.trim();
    
    if (text !== '') {
        // 1. 输入框非空：发送当前文本，并追加“追加映射选择器”的值
        const select = document.getElementById('key-mapping-select');
        const opt = select.options[select.selectedIndex];
        const keyMappingId = opt ? opt.value : 'none';
        const keySequence = opt ? (opt.getAttribute('data-keys') || '') : '';
        
        wsClient.send('send', text, {
            key_mapping_id: keyMappingId,
            key_sequence: keySequence
        });
        chatManager.addMessage(text);
        inputBox.value = '';
    } else {
        // 2. 输入框为空：单独发送一次“单独按键映射选择器”的值
        const singleSelect = document.getElementById('single-key-mapping-select');
        const opt = singleSelect.options[singleSelect.selectedIndex];
        const keyMappingId = opt ? opt.value : 'none';
        const keySequence = opt ? (opt.getAttribute('data-keys') || '') : '';
        
        if (keyMappingId === 'none' || !keySequence) {
            // 若为“无”，空输入框发送则不产生任何响应
            return;
        }
        
        wsClient.send('send', '', {
            key_mapping_id: keyMappingId,
            key_sequence: keySequence
        });
        chatManager.addMessage(`[单独发送按键] ${opt.textContent} (${keySequence})`);
    }
}
```

### 离线状态与可用性判定
- 当网页断开连接时，追加下拉框、单独发送下拉框以及底部输入框、发送按钮统一被禁用（`disabled = true`）。
- 在连接状态下，即使输入框为空，『发送』按钮也**别禁用变灰**，除非“单独发按键”下拉框和“追加按键”下拉框同时均设为了 `none`。

---

## 4. 自动化测试计划
1. **HTML 静态内容测试**：
   - 验证 `mobile.html` 中包含 `key-mapping-select` 元素。
   - 验证 `mobile.html` 中包含新定义的 `single-key-mapping-select` 元素。
   - 验证 `mobile.html` 中**不包含**上一版已弃用的 `btn-send-mapping` 元素。
2. **逻辑分流静态检查**：
   - 验证 JS 代码中同时支持读取两个下拉框的值，并根据 `value.trim() === ''` 进行分流发送的特征关键字匹配。
