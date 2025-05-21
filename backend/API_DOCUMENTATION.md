# 建筑垃圾清理运输系统 API 文档

本文档详细说明了建筑垃圾清理运输系统的API接口。

## 基本信息

- 基础URL: `/api/v1`
- API文档: `/docs` 或 `/redoc`（基于Swagger和ReDoc自动生成）
- 健康检查: `/health`

## 认证

大多数API端点需要认证。认证通过JWT令牌实现，令牌通过以下方式获取：

### 获取访问令牌

```
POST /api/v1/auth/login
```

**请求体**：

```json
{
  "username": "string",
  "password": "string"
}
```

**响应**：

```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### 微信小程序登录

```
POST /api/v1/auth/wx-login
```

**请求体**：

```json
{
  "code": "string"
}
```

**响应**：

```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user_info": {
    "id": "string",
    "username": "string",
    "role": "string"
  }
}
```

## 用户管理

### 获取当前用户信息

```
GET /api/v1/users/me
```

**响应**：

```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "role": "string",
  "is_active": true
}
```

### 创建新用户（仅管理员）

```
POST /api/v1/users/
```

**请求体**：

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string",
  "role": "string"
}
```

**响应**：

```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "role": "string",
  "is_active": true
}
```

### 获取用户列表（仅管理员）

```
GET /api/v1/users/
```

**查询参数**：

- `skip`: 跳过的记录数（默认：0）
- `limit`: 返回的最大记录数（默认：100）

**响应**：

```json
[
  {
    "id": "string",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "role": "string",
    "is_active": true
  }
]
```

### 获取特定用户（仅管理员）

```
GET /api/v1/users/{user_id}
```

**响应**：

```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "role": "string",
  "is_active": true
}
```

### 更新用户信息

```
PUT /api/v1/users/{user_id}
```

**请求体**：

```json
{
  "email": "string",
  "full_name": "string",
  "password": "string"
}
```

**响应**：

```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "role": "string",
  "is_active": true
}
```

## 垃圾清运订单管理

### 创建清运订单

```
POST /api/v1/orders/
```

**请求体**：

```json
{
  "address": "string",
  "contact_name": "string",
  "contact_phone": "string",
  "waste_type": "string",
  "waste_volume": "number",
  "expected_time": "string",
  "remarks": "string"
}
```

**响应**：

```json
{
  "id": "string",
  "user_id": "string",
  "address": "string",
  "contact_name": "string",
  "contact_phone": "string",
  "waste_type": "string",
  "waste_volume": "number",
  "expected_time": "string",
  "status": "string",
  "remarks": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

### 获取订单列表

```
GET /api/v1/orders/
```

**查询参数**：

- `skip`: 跳过的记录数（默认：0）
- `limit`: 返回的最大记录数（默认：100）
- `status`: 订单状态过滤（可选）

**响应**：

```json
[
  {
    "id": "string",
    "user_id": "string",
    "address": "string",
    "contact_name": "string",
    "contact_phone": "string",
    "waste_type": "string",
    "waste_volume": "number",
    "expected_time": "string",
    "status": "string",
    "remarks": "string",
    "created_at": "string",
    "updated_at": "string"
  }
]
```

### 获取特定订单

```
GET /api/v1/orders/{order_id}
```

**响应**：

```json
{
  "id": "string",
  "user_id": "string",
  "address": "string",
  "contact_name": "string",
  "contact_phone": "string",
  "waste_type": "string",
  "waste_volume": "number",
  "expected_time": "string",
  "status": "string",
  "remarks": "string",
  "created_at": "string",
  "updated_at": "string",
  "user": {
    "id": "string",
    "username": "string",
    "full_name": "string"
  }
}
```

### 更新订单状态

```
PATCH /api/v1/orders/{order_id}/status
```

**请求体**：

```json
{
  "status": "string"
}
```

**响应**：

```json
{
  "id": "string",
  "status": "string",
  "updated_at": "string"
}
```

### 取消订单

```
POST /api/v1/orders/{order_id}/cancel
```

**请求体**：

```json
{
  "cancel_reason": "string"
}
```

**响应**：

```json
{
  "id": "string",
  "status": "cancelled",
  "updated_at": "string"
}
```

## 车辆管理

### 获取车辆列表

```
GET /api/v1/vehicles/
```

**查询参数**：

- `skip`: 跳过的记录数（默认：0）
- `limit`: 返回的最大记录数（默认：100）
- `status`: 车辆状态过滤（可选）

**响应**：

```json
[
  {
    "id": "string",
    "plate_number": "string",
    "vehicle_type": "string",
    "capacity": "number",
    "status": "string",
    "driver_id": "string",
    "driver": {
      "id": "string",
      "username": "string",
      "full_name": "string"
    }
  }
]
```

### 获取特定车辆

```
GET /api/v1/vehicles/{vehicle_id}
```

**响应**：

```json
{
  "id": "string",
  "plate_number": "string",
  "vehicle_type": "string",
  "capacity": "number",
  "status": "string",
  "driver_id": "string",
  "driver": {
    "id": "string",
    "username": "string",
    "full_name": "string"
  }
}
```

### 创建车辆（仅管理员）

```
POST /api/v1/vehicles/
```

**请求体**：

```json
{
  "plate_number": "string",
  "vehicle_type": "string",
  "capacity": "number",
  "driver_id": "string"
}
```

**响应**：

```json
{
  "id": "string",
  "plate_number": "string",
  "vehicle_type": "string",
  "capacity": "number",
  "status": "available",
  "driver_id": "string"
}
```

## 统计数据

### 获取订单统计

```
GET /api/v1/stats/orders
```

**查询参数**：

- `start_date`: 开始日期（格式：YYYY-MM-DD）
- `end_date`: 结束日期（格式：YYYY-MM-DD）

**响应**：

```json
{
  "total_orders": "number",
  "completed_orders": "number",
  "cancelled_orders": "number",
  "pending_orders": "number",
  "in_progress_orders": "number",
  "total_waste_volume": "number",
  "daily_stats": [
    {
      "date": "string",
      "order_count": "number",
      "waste_volume": "number"
    }
  ]
}
```

## 错误响应

所有API错误响应都遵循以下格式：

```json
{
  "detail": "string"
}
```

常见HTTP状态码：

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证或认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 请求参数验证失败
- `500 Internal Server Error`: 服务器内部错误

## 数据模型

### 用户角色

- `admin`: 管理员
- `driver`: 司机
- `customer`: 客户

### 订单状态

- `pending`: 待处理
- `assigned`: 已分配
- `in_progress`: 处理中
- `completed`: 已完成
- `cancelled`: 已取消

### 车辆状态

- `available`: 可用
- `in_use`: 使用中
- `maintenance`: 维护中
- `out_of_service`: 停用