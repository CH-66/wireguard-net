# WireGuard 组网工具 - 前端界面

基于 Vue 3 + TypeScript + Vite + Element Plus 构建的现代化 Web 管理界面。

## 技术栈

- **核心框架**: Vue 3 (Composition API)
- **开发语言**: TypeScript
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **HTTP 客户端**: Axios
- **路由管理**: Vue Router
- **状态管理**: Pinia

## 功能特性

- ✅ 服务端初始化管理
- ✅ 节点全生命周期管理（创建、查看、删除）
- ✅ 配置文件和脚本下载
- ✅ 实时搜索和平台筛选
- ✅ 响应式设计，适配桌面端
- ✅ 表单验证和错误提示
- ✅ 密钥复制到剪贴板
- ✅ 统一的错误处理

## 开发指南

### 环境要求

- Node.js >= 16
- npm >= 8

### 安装依赖

```bash
cd web/frontend
npm install
```

### 开发模式

启动开发服务器，支持热更新：

```bash
npm run dev
```

访问 `http://localhost:5173` 查看应用。

开发模式下，API 请求会通过 Vite 代理转发到 `http://localhost:8080`。

### 生产构建

```bash
npm run build
```

构建产物会输出到 `dist` 目录，包含：
- `index.html` - 应用入口
- `assets/` - 静态资源（JS、CSS）

### 类型检查

```bash
npm run type-check
```

## 项目结构

```
src/
├── api/                 # API接口封装
│   ├── http.ts          # Axios实例和拦截器
│   ├── server.ts        # 服务端接口
│   ├── nodes.ts         # 节点接口
│   └── downloads.ts     # 下载接口
├── assets/              # 资源文件
│   └── styles/          # 全局样式
│       ├── variables.scss
│       └── global.scss
├── components/          # 公共组件
│   └── Layout/          # 布局组件
│       ├── Header.vue
│       ├── Footer.vue
│       └── MainLayout.vue
├── views/               # 页面视图
│   ├── Server/          # 服务端管理
│   │   └── ServerManage.vue
│   └── Nodes/           # 节点管理
│       ├── NodeList.vue
│       ├── NodeCreateDialog.vue
│       └── NodeDetailDialog.vue
├── stores/              # Pinia状态管理
│   ├── server.ts
│   └── nodes.ts
├── router/              # 路由配置
│   └── index.ts
├── types/               # TypeScript类型定义
│   ├── api.ts
│   ├── server.ts
│   └── node.ts
├── utils/               # 工具函数
│   ├── format.ts        # 格式化工具
│   ├── download.ts      # 下载工具
│   └── validator.ts     # 校验工具
├── App.vue              # 根组件
└── main.ts              # 应用入口
```

## 部署

### 方式一：FastAPI 托管（推荐）

1. 构建前端项目：
   ```bash
   cd web/frontend
   npm run build
   ```

2. 启动后端服务：
   ```bash
   cd ../../
   uv run uvicorn web.backend.main:app --host 0.0.0.0 --port 8080
   ```

3. 访问 `http://SERVER_IP:8080/web` 使用应用

### 方式二：独立部署

如需独立部署前端，可使用 nginx 或其他静态文件服务器托管 `dist` 目录。

nginx 配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend-server:8080;
    }
}
```

## 环境变量

### 开发环境 (`.env.development`)

```env
VITE_API_BASE_URL=/api/v1
```

### 生产环境 (`.env.production`)

```env
VITE_API_BASE_URL=/api/v1
```

## 浏览器兼容性

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 开发规范

### 命名约定

- 组件文件: PascalCase (例: `NodeList.vue`)
- 工具函数: camelCase (例: `formatDate`)
- 常量: UPPER_SNAKE_CASE (例: `API_BASE_URL`)
- CSS类: kebab-case (例: `node-list-container`)

### 组件规范

- 单文件组件顺序: template -> script -> style
- 使用 Composition API + `<script setup>`
- Props 定义必须包含类型和默认值
- 事件命名使用 kebab-case

### Git 提交规范

```
<type>(<scope>): <subject>

type: feat, fix, style, refactor, docs
scope: server, nodes, api, layout, common
```

示例:
- `feat(nodes): 实现节点列表展示功能`
- `fix(api): 修复下载文件名提取错误`

## 常见问题

### API 调用失败

1. 检查后端服务是否启动
2. 检查 CORS 配置
3. 检查 Vite 代理配置

### 路由 404

1. 检查 `vite.config.ts` 中的 `base` 配置
2. 确保后端正确托管静态文件
3. 检查 Vue Router 的 `history` 配置

### 样式不生效

1. 检查组件样式是否使用 `scoped`
2. 检查全局样式导入顺序
3. 检查 CSS 变量是否正确引用

## 调试建议

- 使用 Vue DevTools 检查组件状态
- 使用 Network 面板监控 API 请求
- 使用 Console 查看日志和错误
- 使用 Pinia DevTools 追踪状态变化

## 许可证

MIT
