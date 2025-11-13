# 使用 uv 管理项目

本项目使用 [uv](https://github.com/astral-sh/uv) 作为 Python 包管理器。uv 是一个极快的 Python 包管理器，用 Rust 编写。

## 为什么使用 uv？

- ⚡ **极快的速度**：比 pip 快 10-100 倍
- 🔒 **可靠的依赖解析**：确保依赖版本兼容
- 📦 **统一的工具链**：包管理、虚拟环境、项目管理一体化
- 🔄 **兼容性好**：完全兼容 pip 和 requirements.txt

## 安装 uv

### Linux/macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 使用 pip 安装
```bash
pip install uv
```

## 常用命令

### 初始化项目
```bash
# 同步依赖（首次运行）
uv sync

# 同步开发依赖
uv sync --all-extras
```

### 运行 Python 脚本
```bash
# uv run 会自动激活虚拟环境并运行
uv run python main.py --help

# 运行项目命令
uv run python main.py init --endpoint YOUR_IP:51820
uv run python main.py api
```

### 依赖管理
```bash
# 添加新依赖
uv add requests

# 添加开发依赖
uv add --dev pytest

# 删除依赖
uv remove requests

# 更新所有依赖
uv lock --upgrade

# 更新特定依赖
uv lock --upgrade-package flask
```

### 虚拟环境
```bash
# uv sync 会自动创建 .venv 虚拟环境

# 手动激活虚拟环境（可选）
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 退出虚拟环境
deactivate
```

### 项目信息
```bash
# 查看已安装的包
uv pip list

# 查看项目树
uv tree
```

## 与传统 pip 的对比

| 操作 | pip | uv |
|------|-----|-----|
| 安装依赖 | `pip install -r requirements.txt` | `uv sync` |
| 添加包 | `pip install flask` + 手动更新 requirements.txt | `uv add flask` |
| 运行脚本 | `source venv/bin/activate && python main.py` | `uv run python main.py` |
| 创建虚拟环境 | `python -m venv venv` | `uv sync`（自动创建） |

## 项目文件说明

- **pyproject.toml**: 项目配置和依赖声明
- **uv.lock**: 锁定的依赖版本（确保可重复构建）
- **.venv/**: 虚拟环境目录（自动创建）
- **.python-version**: 指定项目使用的 Python 版本

## 兼容性说明

如果您不想使用 uv，仍然可以使用传统的 pip：

```bash
# 使用 pip
pip install -r requirements.txt

# 运行项目
python3 main.py --help
```

requirements.txt 文件会继续保留，以确保向后兼容。

## 常见问题

### 1. uv 找不到合适的 Python 版本

uv 会自动下载需要的 Python 版本，无需手动安装。

### 2. 如何在 CI/CD 中使用？

```yaml
# GitHub Actions 示例
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: uv sync

- name: Run tests
  run: uv run pytest
```

### 3. 如何升级 uv？

```bash
uv self update
```

## 更多信息

- [uv 官方文档](https://docs.astral.sh/uv/)
- [uv GitHub](https://github.com/astral-sh/uv)
