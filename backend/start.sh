#!/bin/bash

# 启动脚本 - 用于运行FastAPI应用

# 确保在正确的目录中
cd "$(dirname "$0")"

# 激活虚拟环境（如果有的话）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 安装依赖（如果需要）
if [ "$1" == "--install" ]; then
    echo "安装依赖..."
    pip install -r requirements.txt
fi

# 运行数据库迁移（如果需要）
if [ "$1" == "--migrate" ] || [ "$2" == "--migrate" ]; then
    echo "运行数据库迁移..."
    alembic upgrade head
fi

# 启动应用
echo "启动应用..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload