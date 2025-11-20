# WireGuard Network Toolkit - 版本更新说明

## v0.2.0 - 项目结构重构

### 主要变化

本版本对项目结构进行了全面重构，引入了统一的命令行入口。

### 新特性

1. **统一命令行入口** `wg-toolkit`
   - 所有功能通过单一命令访问
   - CLI 和 Web 服务统一管理
   - 更清晰的命令结构

2. **模块化架构**
   - 清晰的分层结构（CLI/Web/Core/Config）
   - 更好的代码组织
   - 易于维护和扩展

3. **完善的文档**
   - CLI 命令参考
   - API 接口文档
   - 开发者指南

### 命令变更

### CLI 命令

| 功能 | 旧命令 | 新命令 | 说明 |
|------|--------|--------|------|
| 初始化服务端 | `uv run python main.py init ...` | `uv run wg-toolkit init ...` | 简化入口 |
| 注册节点 | `uv run python main.py register ...` | `uv run wg-toolkit register ...` | 简化入口 |
| 列出节点 | `uv run python main.py list` | `uv run wg-toolkit list` | 简化入口 |
| 查看节点详情 | `uv run python main.py show ...` | `uv run wg-toolkit show ...` | 简化入口 |
| 删除节点 | `uv run python main.py delete ...` | `uv run wg-toolkit delete ...` | 简化入口 |
| 导出配置 | `uv run python main.py export ...` | `uv run wg-toolkit export ...` | 简化入口 |
| 服务端信息 | `uv run python main.py server-info` | `uv run wg-toolkit server-info` | 简化入口 |

### Web 服务命令

| 功能 | 旧命令 | 新命令 | 说明 |
|------|--------|--------|------|
| 启动 API 服务 | `uv run python main.py api` | `uv run wg-toolkit web start` | 使用 FastAPI |
| 直接启动 uvicorn | `uv run uvicorn web.backend.main:app` | `uv run wg-toolkit web start` | 统一入口 |
| 启动脚本 | `scripts/start_web.sh` | `uv run wg-toolkit web start` | 建议使用新命令 |

### 辅助脚本

| 功能 | 旧方式 | 新方式 | 说明 |
|------|--------|--------|------|
| 初始化数据库 | `python init_db.py` | `uv run python scripts/init_db.py` | 移至 scripts 目录 |

## 详细迁移步骤

### 步骤 1：更新命令行脚本

如果您有自动化脚本或文档使用旧命令，请按照上述对照表更新。

**示例：服务端初始化**

旧脚本：
```bash
#!/bin/bash
uv run python main.py init --endpoint 203.0.113.100:51820
```

新脚本：
```bash
#!/bin/bash
uv run wg-toolkit init --endpoint 203.0.113.100:51820
```

### 步骤 2：更新环境变量和配置

新版本的 Web 服务基于 FastAPI，配置保持不变：
- `API_HOST`: 监听地址（默认 0.0.0.0）
- `API_PORT`: 监听端口（默认 8080）
- `API_RELOAD`: 是否启用热重载

### 步骤 3：更新文档链接

如果您在内部文档中引用了命令，请更新为新的格式。

### 步骤 4：测试新命令

在生产环境部署前，先在测试环境验证新命令：

```bash
# 测试帮助命令
uv run wg-toolkit --help
uv run wg-toolkit init --help
uv run wg-toolkit web start --help

# 测试实际功能（在测试环境）
uv run wg-toolkit init --endpoint TEST_IP:51820
uv run wg-toolkit register test-node linux --export
uv run wg-toolkit list
```

## 兼容性说明

### 向后兼容

**旧命令仍然可用**，但会显示弃用警告：

```bash
# 旧命令仍然有效
uv run python main.py init --endpoint YOUR_IP:51820

# 输出会包含警告：
# ================================================================
# 警告: 此入口已弃用
# ================================================================
# 请使用新的统一入口 'wg-toolkit'
# ...
```

### 数据兼容性

✅ **完全兼容**：
- 数据库结构不变（`wg_data/wg_nodes.db`）
- 配置文件位置不变（`/etc/wireguard/wg0.conf`）
- 导出目录不变（`./exports/`）
- 所有现有数据和配置可以继续使用

### API 变化

**重要**：Web API 从 Flask 迁移到 FastAPI

**旧 Flask API** (已弃用):
- 端点：`http://localhost:8080/api/nodes/register`
- 文档：无自动生成文档

**新 FastAPI API** (推荐):
- 端点：`http://localhost:8080/api/v1/nodes`
- 文档：`http://localhost:8080/docs`（自动生成的交互式文档）
- 性能更好，类型安全

## 常见问题

### Q1: 我需要重新安装吗？

**不需要**。运行 `uv sync` 确保依赖最新即可：

```bash
cd /path/to/wireguard-net
uv sync
```

### Q2: 旧命令何时会被移除？

旧命令将保留至少 2-3 个版本周期，给用户充足的迁移时间。具体移除时间会在发布说明中提前公告。

### Q3: 我的脚本需要全部更新吗？

**不需要立即更新**。旧命令仍然可用，但建议逐步迁移到新命令以：
- 避免将来的破坏性更新
- 使用新功能和改进
- 保持与文档一致

### Q4: Web API 客户端需要修改吗？

如果您使用旧的 Flask API：
- API 端点路径略有变化（`/api/...` → `/api/v1/...`）
- 响应格式保持兼容
- 建议参考新的 API 文档：`http://localhost:8080/docs`

### Q5: 如何禁用弃用警告？

在 Python 代码中：
```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

在命令行中：
```bash
export PYTHONWARNINGS="ignore::DeprecationWarning"
uv run python main.py init ...
```

**不建议长期禁用警告**，应尽快迁移到新命令。

## 获取帮助

如果在迁移过程中遇到问题：

1. 查看新的命令帮助：
   ```bash
   uv run wg-toolkit --help
   uv run wg-toolkit [command] --help
   ```

2. 查看完整文档：
   - [README.md](../README.md)
   - [QUICKSTART.md](./QUICKSTART.md)
   - [CLI_REFERENCE.md](./CLI_REFERENCE.md)
   - [API_REFERENCE.md](./API_REFERENCE.md)

3. 提交 Issue 或查看 GitHub Discussions

## 迁移检查清单

使用此清单确保完整迁移：

- [ ] 更新所有自动化脚本中的命令
- [ ] 更新内部文档和操作手册
- [ ] 在测试环境验证新命令
- [ ] 如果使用 Web API，测试新的 API 端点
- [ ] 更新 systemd 服务文件（如果有）
- [ ] 通知团队成员命令变更
- [ ] 在生产环境部署前完整测试

## 总结

新的统一入口 `wg-toolkit` 提供了更好的用户体验和可维护性。迁移过程平滑，旧命令仍然可用，数据完全兼容。建议尽早迁移以享受新功能和改进。
