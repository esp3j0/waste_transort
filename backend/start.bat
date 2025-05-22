@echo off
REM 启动脚本 - 用于Windows环境下运行FastAPI应用

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查是否存在虚拟环境
if exist venv (
    call venv\Scripts\activate.bat
)

REM 安装依赖（如果需要）
if "%1"=="--install" (
    echo 安装依赖...
    pip install -r requirements.txt
)

REM 运行数据库迁移（如果需要）
if "%1"=="--migrate" (
    echo 运行数据库迁移...
    alembic upgrade head
) else if "%2"=="--migrate" (
    echo 运行数据库迁移...
    alembic upgrade head
)

REM 初始化数据库
echo 正在初始化数据库...
python -m app.db.init_db

REM 启动应用
echo 启动应用...
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload