# PetPoster AI Claude 开发交接计划

本文档用于交给 Claude 继续开发当前工程。请按本文档执行，不要重新设计技术路线，不要重写已有小程序 UI。

## 一、项目现状

当前工程根目录：

```text
C:\Users\lenovo\Desktop\PetPoster AI
```

当前目录结构：

```text
PetPoster AI/
  miniprogram/   # 微信原生小程序，当前已有本地闭环
  admin/         # SoybeanAdmin Element Plus 后台管理前端
  api/           # FastAPI 后端 API
  docs/          # 接口、数据库、开发说明
  .env.example
  .gitignore
  README.md
```

当前已完成：

- `miniprogram/`：微信原生小程序，已实现本地闭环，包括上传宠物照片、选择风格、模拟生成、结果页、历史记录、我的页面。
- `admin/`：已拉取完整 `soybean-admin-element-plus` 模板，已新增 PetPoster 菜单占位页面。
- `api/`：已搭建 `FastAPI + SQLAlchemy + Alembic + PostgreSQL` 骨架。
- `docs/`：已有接口和数据库说明。

当前 API 已有接口：

```text
GET  /api/health
POST /api/admin/auth/login
GET  /api/admin/me
GET  /api/admin/dashboard
```

统一成功响应：

```json
{
  "success": true,
  "data": {},
  "message": ""
}
```

统一失败响应：

```json
{
  "success": false,
  "errorCode": "ERROR_CODE",
  "message": "中文错误提示"
}
```

## 二、必须遵守的开发约束

1. 所有说明、注释、错误提示、页面文案使用中文。
2. 技术字段名、接口路径、环境变量名、数据库字段名保持英文，不要翻译。
3. 不要重写 `miniprogram/`，只在后续需要接真实接口时做小范围替换。
4. 不要改成 Taro、React Native 或 uni-app，小程序继续保持微信原生 JS。
5. 后台前端继续使用 `soybean-admin-element-plus`，不要替换为其他后台模板。
6. 后端继续使用 `FastAPI + SQLAlchemy + Alembic + PostgreSQL`。
7. 第一阶段不要开发真实 AI 生图、Cloudflare R2、微信支付、微信登录。
8. 每次改动后必须给出已改文件、验证命令、下一步建议。

## 三、当前推荐启动命令

### API

```powershell
cd "C:\Users\lenovo\Desktop\PetPoster AI\api"
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```text
GET http://127.0.0.1:8000/api/health
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

### 后台管理

```powershell
cd "C:\Users\lenovo\Desktop\PetPoster AI\admin"
corepack pnpm dev
```

如依赖缺失：

```powershell
corepack pnpm install
```

### 小程序

使用微信开发者工具打开：

```text
C:\Users\lenovo\Desktop\PetPoster AI\miniprogram
```

## 四、下一阶段总目标

下一阶段优先完成：

```text
FastAPI 数据库基础 + 后台模板管理 + 小程序模板接口读取
```

原因：

- 模板是小程序和后台最早共享的数据。
- 先做模板管理，可以最快验证 `admin -> api -> database` 是否打通。
- 小程序当前本地 `posterStyles.js` 可以在后续替换为真实 `GET /api/templates`。
- 不依赖支付、R2、微信登录、AI 生图，返工风险最低。

## 五、下一阶段开发任务

### 阶段 1：数据库基础

目标：让 API 有真实数据库模型和迁移能力。

需要完成：

1. 配置 SQLAlchemy 数据库连接。
2. 配置 Alembic 自动识别模型元数据。
3. 新增首批模型：
   - `admin_users`
   - `templates`
   - `generation_tasks`
4. 新增 Alembic 迁移文件。
5. 增加种子管理员账号机制。

建议表结构：

#### admin_users

```text
id
username
password_hash
nickname
role
is_active
created_at
updated_at
last_login_at
```

约束：

- `username` 唯一。
- `is_active` 默认 true。
- 密码必须只保存 hash，不保存明文。

#### templates

```text
id
name
category
description
cover_image_url
preview_image_url
prompt_template
negative_prompt
sort_order
is_active
created_at
updated_at
```

约束：

- `sort_order` 默认 0。
- `is_active` 默认 true。
- 列表默认按 `sort_order asc, created_at desc`。

#### generation_tasks

```text
id
user_id
template_id
status
original_image_urls
result_image_url
prompt
cost
failure_type
error_message
retry_count
request_id
created_at
updated_at
completed_at
```

说明：

- 当前阶段只建表，不接真实生成。
- `original_image_urls` 可先用 JSON 字段。
- `status` 先支持 `pending`、`processing`、`success`、`failed`。

验收标准：

- `alembic upgrade head` 可执行。
- 数据库可看到三张表。
- 模型字段和迁移文件一致。

### 阶段 2：后台登录接入数据库

目标：后台登录不再只依赖环境变量中的固定账号。

需要完成：

