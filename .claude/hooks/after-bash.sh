#!/bin/bash
# ==============================================================================
# Hook 示例 3: PostToolUse (Bash) - 在执行命令之后执行
# ==============================================================================
#
# 这个 hook 会在 Claude 执行 Bash 命令后被触发
# 可用于：
#   - 记录命令执行历史
#   - 检查命令结果
#   - 清理临时文件

# 读取 stdin 中的 JSON 数据
INPUT=$(cat)

# 解析执行的命令
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // "unknown"' 2>/dev/null)
# 截取前50个字符用于日志
COMMAND_SHORT=$(echo "$COMMAND" | head -c 50)

# 记录到日志
LOG_FILE="$CLAUDE_PROJECT_DIR/.claude/hooks/hook.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bash executed: $COMMAND_SHORT..." >> "$LOG_FILE"

exit 0
