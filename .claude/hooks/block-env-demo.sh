#!/bin/bash
# 演示：阻止修改 .env 文件的 hook

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // "unknown"' 2>/dev/null)

# 检查是否是 .env 文件
if [[ "$FILE_PATH" == *".env"* ]]; then
    echo "🚫 警告：不允许修改 .env 文件！这可能泄露敏感信息！" >&2
    exit 2  # exit 2 会阻止工具执行
fi

echo "✅ 允许编辑: $FILE_PATH"
exit 0
