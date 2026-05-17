# PetPoster API

FastAPI 后端服务，负责后台管理、小程序接口、生成任务和后续 AI 图片生成链路。

## 本地启动

```bash
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 当前接口

```text
GET  /api/health
POST /api/admin/auth/login
GET  /api/admin/me
GET  /api/admin/dashboard
```

默认本地管理员：

```text
账号：admin
密码：admin123
```

生产环境必须修改 `.env` 中的 `ADMIN_PASSWORD` 和 `ADMIN_JWT_SECRET`。
