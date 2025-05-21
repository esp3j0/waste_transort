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
├── scripts/              # 工具脚本目录
│   ├── db_backup.py      # 数据库备份和恢复脚本
│   └── db_backup.bat     # Windows环境下的数据库备份批处理脚本
├── tests/                # 测试目录
├── .env                  # 环境变量
├── .gitignore            # Git忽略文件
├── alembic.ini           # Alembic配置
├── API_DOCUMENTATION.md  # API文档
├── DEPLOYMENT.md         # 部署指南
├── Dockerfile            # Docker配置文件
├── docker-compose.yml    # Docker Compose配置文件
├── main.py               # 应用入口
├── requirements.txt      # 依赖包
├── start.bat             # Windows环境下的启动脚本
└── start.sh              # Linux/Mac环境下的启动脚本
```

## 安装与运行

### 本地开发环境

1. 安装依赖

```bash
# 手动安装
pip install -r requirements.txt

# 或使用启动脚本安装（Windows）
start.bat --install

# 或使用启动脚本安装（Linux/Mac）
chmod +x start.sh  # 赋予执行权限
./start.sh --install
```

2. 设置环境变量（编辑.env文件）

3. 运行数据库迁移

```bash
# 手动运行迁移
alembic upgrade head

# 或使用启动脚本运行迁移（Windows）
start.bat --migrate

# 或使用启动脚本运行迁移（Linux/Mac）
./start.sh --migrate
```

4. 启动服务

```bash
# 手动启动
uvicorn main:app --reload

# 或使用启动脚本（Windows）
start.bat

# 或使用启动脚本（Linux/Mac）
./start.sh
```

5. 访问API文档

```
http://localhost:8000/docs
```

### Docker部署

使用Docker Compose快速部署：

```bash
# 构建并启动容器
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

更多详细的部署说明，请参考[部署指南](./DEPLOYMENT.md)。

## 主要功能

- 用户认证与授权
- 订单管理
- 物业管理
- 运输管理
- 处置回收管理
- 数据统计与报表

## 工具脚本

在`scripts`目录下提供了一些实用工具：

### 数据库备份和恢复

```bash
# Windows环境
# 备份数据库
scripts\db_backup.bat backup

# 恢复数据库
scripts\db_backup.bat restore <备份文件路径>

# Linux/Mac环境
# 备份数据库
python scripts/db_backup.py backup

# 恢复数据库
python scripts/db_backup.py restore <备份文件路径>
```

更多详细信息请参考[scripts/README.md](./scripts/README.md)。

## 文档

- [API文档](./API_DOCUMENTATION.md) - 详细的API接口说明
- [部署指南](./DEPLOYMENT.md) - 包含本地开发、Docker部署和生产环境部署的详细说明