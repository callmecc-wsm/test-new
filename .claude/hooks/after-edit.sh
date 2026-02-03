#!/bin/bash
# ==============================================================================
# Hook 示例 2: PostToolUse - 在编辑文件之后执行
# ==============================================================================
#
# 这个 hook 会在 Claude 成功使用 Edit 或 Write 工具之后被触发
# 常见用途：
#   - 自动格式化代码（prettier, black, gofmt 等）
#   - 运行 linter 检查
#   - 更新相关文件
#   - 发送通知

# 读取 stdin 中的 JSON 数据
INPUT=$(cat)

# 解析信息
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // "unknown"' 2>/dev/null)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null)

# 记录到日志
LOG_FILE="$CLAUDE_PROJECT_DIR/.claude/hooks/hook.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] PostToolUse: $TOOL_NAME completed on $FILE_PATH" >> "$LOG_FILE"

# 示例：如果是 JavaScript/TypeScript 文件，可以自动运行 prettier
# （取消注释来启用）
# if [[ "$FILE_PATH" == *.js ]] || [[ "$FILE_PATH" == *.ts ]]; then
#     npx prettier --write "$FILE_PATH" 2>/dev/null
#     echo "已自动格式化: $FILE_PATH"
# fi

exit 0
