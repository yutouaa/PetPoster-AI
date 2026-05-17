/# PetPoster AI / 宠物海报 AI

面向微信小程序用户的 AI 宠物海报生成产品。当前工程采用三端结构：

```text
PetPoster AI/
  miniprogram/   # 微信原生小程序，当前已有本地闭环
  admin/         # SoybeanAdmin Element Plus 后台管理前端
  api/           # FastAPI 后端 API
  docs/          # 接口和数据库说明
```

## 当前状态

- `miniprogram/` 已实现本地闭环：上传照片、选择风格、模拟生成、结果页、历史记录。
- `admin/` 使用完整 `soybean-admin-element-plus` 模板，已加入 PetPoster 菜单占位。
- `api/` 使用 FastAPI 骨架，已提供健康检查、后台登录、当前管理员和 Dashboard 占位接口。

## 启动方式

### 小程序

使用微信开发者工具导入：

```text
miniprogram/
```

### API

```bash
cd api
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```text
GET http://127.0.0.1:8000/api/health
```

### 后台管理

```bash
cd admin
corepack enable
pnpm install
pnpm dev
```

如果本机没有 `pnpm`，先执行：

```bash
corepack prepare pnpm@latest --activate
```

## 下一步优先级

第一优先开发：FastAPI 数据库基础 + 后台模板管理。

原因：模板是小程序和后台最早共享的数据。先做模板管理，可以最快把当前小程序里的本地 `posterStyles.js` 替换成真实接口，也能验证后台前端、API、数据库三者是否打通。



知识图谱 Schema 优化与检索对齐｜1 天
● 完成现有图谱结构与 KG 检索需求的差异分析，优化实体属性、关系类型及索引策略，确保满足检索性能要求；
● 验证优化后的图谱结构与现有多模态能力的兼容性，保障数据与图谱知识的无缝对接。
2.    图谱接口开发与效果验证｜3 天
● 完成知识图谱 CRUD 对接接口开发，支持关系的增删改查操作；
● 审查并评估对接现有知识图谱能力后的问答效果，量化分析检索准确率与推理深度提升情况。