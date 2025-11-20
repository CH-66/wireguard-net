# WireGuard Network Toolkit - 开发指南

本文档面向项目开发者和贡献者。

## 项目结构

```
wireguard-net/
├── cli/                       # CLI 模块
│   ├── commands/             # CLI 命令实现
│   │   ├── init.py          # 初始化命令
│   │   ├── node.py          # 节点管理命令
│   │   ├── server.py        # 服务端信息命令
│   │   └── export.py        # 导出命令
│   └── main.py              # CLI 入口（已弃用）
│
├── web/                      # Web 模块
│   └── backend/
│       ├── api/v1/          # API 路由
│       │   ├── nodes.py     # 节点 API
│       │   ├── server.py    # 服务端 API
│       │   └── downloads.py # 下载 API
│       ├── schemas/         # Pydantic 数据模型
│       │   ├── common.py    # 公共模型
│       │   ├── node.py      # 节点模型
│       │   └── server.py    # 服务端模型
│       └── main.py          # FastAPI 应用
│
├── core/                     # 核心业务逻辑
│   ├── domain/              # 领域模型
│   │   ├── node.py         # 节点实体
│   │   └── server.py       # 服务端实体
│   ├── models/              # 数据访问层
│   │   ├── repositories/
│   │   │   ├── node_repo.py
│   │   │   └── server_repo.py
│   │   └── database.py     # 数据库操作
│   ├── services/            # 服务层
│   │   ├── config_service.py
│   │   ├── node_service.py
│   │   └── server_service.py
│   └── utils/               # 工具类
│       ├── config_generator.py
│       ├── ip_allocator.py
│       ├── key_manager.py
│       └── privileged_executor.py
│
├── config/                   # 配置管理
│   ├── base.py              # 基础配置
│   ├── cli.py               # CLI 配置
│   └── web.py               # Web 配置
│
├── scripts/                  # 辅助脚本
│   ├── init_db.py           # 数据库初始化
│   ├── install.sh           # 系统安装脚本
│   └── start_web.sh         # Web 启动脚本
│
├── doc/                      # 文档
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── CLI_REFERENCE.md
│   ├── API_REFERENCE.md
│   ├── ARCHITECTURE.md
│   ├── MIGRATION.md
│   └── DEVELOPMENT.md       # 本文档
│
├── wg_toolkit_cli.py        # 统一入口
├── pyproject.toml           # 项目配置
└── README.md                # 项目简介
```

## 开发环境搭建

### 前置要求

- Python 3.8.1+
- WireGuard (仅服务端需要)
- uv (Python 包管理器)

### 安装步骤

1. **克隆项目**:
```bash
git clone <repository-url>
cd wireguard-net
```

2. **安装 uv**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **同步依赖**:
```bash
uv sync
```

4. **初始化数据库**（可选）:
```bash
uv run python scripts/init_db.py
```

## 架构设计

### 分层架构

```
┌─────────────────────────────────────┐
│   表现层 (CLI / Web API)            │
├─────────────────────────────────────┤
│   服务层 (Services)                 │
├─────────────────────────────────────┤
│   仓储层 (Repositories)             │
├─────────────────────────────────────┤
│   领域层 (Domain Models)            │
├─────────────────────────────────────┤
│   基础设施层 (Utils / Config)       │
└─────────────────────────────────────┘
```

### 模块职责

- **CLI**: 命令行界面，调用服务层
- **Web API**: RESTful API，调用服务层
- **Services**: 业务逻辑实现
- **Repositories**: 数据持久化
- **Domain**: 领域实体和业务规则
- **Utils**: 通用工具类

## 开发规范

### 代码风格

遵循 PEP 8 规范，使用 Black 格式化：

```bash
uv run black .
```

### 导入规范

使用绝对导入：

```python
# ✅ 正确
from core.services.node_service import NodeService
from config.base import DEFAULT_NETWORK_CIDR

# ❌ 错误
from node_service import NodeService
import config
```

