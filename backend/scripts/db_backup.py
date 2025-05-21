#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库备份脚本

此脚本用于备份和恢复数据库。支持SQLite和PostgreSQL数据库。
使用方法：
    备份: python db_backup.py backup [备份文件路径]
    恢复: python db_backup.py restore [备份文件路径]
"""

import os
import sys
import datetime
import subprocess
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings

# 获取数据库URL
DATABASE_URL = settings.DATABASE_URL


def is_sqlite():
    """检查是否使用SQLite数据库"""
    return DATABASE_URL.startswith("sqlite")


def is_postgresql():
    """检查是否使用PostgreSQL数据库"""
    return DATABASE_URL.startswith("postgresql")


def get_sqlite_path():
    """从SQLite连接字符串中提取数据库文件路径"""
    # 格式: sqlite:///./path/to/db.sqlite
    if DATABASE_URL.startswith("sqlite:///"):
        path = DATABASE_URL.replace("sqlite:///", "")
        # 处理相对路径
        if path.startswith("./"):
            path = path[2:]
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), path)
    return None


def get_pg_connection_params():
    """从PostgreSQL连接字符串中提取连接参数"""
    # 格式: postgresql://user:password@host:port/dbname
    if not is_postgresql():
        return None
    
    # 移除协议部分
    conn_string = DATABASE_URL.replace("postgresql://", "")
    
    # 分离用户凭据和主机信息
    if "@" in conn_string:
        credentials, host_info = conn_string.split("@")
    else:
        credentials, host_info = "", conn_string
    
    # 分离用户名和密码
    if ":" in credentials:
        username, password = credentials.split(":")
    else:
        username, password = credentials, ""
    
    # 分离主机/端口和数据库名
    if "/" in host_info:
        host_port, dbname = host_info.split("/")
    else:
        host_port, dbname = host_info, ""
    
    # 分离主机和端口
    if ":" in host_port:
        host, port = host_port.split(":")
    else:
        host, port = host_port, "5432"
    
    return {
        "host": host,
        "port": port,
        "user": username,
        "password": password,
        "dbname": dbname
    }


def backup_sqlite(backup_path=None):
    """备份SQLite数据库"""
    db_path = get_sqlite_path()
    if not db_path or not os.path.exists(db_path):
        print(f"错误: 找不到SQLite数据库文件: {db_path}")
        return False
    
    # 如果未指定备份路径，则使用默认路径
    if not backup_path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"waste_transport_{timestamp}.sqlite")
    
    try:
        # 简单复制文件作为备份
        shutil.copy2(db_path, backup_path)
        print(f"SQLite数据库已成功备份到: {backup_path}")
        return True
    except Exception as e:
        print(f"备份SQLite数据库时出错: {e}")
        return False


def backup_postgresql(backup_path=None):
    """备份PostgreSQL数据库"""
    params = get_pg_connection_params()
    if not params:
        print("错误: 无法解析PostgreSQL连接参数")
        return False
    
    # 如果未指定备份路径，则使用默认路径
    if not backup_path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"waste_transport_{timestamp}.sql")
    
    # 构建pg_dump命令
    cmd = [
        "pg_dump",
        "-h", params["host"],
        "-p", params["port"],
        "-U", params["user"],
        "-d", params["dbname"],
        "-f", backup_path,
        "--format=p"  # 纯文本SQL格式
    ]
    
    # 设置PGPASSWORD环境变量
    env = os.environ.copy()
    if params["password"]:
        env["PGPASSWORD"] = params["password"]
    
    try:
        # 执行pg_dump命令
        process = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        print(f"PostgreSQL数据库已成功备份到: {backup_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"备份PostgreSQL数据库时出错: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"备份过程中发生异常: {e}")
        return False


def restore_sqlite(backup_path):
    """从备份恢复SQLite数据库"""
    if not os.path.exists(backup_path):
        print(f"错误: 备份文件不存在: {backup_path}")
        return False
    
    db_path = get_sqlite_path()
    if not db_path:
        print("错误: 无法确定SQLite数据库路径")
        return False
    
    try:
        # 如果数据库文件已存在，先创建备份
        if os.path.exists(db_path):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_before_restore = f"{db_path}.{timestamp}.bak"
            shutil.copy2(db_path, backup_before_restore)
            print(f"已创建现有数据库的备份: {backup_before_restore}")
        
        # 复制备份文件到数据库位置
        shutil.copy2(backup_path, db_path)
        print(f"SQLite数据库已从 {backup_path} 成功恢复")
        return True
    except Exception as e:
        print(f"恢复SQLite数据库时出错: {e}")
        return False


def restore_postgresql(backup_path):
    """从备份恢复PostgreSQL数据库"""
    if not os.path.exists(backup_path):
        print(f"错误: 备份文件不存在: {backup_path}")
        return False
    
    params = get_pg_connection_params()
    if not params:
        print("错误: 无法解析PostgreSQL连接参数")
        return False
    
    # 构建psql命令
    cmd = [
        "psql",
        "-h", params["host"],
        "-p", params["port"],
        "-U", params["user"],
        "-d", params["dbname"],
        "-f", backup_path
    ]
    
    # 设置PGPASSWORD环境变量
    env = os.environ.copy()
    if params["password"]:
        env["PGPASSWORD"] = params["password"]
    
    try:
        # 执行psql命令
        process = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        print(f"PostgreSQL数据库已从 {backup_path} 成功恢复")
        return True
    except subprocess.CalledProcessError as e:
        print(f"恢复PostgreSQL数据库时出错: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"恢复过程中发生异常: {e}")
        return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python db_backup.py [backup|restore] [备份文件路径]")
        return
    
    action = sys.argv[1].lower()
    backup_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if action == "backup":
        if is_sqlite():
            backup_sqlite(backup_path)
        elif is_postgresql():
            backup_postgresql(backup_path)
        else:
            print(f"错误: 不支持的数据库类型: {DATABASE_URL}")
    elif action == "restore":
        if not backup_path:
            print("错误: 恢复操作需要指定备份文件路径")
            return
        
        if is_sqlite():
            restore_sqlite(backup_path)
        elif is_postgresql():
            restore_postgresql(backup_path)
        else:
            print(f"错误: 不支持的数据库类型: {DATABASE_URL}")
    else:
        print(f"错误: 未知操作 '{action}'。请使用 'backup' 或 'restore'")


if __name__ == "__main__":
    main()