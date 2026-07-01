# WebSocket Communication Contract: key-mappings-redesign

## 1. 消息协议流向

### 1.1 发送文本与追加按键 (文本非空)
当输入框中有字时，手机端通过 WebSocket 发送格式如下：

- **Type**: `send`
- **Direction**: Client -> Server
- **Payload Format**:
  ```json
  {
    "type": "send",
    "text": "输入的文本内容",
    "key_mapping_id": "8f8e02d8-5527-4632-a54f-124b13e9a9db",
    "key_sequence": "enter"
  }
  ```

### 1.2 单独模拟按键 (文本为空)
当输入框中无字（或全为空格）时，用户点击发送或敲键盘回车，手机端通过 WebSocket 发送格式如下：

- **Type**: `send`
- **Direction**: Client -> Server
- **Payload Format**:
  ```json
  {
    "type": "send",
    "text": "",
    "key_mapping_id": "9a38f381-12cd-41ef-8b89-21a4bc5a3a22",
    "key_sequence": "tab"
  }
  ```

---

## 2. 约束说明
- 若 `text` 是空字符串 `""`，且 `key_mapping_id` 也是 `"none"`，客户端将执行本地拦截，禁止向 WebSocket 链路发出任何请求。
- 服务端（PC 侧）接收到 `text == ""` 消息时，其 `flash_insert` 函数应该在做安全前置判断后无害返回，而 `send_keys` 应该正常处理并触发模拟按键。
