#!/bin/sh
echo "Testing uv detection..."

# Check if uv is in PATH
echo "PATH=$PATH"

# Try different ways to find uv
echo "Using command -v uv:"
command -v uv

echo "Using which uv:"
which uv

echo "Using type uv:"
type uv

echo "Directly calling uv --version:"
"$HOME/.local/bin/uv" --version