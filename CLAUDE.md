# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

PetPoster AI（宠物海报 AI）是一个面向微信小程序用户的宠物海报生成产品，包含三端：

```text
miniprogram/   微信原生小程序（客户端）
admin/         SoybeanAdmin Element Plus 后台管理前端
api/           FastAPI 后端 API
docs/          接口和数据库设计草案
```

## 启动命令

### API（FastAPI + uv）

```bash
cd api
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

开发模式默认使用 SQLite，启动时自动建表 + seed（无需手动配置数据库）。生产使用 PostgreSQL。

数据库迁移（仅 PostgreSQL 生产环境）：

```bash
cd api
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "描述"
```

运行测试：

```bash
cd api
uv run pytest
uv run pytest tests/test_xxx.py -k "test_name"
```

### 后台管理（Vue 3 + Vite + pnpm）

```bash
cd admin
corepack pnpm install
corepack pnpm dev          # 开发服务器（端口 9527）
corepack pnpm build        # 生产构建
corepack pnpm lint         # ESLint 修复
corepack pnpm typecheck    # vue-tsc 类型检查
```

如需激活 pnpm：`corepack prepare pnpm@10.5.0 --activate`

### 小程序

用微信开发者工具导入 `miniprogram/` 目录。

## 架构要点

### API 层（api/app/）

- 入口：`main.py` → `create_app()` 工厂函数，挂载 CORS、异常处理器、静态文件、路由
- 路由注册：`api/router.py` 汇总所有子路由，统一前缀 `/api`
- 路由模块：`health`、`admin`（登录）、`admin_templates`（后台模板管理）、`templates`（小程序读取）、`generation_tasks`（生成任务）、`upload`（图片上传）
- 配置：`core/config.py` 使用 pydantic-settings + `@lru_cache`，从 `.env` 读取
- 认证：`core/security.py` JWT 签发/验证，`api/deps.py` 提供 `get_current_admin` 和 `get_db` 依赖
- 错误处理：`core/errors.py` 定义 `AppError(error_code, message, status_code)` 异常类
- 响应格式：`core/responses.py` → `success_response` / `error_response`
- 数据库：SQLAlchemy 2.0，`db/session.py` 创建引擎，`db/bootstrap.py` 开发环境自动建表
- 模型：`models/` 下 `AdminUser`、`Template`、`GenerationTask`
- AI 生成：`services/ai_service.py` 调用 Rightcode API（gpt-image-2）生成海报，`services/generation_processor.py` 处理异步任务流程
- 种子数据：`db/seed.py` 初始化管理员账号 + 8 个默认模板

统一响应格式（兼容 SoybeanAdmin）：
```json
{ "success": true, "code": "0000", "data": {}, "msg": "", "message": "" }
{ "success": false, "code": "ERROR_CODE", "errorCode": "ERROR_CODE", "data": null, "msg": "", "message": "" }
```

### 后台管理（admin/）

- 基于 SoybeanAdmin Element Plus 模板（Vue 3 + TypeScript + UnoCSS）
- 路由使用 `@elegant-router/vue` 自动生成（基于文件系统）
- PetPoster 业务页面在 `src/views/petposter/`：dashboard、templates、generations
- 状态管理：Pinia（`src/store/modules/`）
- HTTP 请求：alova（`packages/alova/`）
- Git hooks：commit-msg 校验 + pre-commit 执行 typecheck + lint + diff check

### 小程序（miniprogram/）

- 原生微信小程序，无框架，单页面 `pages/index/index`
- 功能集成在一个页面内：上传照片、选风格、生成、查看结果
- `utils/api.js`：统一 HTTP 请求封装，调用后端 `/api/templates`、`/api/generation-tasks`、`/api/upload/images`
- `components/`：`status-bar`、`mini-nav`、`tab-bar` 自定义组件
- `styles/tokens.wxss`：设计令牌（颜色、间距、圆角等）
- 自定义导航栏（`navigationStyle: "custom"`）

## 开发约定

- 页面文案、注释和说明优先使用中文
- 技术字段名、接口路径、环境变量名保持英文
- 小程序使用原生 WXML/WXSS/JS，不引入 Taro、uni-app 或 TypeScript
- 后台前端遵循 SoybeanAdmin 原有工程规范，不重写模板架构
- API 使用 FastAPI + SQLAlchemy，Python >= 3.12

## 本地环境

默认管理员：`admin` / `admin123`

API 开发环境无需 `.env` 文件即可启动（SQLite + 默认配置）。生产环境需配置：

```text
APP_ENV=production
DATABASE_URL=postgresql+psycopg://petposter:petposter@localhost:5432/petposter_ai
ADMIN_JWT_SECRET=（必须修改）
ADMIN_PASSWORD=（必须修改）
CORS_ORIGINS=http://localhost:9527
RIGHTCODE_API_KEY=（AI 生成服务密钥）
PUBLIC_BASE_URL=https://your-domain.com
```
