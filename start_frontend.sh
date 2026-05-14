#!/bin/bash

echo "========================================"
echo "Starting Frontend (Next.js)..."
echo "========================================"

cd frontend

# 使用独立前端端口，并把浏览器端 API URL 显式指向本项目后端。
FRONTEND_PORT="${FRONTEND_PORT:-$(grep -E '^FRONTEND_PORT=' ../.env 2>/dev/null | tail -n 1 | cut -d= -f2-)}"
API_PORT="${API_PORT:-$(grep -E '^API_PORT=' ../.env 2>/dev/null | tail -n 1 | cut -d= -f2-)}"
FRONTEND_PORT="${FRONTEND_PORT:-39211}"
API_PORT="${API_PORT:-48217}"
export PORT="$FRONTEND_PORT"
export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:$API_PORT}"

echo "Frontend Port: $PORT"
echo "Backend API URL: $NEXT_PUBLIC_API_URL"

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm install
    echo "✅ Dependencies installed."
fi

npm run dev -- -p "$PORT"