1. 使用 `admin_users` 表校验管理员。
2. 使用密码 hash 校验登录。
3. 登录成功签发 JWT。
4. `GET /api/admin/me` 从数据库返回当前管理员信息。
5. 保留统一错误响应。

接口保持：

```text
POST /api/admin/auth/login
GET  /api/admin/me
```

验收标准：

- 默认管理员可以登录。
- 错误密码返回中文错误。
- 被禁用管理员不能登录。
- 无 token 访问 `/api/admin/me` 返回认证失败。

### 阶段 3：后台模板管理 API

目标：完成模板的增删改查和上下架。

需要新增接口：

```text
GET    /api/admin/templates
POST   /api/admin/templates
GET    /api/admin/templates/{template_id}
PUT    /api/admin/templates/{template_id}
DELETE /api/admin/templates/{template_id}
PATCH  /api/admin/templates/{template_id}/status
PATCH  /api/admin/templates/sort
```

列表查询参数：

```text
page
pageSize
keyword
category
isActive
```

返回结构建议：

```json
{
  "success": true,
  "data": {
    "list": [],
    "page": 1,
    "pageSize": 10,
    "total": 0
  },
  "message": ""
}
```

验收标准：

- 可以新增模板。
- 可以编辑模板。
- 可以上下架模板。
- 可以按分类和关键词筛选。
- 可以删除模板。
- 删除策略先用真实删除或软删除二选一，但需要在代码注释中说明。

### 阶段 4：后台模板管理页面

目标：把 SoybeanAdmin 的模板管理占位页接到真实 API。

需要完成：

1. 在 `admin/` 中新增模板 API 请求封装。
2. 模板管理页面展示真实列表。
3. 支持新增、编辑、删除、上下架。
4. 表单字段与 API 字段保持一致。
5. 所有页面文案使用中文。

页面字段：

```text
模板名称
分类
描述
封面图 URL
预览图 URL
提示词模板
反向提示词
排序
是否上架
创建时间
更新时间
```

验收标准：

- 后台登录后可进入模板管理。
- 模板列表来自 FastAPI。
- 新增或编辑模板后列表刷新。
- 接口错误能用中文提示。

### 阶段 5：小程序公开模板接口

目标：让小程序能读取后台配置的上架模板。

需要新增公开接口：

```text
GET /api/templates
GET /api/templates/{template_id}
```

只返回上架模板：

```text
is_active = true
```

建议返回字段：

```text
id
name
category
description
coverImageUrl
previewImageUrl
sortOrder
```

验收标准：

- 未登录也能读取上架模板。
- 下架模板不会出现在小程序接口。
- 排序与后台一致。

### 阶段 6：小程序替换模板数据源

目标：把小程序风格页从本地 `posterStyles.js` 逐步替换为 API。

要求：

1. 保留本地 mock 作为接口失败兜底。
2. 不破坏当前本地闭环。
3. 风格页优先调用 `GET /api/templates`。
4. 接口失败时显示中文提示，并继续展示本地模板。

验收标准：

- API 正常时风格页展示后台模板。
- API 异常时小程序仍可使用本地模板。
- 选择模板、生成中、结果页流程不被破坏。

## 六、暂时不要做的事情

以下功能不要在下一阶段优先做：

```text
真实 AI 生图
Cloudflare R2 上传
微信支付
微信登录
用户额度系统
分享奖励
后台订单管理
后台用户管理
小程序 UI 重构
```

这些功能要等模板管理链路打通后再做。

## 七、推荐验证命令

### API

```powershell
cd "C:\Users\lenovo\Desktop\PetPoster AI\api"
uv run python -m compileall app alembic
uv run pytest
```

如暂时没有测试文件，至少运行：

```powershell
uv run python -m compileall app alembic
```

### Admin

```powershell
cd "C:\Users\lenovo\Desktop\PetPoster AI\admin"
corepack pnpm typecheck
corepack pnpm build
```

### 小程序

用微信开发者工具重新编译并检查：

```text
首页 -> 选择风格 -> 生成中 -> 结果页
我的 -> 生成历史
```

## 八、交付格式要求

Claude 每完成一个阶段，需要输出：

```text
已完成内容
修改文件列表
运行过的验证命令
验证结果
遗留问题
下一步建议
```

不要只输出思路，必须实际修改工程文件。

## 九、首个开发指令建议

可以直接把下面这段交给 Claude：

```text
请阅读 C:\Users\lenovo\Desktop\PetPoster AI\docs\claude-handoff-plan.md，然后执行“阶段 1：数据库基础”和“阶段 2：后台登录接入数据库”。

要求：
1. 不要重写 miniprogram。
2. 不要替换 soybean-admin-element-plus。
3. 后端继续使用 FastAPI、SQLAlchemy、Alembic、PostgreSQL。
4. 所有说明、注释、错误提示使用中文。
5. 完成后运行 API 编译检查，并告诉我修改了哪些文件。
```

