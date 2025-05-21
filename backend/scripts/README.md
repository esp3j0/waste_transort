# 工具脚本

本目录包含项目的各种工具脚本，用于辅助开发、部署和维护。

## 数据库备份和恢复

### 脚本说明

- `db_backup.py`: 数据库备份和恢复的Python脚本，支持SQLite和PostgreSQL数据库
- `db_backup.bat`: Windows环境下的批处理脚本，用于调用Python脚本

### 使用方法

#### 备份数据库

```bash
# Linux/Mac
python db_backup.py backup [备份文件路径]

# Windows
db_backup.bat backup [备份文件路径]
```

如果不指定备份文件路径，脚本会自动在项目根目录下的`backups`文件夹中创建一个带有时间戳的备份文件。

#### 恢复数据库

```bash
# Linux/Mac
python db_backup.py restore <备份文件路径>

# Windows
db_backup.bat restore <备份文件路径>
```

恢复操作必须指定备份文件路径。

### 注意事项

- 备份和恢复操作会使用`.env`文件中配置的数据库连接信息
- 对于PostgreSQL数据库，需要安装`pg_dump`和`psql`命令行工具
- 恢复操作会覆盖现有数据库，请谨慎操作
- 在恢复SQLite数据库前，脚本会自动创建现有数据库的备份