# Hook 类型详解：Command vs Prompt vs Agent

## 概述

Claude Code 提供三种 Hook 类型，适用于不同场景：

| 类型 | 执行者 | 能力 | 适用场景 |
|------|--------|------|----------|
| **Command** | Shell 脚本 | 执行系统命令 | 格式化、日志、简单检查 |
| **Prompt** | LLM (单次) | 理解语义 | 需要"理解"的判断 |
| **Agent** | 子智能体 (多轮) | 使用工具 | 复杂验证、多步骤检查 |

---

## 1. Command Hook（命令钩子）

### 工作原理
```
事件触发 → 执行 Shell 脚本 → 根据退出码决定后续
```

### 配置示例
```json
{
  "type": "command",
  "command": "bash /path/to/script.sh",
  "timeout": 10
}
```

### 适用场景
- ✅ 运行 `prettier` 格式化代码
- ✅ 检查文件名是否匹配模式
- ✅ 记录操作日志
- ✅ 发送通知

### 优点
- 执行速度快
- 完全确定性
- 不消耗 AI token

### 缺点
- 只能做字符串匹配，无法"理解"内容
- 需要会写 Shell 脚本

---

## 2. Prompt Hook（提示钩子）

### 工作原理
```
事件触发 → 发送提示给 LLM → LLM 返回 JSON 判断 → 根据结果决定后续
```

### 配置示例
```json
{
  "type": "prompt",
  "prompt": "检查这个命令是否安全: $ARGUMENTS。如果危险返回 {\"ok\": false, \"reason\": \"原因\"}，否则返回 {\"ok\": true}",
  "timeout": 30
}
```

### 关键点：`$ARGUMENTS` 变量
- 在 `PreToolUse` 中：包含工具输入参数
- 在 `PostToolUse` 中：包含工具输出结果
- 在 `Stop` 中：包含对话历史摘要

### 适用场景
- ✅ 判断命令是否"危险"（需要理解语义）
- ✅ 检查代码修改是否合理
- ✅ 验证任务是否真正完成

### 返回格式
LLM 必须返回 JSON：
```json
{"ok": true}                           // 允许继续
{"ok": false, "reason": "不安全的操作"} // 阻止并说明原因
```

### 优点
- 能"理解"内容，不只是字符串匹配
- 无需编写复杂脚本

### 缺点
- 消耗 AI token
- 有一定延迟
- 单次判断，无法执行多步骤

---

## 3. Agent Hook（智能体钩子）

### 工作原理
```
事件触发 → 生成子智能体 → 智能体可使用工具(多轮) → 返回验证结果
```

### 配置示例
```json
{
  "type": "agent",
  "prompt": "验证代码质量：1) 用 Grep 搜索 console.log 2) 用 Read 检查语法。发现问题返回 {\"ok\": false}",
  "timeout": 120
}
```

### 子智能体可用的工具
- `Read` - 读取文件
- `Grep` - 搜索代码
- `Glob` - 查找文件
- ❌ 不能使用 `Edit`、`Write`、`Bash`（只读操作）

### 适用场景
- ✅ 运行测试并检查结果
- ✅ 搜索代码库验证一致性
- ✅ 读取多个文件进行交叉验证
- ✅ 复杂的代码审查

### 优点
- 最强大，可执行多步骤验证
- 可以读取文件系统
- 能做复杂推理

### 缺点
- 消耗最多 token
- 延迟最高
- 需要合理设置 timeout

---

## 实际对比示例

### 场景：检查是否有危险的 rm 命令

**方式 1: Command Hook**
```bash
# 只能做简单字符串匹配
if echo "$COMMAND" | grep -q "rm -rf"; then
    exit 2
fi
```
问题：无法识别 `rm -r -f` 或 `rm --recursive --force`

**方式 2: Prompt Hook**
```json
{
  "type": "prompt",
  "prompt": "判断这个命令是否会删除文件: $ARGUMENTS"
}
```
优势：能理解各种变体写法

**方式 3: Agent Hook**
```json
{
  "type": "agent",
  "prompt": "分析命令 $ARGUMENTS：1) 识别要删除的路径 2) 用 Glob 检查这些路径是否存在重要文件 3) 评估风险"
}
```
优势：不仅理解命令，还能检查实际会影响哪些文件

---

## 如何选择？

```
                    需要理解语义吗？
                         │
           ┌─────────────┴─────────────┐
           │ 否                        │ 是
           ▼                           ▼
      Command Hook              需要多步骤/读文件吗？
     (简单快速)                        │
                         ┌─────────────┴─────────────┐
                         │ 否                        │ 是
                         ▼                           ▼
                    Prompt Hook                 Agent Hook
                   (单次判断)                 (复杂验证)
```

---

## 完整配置示例

将三种 hook 组合使用：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/log-command.sh"
          },
          {
            "type": "prompt",
            "prompt": "这个命令安全吗: $ARGUMENTS"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $(echo '$ARGUMENTS' | jq -r '.file_path')"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "验证所有修改的文件没有语法错误，运行相关测试",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

---

## 调试技巧

1. **查看 hook 执行日志**：在 command hook 中写入日志文件
2. **测试 prompt**：先在普通对话中测试你的判断提示
3. **设置合理 timeout**：agent hook 需要更长时间
4. **从简单开始**：先用 command hook，需要时再升级

---

## 总结

| 问题 | 选择 |
|------|------|
| 只需要字符串匹配？ | Command |
| 需要理解含义？ | Prompt |
| 需要读文件/多步骤？ | Agent |
| 追求速度？ | Command |
| 追求准确性？ | Agent |
