# Claude Code Hooks 学习指南

## 什么是 Hooks？

**Hooks（钩子）** 是在 Claude Code 执行特定操作时自动触发的 shell 命令。

你可以把它想象成"事件监听器"：
- 当 Claude **准备编辑文件之前** → 触发 `PreToolUse` hook
- 当 Claude **编辑完文件之后** → 触发 `PostToolUse` hook
- 当 Claude **会话开始时** → 触发 `SessionStart` hook

## 为什么需要 Hooks？

1. **自动化**: 自动格式化代码、运行 linter
2. **安全控制**: 阻止修改敏感文件（如 .env）
3. **日志记录**: 记录 Claude 的所有操作
4. **集成工具**: 与现有开发工具链集成

## Hook 类型一览

| 事件名 | 触发时机 | 常见用途 |
|--------|----------|----------|
| `SessionStart` | 会话开始时 | 加载环境变量、显示欢迎信息 |
| `PreToolUse` | 工具执行**前** | 阻止危险操作、验证输入 |
| `PostToolUse` | 工具执行**后** | 自动格式化、运行测试 |
| `Notification` | 需要通知时 | 发送桌面通知 |
| `Stop` | Claude 完成响应时 | 检查任务是否完成 |

## 项目结构说明

```
.claude/
├── settings.json          # Hook 配置文件
└── hooks/
    ├── before-edit.sh     # 编辑前触发的脚本
    ├── after-edit.sh      # 编辑后触发的脚本
    ├── after-bash.sh      # 命令执行后触发的脚本
    └── hook.log           # 日志文件（运行后自动生成）
```

## 配置文件详解

查看 `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [           // ← 事件名称
      {
        "matcher": "Edit|Write",  // ← 只匹配 Edit 和 Write 工具
        "hooks": [
          {
            "type": "command",     // ← hook 类型：shell 命令
            "command": "bash ...", // ← 要执行的命令
            "timeout": 10          // ← 超时时间（秒）
          }
        ]
      }
    ]
  }
}
```

## Hook 脚本如何工作

### 1. 输入：从 stdin 读取 JSON

Claude 会通过 stdin 传递工具调用信息：

```json
{
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/path/to/file.js",
    "old_string": "...",
    "new_string": "..."
  }
}
```

### 2. 处理：解析并执行逻辑

```bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path')
```

### 3. 输出：通过退出码控制行为

| 退出码 | 含义 |
|--------|------|
| `exit 0` | 成功，继续执行 |
| `exit 2` | **阻止**工具执行（仅 PreToolUse） |
| 其他 | 出错，但不阻止 |

## 实际例子

### 例子 1：阻止修改 .env 文件

```bash
if [[ "$FILE_PATH" == *".env"* ]]; then
    echo "不允许修改 .env 文件！" >&2
    exit 2  # 阻止操作
fi
```

### 例子 2：自动格式化 JavaScript

```bash
if [[ "$FILE_PATH" == *.js ]]; then
    npx prettier --write "$FILE_PATH"
fi
```

### 例子 3：发送桌面通知（Notification hook）

```json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude' '需要你的注意！'"
          }
        ]
      }
    ]
  }
}
```

## 如何测试 Hooks

1. 查看日志文件:
   ```bash
   cat .claude/hooks/hook.log
   ```

2. 在 Claude Code 中输入 `/hooks` 可以交互式管理 hooks

## 进阶：三种 Hook 类型

### 1. Command Hook（命令钩子）
执行 shell 命令，最常用。

### 2. Prompt Hook（提示钩子）
让 LLM 做判断：
```json
{
  "type": "prompt",
  "prompt": "检查代码是否有安全问题"
}
```

### 3. Agent Hook（智能体钩子）
生成子智能体进行复杂验证：
```json
{
  "type": "agent",
  "prompt": "运行测试并验证结果"
}
```

## 总结

Hooks 让你能够：
- ✅ 在 Claude 操作的**前后**插入自定义逻辑
- ✅ **阻止**危险或不想要的操作
- ✅ **自动化**重复性任务
- ✅ **记录**所有操作到日志

这是一种确定性的控制方式，比让 LLM 自己"记住规则"更可靠！
