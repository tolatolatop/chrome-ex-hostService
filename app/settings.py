import os
from typing import Optional

# 数据库配置
DEFAULT_DATABASE_URL = "sqlite:///:memory:"
SQL_URI: str = os.getenv("SQL_URI", DEFAULT_DATABASE_URL)

# 数据库连接参数


def get_db_connect_args() -> dict:
    if SQL_URI.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}
