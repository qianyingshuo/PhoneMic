# WSS 协议自适应设计规约

## 1. 背景与目标
PhoneMic 默认在局域网内通过 HTTP 协议运行，手机端通过 `ws://` 协议连接电脑端。
在未来扩展外网安全访问时（例如部署 Cloudflare Tunnel 或 Tailscale Funnel），网页会被加载为 `https://`。由于浏览器的安全限制，在 HTTPS 网页中禁止连接未加密的 `ws://`，必须使用加密的 `wss://`。

本规约的目标是：在保持局域网内 HTTP 扫码即用（无需配置证书）的前提下，让前端网页在 HTTPS 访问时自动采用 `wss://` 连接。

---

## 2. 变更方案

### 手机网页端

#### [MODIFY] [mobile.html](file:///home/coding/workspace/PhoneMic/phonemic/resources/mobile.html)

定位到文件中实例化 `WSClient` 建立连接的代码（约第 729 行）：

```javascript
const wsClient = new WSClient(`ws://${window.location.host}/ws`, appConfig);
```

将其修改为使用自适应的协议头：

```javascript
// 根据当前网页加载协议自动决定使用 wss:// 还是 ws://
const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsClient = new WSClient(`${wsProto}//${window.location.host}/ws`, appConfig);
```

---

## 3. 验证计划

### 自动与手工测试
1. **局域网回退测试（HTTP）**：
   - 正常启动 PhoneMic。
   - 使用手机扫码（URL 为 `http://<LAN_IP>:7979`）进行连接。
   - 确认手机网页能正常连接电脑，并能够进行语音输入。
2. **安全连接测试（HTTPS 理论校验）**：
   - 确认当 `window.location.protocol` 的值为 `"https:"` 时，算出的 `wsProto` 为 `"wss:"`，构造出的 WebSocket 客户端地址为 `wss://<HOST>/ws`。