### 命名规范

- 文件名：`snake_case.py`
- 类名：`PascalCase`
- 函数/变量：`snake_case`
- 常量：`UPPER_SNAKE_CASE`

### 文档字符串

使用 Google 风格的 docstring：

```python
def register_node(node_name: str, platform: str) -> dict:
    """注册新节点
    
    Args:
        node_name: 节点名称
        platform: 平台类型 (linux/windows)
        
    Returns:
        包含节点信息的字典
        
    Raises:
        ValueError: 节点名称已存在
        RuntimeError: IP 地址池已耗尽
    """
    pass
```

## 添加新功能

### 添加 CLI 命令

1. 在 `cli/commands/` 创建命令文件
2. 实现 `register_command(subparsers)` 函数
3. 在 `wg_toolkit_cli.py` 中注册命令

示例：
```python
# cli/commands/example.py
def register_command(subparsers):
    parser = subparsers.add_parser('example', help='示例命令')
    parser.add_argument('--param', help='参数')
    parser.set_defaults(func=cmd_example)

def cmd_example(args):
    print(f"参数: {args.param}")
    return 0
```

### 添加 API 端点

1. 在 `web/backend/schemas/` 定义数据模型
2. 在 `web/backend/api/v1/` 创建路由文件
3. 在 `web/backend/main.py` 注册路由

示例：
```python
# web/backend/api/v1/example.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def get_example():
    return {"message": "Hello"}
```

### 添加服务层功能

1. 在 `core/services/` 创建或修改服务类
2. 注入必要的依赖（数据库、仓储）
3. 实现业务逻辑

示例：
```python
# core/services/example_service.py
class ExampleService:
    def __init__(self, db):
        self.db = db
    
    def do_something(self):
        # 业务逻辑
        pass
```

## 测试

### 运行测试

```bash
uv run pytest
```

### 编写测试

测试文件放在 `tests/` 目录：

```python
# tests/test_node_service.py
def test_register_node():
    # 测试逻辑
    pass
```

## 调试

### 启用调试模式

CLI:
```bash
PYTHONBREAKPOINT=ipdb.set_trace uv run wg-toolkit init ...
```

Web:
```bash
uv run wg-toolkit web start --reload
```

### 日志输出

添加日志：
```python
import logging

logger = logging.getLogger(__name__)
logger.info("信息日志")
logger.error("错误日志")
```

## 发布流程

### 版本号管理

遵循语义化版本 (SemVer)：
- MAJOR.MINOR.PATCH
- 例如：1.2.3

### 发布步骤

1. 更新版本号 (`pyproject.toml`)
2. 更新 CHANGELOG.md
3. 提交并打标签
4. 构建分发包

```bash
# 更新版本
vim pyproject.toml

# 构建
uv build

# 发布（如果需要）
uv publish
```

## 贡献指南

### 提交代码

1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 提交 Pull Request

### Commit 规范

使用约定式提交：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型：
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

示例：
```
feat(cli): 添加节点批量导入功能

实现通过 CSV 文件批量导入节点的功能

Closes #123
```

## 常见开发任务

### 更新依赖

```bash
uv sync --upgrade
```

### 添加新依赖

```bash
uv add <package-name>
```

### 格式化代码

```bash
uv run black .
uv run isort .
```

### 代码检查

```bash
uv run flake8
uv run mypy .
```

## 故障排查

### 数据库问题

重新初始化数据库：
```bash
rm -rf wg_data/
uv run python scripts/init_db.py
```

### 导入路径问题

确保使用绝对导入，检查 `sys.path`：
```python
import sys
print(sys.path)
```

## 资源链接

- [WireGuard 文档](https://www.wireguard.com/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [uv 文档](https://github.com/astral-sh/uv)

## 联系方式

如有问题，请通过以下方式联系：
- GitHub Issues
- Email: (待添加)
