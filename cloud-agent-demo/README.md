# Cloud Agent 计数器演示

无外部依赖的静态网页计数器，用于 Cloud Agent 核心流程验证。

## 功能

- 初始值 **0**，支持 **+1**、**−1**、**重置**
- 取值范围 **0–10**；为 0 时禁用减号，为 10 时禁用加号；已为 0 时禁用重置

## 运行测试

```bash
cd cloud-agent-demo
./run-tests.sh
# 或
node --test test.mjs
```

## 本地预览

在仓库根目录或本目录下启动静态服务，例如：

```bash
cd cloud-agent-demo
python3 -m http.server 8765
```

浏览器打开 `http://127.0.0.1:8765/` 即可。

## 文件说明

| 文件 | 说明 |
|------|------|
| `counter.js` | 计数逻辑（浏览器 + Node 测试共用） |
| `app.js` | DOM 绑定 |
| `index.html` / `styles.css` | 简洁中文界面 |
| `test.mjs` | Node 内置测试 |
| `run-tests.sh` | 测试入口脚本 |
