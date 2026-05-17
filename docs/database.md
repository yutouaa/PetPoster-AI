# PetPoster AI 数据库草案

数据库目标：PostgreSQL。

迁移工具：Alembic。

## 第一阶段核心表

```text
admin_users
templates
generation_tasks
```

## 后续表

```text
users
credit_logs
share_logs
orders
payment_packages
```

## 设计原则

- 后台管理员账号和小程序用户账号分开。
- 所有额度变化必须写入 `credit_logs`。
- 所有生成任务必须可追踪、可重试、可补偿。
- 任务状态先使用：`pending`、`processing`、`success`、`failed`、`refunded`。
- 金额、额度、成本等字段必须有非负约束。

## 下一步

先用 Alembic 创建 `admin_users`、`templates`、`generation_tasks` 三张表，再接后台模板管理页面。
