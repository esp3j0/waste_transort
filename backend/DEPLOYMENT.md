# 建筑垃圾清理运输系统部署指南

本文档提供了建筑垃圾清理运输系统后端的部署和运行说明。

## 目录

- [本地开发环境](#本地开发环境)
- [Docker部署](#docker部署)
- [生产环境部署](#生产环境部署)
- [数据库管理](#数据库管理)
- [环境变量配置](#环境变量配置)

## 本地开发环境

### 前提条件

- Python 3.8+
- pip (Python包管理器)
- 虚拟环境工具(可选，但推荐)

### 安装步骤

1. 克隆代码库

```bash
git clone <仓库地址>
cd waste_transort/backend
```

2. 创建并激活虚拟环境(可选)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 配置环境变量

复制`.env.example`文件(如果有)或创建`.env`文件，并根据需要修改配置。

5. 运行数据库迁移

```bash
alembic upgrade head
```

6. 启动应用

```bash
uvicorn main:app --reload
```

或使用启动脚本

```bash
# Linux/Mac (可能需要先赋予执行权限)
chmod +x start.sh
./start.sh

# Windows (PowerShell)
python -m uvicorn main:app --reload
```

应用将在 http://localhost:8000 运行，API文档可在 http://localhost:8000/docs 访问。

## Docker部署

### 前提条件

- Docker
- Docker Compose

### 使用Docker Compose部署

1. 构建并启动容器

```bash
docker-compose up -d --build
```

2. 查看日志

```bash
docker-compose logs -f
```

3. 停止服务

```bash
docker-compose down
```

### 仅使用Dockerfile部署

1. 构建Docker镜像

```bash
docker build -t waste-transport-api .
```

2. 运行容器

```bash
docker run -d -p 8000:8000 --name waste-transport-container waste-transport-api
```

## 生产环境部署

### 推荐配置

- 使用反向代理(如Nginx)处理HTTPS和负载均衡
- 使用PostgreSQL数据库
- 配置适当的日志记录和监控

### 部署步骤

1. 准备服务器环境

2. 配置环境变量
   - 修改`.env`文件中的配置，特别是数据库连接、密钥等敏感信息
   - 确保`SECRET_KEY`已更改为强密码
   - 配置正确的`DATABASE_URL`
   - 设置适当的`BACKEND_CORS_ORIGINS`

3. 使用Docker Compose部署

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

4. 配置Nginx反向代理(示例)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 数据库管理

### 数据库迁移

创建新的迁移

```bash
alembic revision --autogenerate -m "描述迁移内容"
```

应用迁移

```bash
alembic upgrade head
```

回滚迁移

```bash
alembic downgrade -1  # 回滚一个版本
```

### 数据库备份与恢复

**PostgreSQL备份**

```bash
# 备份
pg_dump -U postgres -d waste_transport > backup.sql

# 从Docker容器中备份
docker exec waste_transport_db pg_dump -U postgres -d waste_transport > backup.sql
```

**PostgreSQL恢复**

```bash
# 恢复
psql -U postgres -d waste_transport < backup.sql

# 向Docker容器中恢复
cat backup.sql | docker exec -i waste_transport_db psql -U postgres -d waste_transport
```

## 环境变量配置

以下是主要环境变量及其说明：

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| PROJECT_NAME | 项目名称 | 建筑垃圾清理运输系统 |
| PROJECT_DESCRIPTION | 项目描述 | 建筑垃圾清理运输微信小程序后端API |
| VERSION | API版本 | 0.1.0 |
| API_V1_STR | API前缀 | /api/v1 |
| SECRET_KEY | 安全密钥 | your-secret-key-change-in-production |
| ACCESS_TOKEN_EXPIRE_MINUTES | 令牌过期时间(分钟) | 11520 (8天) |
| DATABASE_URL | 数据库连接URL | sqlite:///./waste_transport.db |
| BACKEND_CORS_ORIGINS | 允许的CORS来源 | ["http://localhost:8080", "http://localhost:3000"] |
| WX_APP_ID | 微信小程序AppID | - |
| WX_APP_SECRET | 微信小程序AppSecret | - |

**注意**：在生产环境中，请确保更改默认的敏感信息，如`SECRET_KEY`和数据库凭据。