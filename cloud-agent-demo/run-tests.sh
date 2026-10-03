#!/usr/bin/env bash
# 可重复运行的单元测试（仅依赖 Node 内置 test 模块）
set -euo pipefail
cd "$(dirname "$0")"
node --test test.mjs
