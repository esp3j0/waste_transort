@echo off
REM 数据库备份和恢复批处理脚本

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查参数
if "%1"=="" (
    echo 用法: db_backup.bat [backup^|restore] [备份文件路径]
    exit /b 1
)

REM 检查Python环境
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 找不到Python。请确保Python已安装并添加到PATH中。
    exit /b 1
)

REM 执行Python脚本
python db_backup.py %*