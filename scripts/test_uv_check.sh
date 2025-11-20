#!/bin/sh
echo "Testing uv detection in script..."

# Add local bin to PATH
PATH="$HOME/.local/bin:$PATH"
export PATH

echo "Updated PATH=$PATH"

# Check Python environment
if ! command -v uv > /dev/null 2>&1; then
    echo "错误: 未找到uv命令"
    echo "请先安装uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
else
    echo "Success: uv found at $(command -v uv)"
fi