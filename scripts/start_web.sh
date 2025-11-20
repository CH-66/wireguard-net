#!/bin/sh
# FastAPI Web服务器启动脚本

echo "========================================"
echo "WireGuard Network Toolkit - Web API"
echo "========================================"
echo ""

# 添加本地bin目录到PATH
PATH="$HOME/.local/bin:$PATH"
export PATH

echo "Debug: PATH=$PATH"
echo "Debug: HOME=$HOME"

# 检查是否在项目根目录
if [ ! -f "pyproject.toml" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查Python环境
if ! command -v uv > /dev/null 2>&1; then
    echo "错误: 未找到uv命令"
    echo "请先安装uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 默认配置
HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-8080}"
RELOAD="${API_RELOAD:-true}"

echo "配置信息:"
echo "  监听地址: $HOST"
echo "  监听端口: $PORT"
echo "  热重载: $RELOAD"
echo ""
echo "API文档:"
echo "  Swagger UI: http://localhost:$PORT/docs"
echo "  ReDoc: http://localhost:$PORT/redoc"
echo ""
echo "========================================"
echo ""

# 启动服务器
if [ "$RELOAD" = "true" ]; then
    echo "启动开发模式（热重载）..."
    uv run uvicorn web.backend.main:app --host "$HOST" --port "$PORT" --reload
else
    echo "启动生产模式..."
    uv run uvicorn web.backend.main:app --host "$HOST" --port "$PORT"
fi
