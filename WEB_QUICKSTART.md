# WireGuard 组网工具 Web 界面快速启动指南

## 概述

Web 界面已开发完成，提供了以下功能：
- ✅ 服务端初始化和配置管理
- ✅ 节点创建、查看、删除
- ✅ 配置文件和脚本下载
- ✅ 搜索和筛选功能
- ✅ 响应式界面设计

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Element Plus
- **后端**: FastAPI (已集成静态文件托管)
- **部署方式**: 前后端一体化部署

## 快速启动

### 1. 开发模式（前后端分离）

#### 启动后端服务

```bash
# 在项目根目录
uv run uvicorn web.backend.main:app --host 0.0.0.0 --port 8080 --reload
```

后端将运行在 `http://localhost:8080`

#### 启动前端开发服务器

```bash
# 打开新终端
cd web/frontend
npm install  # 首次运行需要安装依赖
npm run dev
```

前端开发服务器将运行在 `http://localhost:5173`

API 请求会自动代理到后端 `http://localhost:8080`

### 2. 生产模式（推荐）

#### 构建前端

```bash
cd web/frontend
npm run build
```

构建产物会生成到 `web/frontend/dist` 目录。

#### 启动服务

```bash
# 回到项目根目录
cd ../..
uv run uvicorn web.backend.main:app --host 0.0.0.0 --port 8080
```

#### 访问应用

打开浏览器访问：`http://SERVER_IP:8080/web`

## 功能演示

### 服务端管理

1. 访问 `服务端管理` 页面
2. 如果未初始化，填写表单：
   - **公网端点**: 服务器的公网 IP:端口（如 `123.45.67.89:51820`）
   - **监听端口**: 默认 51820
   - **网络段**: 默认 10.0.0.0/24
   - **服务端IP**: 默认 10.0.0.1
3. 点击 `初始化服务端` 按钮
4. 初始化成功后可以查看服务端信息和执行重载配置

### 节点管理

1. 访问 `节点管理` 页面
2. 点击 `新建节点` 按钮
3. 填写节点信息：
   - **节点名称**: 唯一标识（如 `laptop-home`）
   - **平台类型**: 选择 Linux 或 Windows
   - **描述**: 可选的节点描述
4. 创建成功后可以：
   - 查看节点详情（包含私钥）
   - 下载配置文件（.conf）
   - 下载安装脚本（.sh 或 .ps1）
   - 删除节点

### 搜索和筛选

- 使用搜索框按节点名称、IP 或描述搜索
- 使用平台筛选器过滤 Linux 或 Windows 节点

## 目录结构

```
web/
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── api/           # API 接口封装
│   │   ├── assets/        # 静态资源
│   │   ├── components/    # 公共组件
│   │   ├── views/         # 页面视图
│   │   ├── stores/        # 状态管理
│   │   ├── router/        # 路由配置
│   │   ├── types/         # TypeScript 类型
│   │   └── utils/         # 工具函数
│   ├── dist/              # 构建产物（生产）
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
└── backend/               # 后端项目
    ├── api/v1/            # API 路由
    ├── schemas/           # 数据模型
    └── main.py            # FastAPI 入口（已集成静态托管）
```

## API 接口文档

访问 `http://SERVER_IP:8080/docs` 查看自动生成的 API 文档。

## 环境要求

### 前端开发

- Node.js >= 16
- npm >= 8

### 后端运行

- Python >= 3.8
- uv (已安装)
- WireGuard

## 配置说明

### 前端配置

位置：`web/frontend/vite.config.ts`

关键配置：
- `base: '/web/'` - 静态资源基础路径
- `server.proxy` - 开发环境 API 代理

### 后端配置

位置：`web/backend/main.py`

已添加静态文件托管：
- `/web/assets/*` - 静态资源
- `/web/*` - SPA 路由支持
- `/web` - 根路径

## 常见问题

### 1. 前端构建失败

检查 Node.js 和 npm 版本：
```bash
node -v  # 应该 >= 16
npm -v   # 应该 >= 8
```

清除缓存重新安装：
```bash
cd web/frontend
rm -rf node_modules package-lock.json
npm install
```

### 2. API 调用失败

- 确保后端服务已启动
- 检查后端监听端口（默认 8080）
- 检查防火墙设置

### 3. 页面空白或 404

- 确保已执行 `npm run build`
- 确保 `web/frontend/dist` 目录存在
- 检查后端 `main.py` 中的静态文件托管配置

### 4. 样式错误

- 清除浏览器缓存
- 重新构建前端：`npm run build`

## 开发调试

### 查看 API 请求

打开浏览器开发者工具（F12）-> Network 标签页

### 查看 Vue 组件状态

安装 [Vue DevTools](https://devtools.vuejs.org/) 浏览器扩展

### 查看控制台日志

开发模式下，API 请求和响应会记录到浏览器控制台

## 下一步

- [ ] 优化大数据量性能（分页）
- [ ] 添加用户认证功能
- [ ] 实时状态监控（WebSocket）
- [ ] 移动端适配优化
- [ ] 多语言支持

## 反馈和贡献

如有问题或建议，请通过以下方式反馈：
- 查看详细文档：`web/frontend/README.md`
- 查看 API 文档：`http://SERVER_IP:8080/docs`

---

**开发完成日期**: 2024-11-20  
**版本**: v1.0.0
