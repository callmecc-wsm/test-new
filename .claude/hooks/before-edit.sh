#!/bin/bash
# ==============================================================================
# Hook 示例 1: PreToolUse - 在编辑文件之前执行
# ==============================================================================
#
# 这个 hook 会在 Claude 使用 Edit 或 Write 工具之前被触发
# 它可以：
#   - 检查文件是否应该被编辑
#   - 记录日志
#   - 阻止某些操作（通过 exit 2）
#
# Claude 会通过 stdin 传入 JSON 数据，包含工具信息

# 读取 stdin 中的 JSON 数据
INPUT=$(cat)

# 使用 jq 解析文件路径（如果有的话）
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // "unknown"' 2>/dev/null)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null)

# 记录到日志文件
LOG_FILE="$CLAUDE_PROJECT_DIR/.claude/hooks/hook.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] PreToolUse: $TOOL_NAME on $FILE_PATH" >> "$LOG_FILE"

# 示例：阻止修改 .env 文件（取消注释下面的代码来启用）
# if [[ "$FILE_PATH" == *".env"* ]]; then
#     echo "警告：不允许修改 .env 文件！" >&2
#     exit 2  # exit 2 会阻止工具执行
# fi

# exit 0 表示允许继续
exit 0
