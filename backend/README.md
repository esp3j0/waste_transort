# 建筑垃圾清理运输微信小程序后端

基于FastAPI开发的建筑垃圾清理运输微信小程序后端服务，支持四个操作端：

- 用户下单端：面向业主、装修公司等终端用户，提供在线下单功能
- 物业管理端：针对小区物业管理，便于物业实时掌握业主装修进度及垃圾清运情况
- 运输管理端：运输机构分配司机，按照预定路线和时间完成清运工作
- 处置回收端：回收站完成回收工作，填写报表数据，确认订单流程完成

## 项目结构

```
backend/
├── alembic/              # 数据库迁移相关文件
├── app/                  # 应用主目录
│   ├── api/              # API路由
│   │   ├── v1/           # API版本1
│   │   │   ├── endpoints/    # 各模块的API端点
│   │   │   └── router.py     # API路由注册
│   ├── core/             # 核心配置
│   ├── crud/             # 数据库CRUD操作
│   ├── db/               # 数据库相关
│   ├── models/           # 数据库模型
│   ├── schemas/          # Pydantic模型
│   └── services/         # 业务逻辑服务
├── tests/                # 测试目录
├── .env                  # 环境变量
├── .gitignore            # Git忽略文件
├── alembic.ini           # Alembic配置
├── main.py               # 应用入口
└── requirements.txt      # 依赖包
```

## 安装与运行

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 设置环境变量（编辑.env文件）

3. 运行数据库迁移

```bash
alembic upgrade head
```

4. 启动服务

```bash
uvicorn main:app --reload
```

5. 访问API文档

```
http://localhost:8000/docs
```

## 主要功能

- 用户认证与授权
- 订单管理
- 物业管理
- 运输管理
- 处置回收管理
- 数据统计与报表