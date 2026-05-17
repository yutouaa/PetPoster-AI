# PetPoster AI API 草案

统一前缀：

```text
/api
```

## 统一响应

成功：

```json
{
  "success": true,
  "data": {},
  "message": ""
}
```

失败：

```json
{
  "success": false,
  "errorCode": "ERROR_CODE",
  "message": "中文错误提示"
}
```

## 当前已建接口

```text
GET  /api/health
POST /api/admin/auth/login
GET  /api/admin/me
GET  /api/admin/dashboard
```

## 下一阶段接口

后台模板管理：

```text
GET    /api/admin/templates
POST   /api/admin/templates
PUT    /api/admin/templates/{id}
DELETE /api/admin/templates/{id}
```

小程序模板读取：

```text
GET /api/templates
```

生成任务：

```text
POST /api/generations
GET  /api/generations/{id}
GET  /api/generations
```
