import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.settings import SQL_URI, get_db_connect_args

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
