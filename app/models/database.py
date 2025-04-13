import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.settings import SQL_URI, get_db_connect_args

# 默认使用内存中的SQLite数据库
DEFAULT_DATABASE_URL = "sqlite:///:memory:"

# 从环境变量获取数据库URL，如果没有则使用默认值
SQLALCHEMY_DATABASE_URL = os.getenv("SQL_URI", DEFAULT_DATABASE_URL)

# 根据数据库类型设置不同的连接参数
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQL_URI,
    connect_args=get_db_connect_args(),
    pool_pre_ping=True  # 启用连接池健康检查
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 依赖项


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
