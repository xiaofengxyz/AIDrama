#!/bin/bash

# 阿里云服务不走代理（避免PAC配置被Python忽略）
# macOS系统代理会被requests库读取，但PAC规则不会被解析
# 显式设置NO_PROXY确保阿里云域名直连
export NO_PROXY="*.aliyuncs.com,localhost,127.0.0.1"
export no_proxy="*.aliyuncs.com,localhost,127.0.0.1"

echo "========================================"
echo "Starting Backend (FastAPI)..."
echo "Proxy Bypass: *.aliyuncs.com"
echo "========================================"

# 确保在项目根目录
cd "$(dirname "$0")"

# 使用本项目独立端口，避免与其他项目的常用 3000/8000/17177 端口冲突。
API_HOST="${API_HOST:-$(grep -E '^API_HOST=' .env 2>/dev/null | tail -n 1 | cut -d= -f2-)}"
API_PORT="${API_PORT:-$(grep -E '^API_PORT=' .env 2>/dev/null | tail -n 1 | cut -d= -f2-)}"
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-48217}"
export LLM_PROVIDER="${LLM_PROVIDER:-dashscope}"
export OPENAI_MODEL="${OPENAI_MODEL:-qwen-plus}"

echo "Host: $API_HOST"
echo "Port: $API_PORT"
echo "LLM Provider: $LLM_PROVIDER"

# 启动 uvicorn
python -m uvicorn src.apps.comic_gen.api:app --reload --port "$API_PORT" --host "$API_HOST"
