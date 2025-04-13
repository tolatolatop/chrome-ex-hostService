from .database import engine, Base
from .school import Teacher, Course, Student, Grade


def init_db():
    # 创建所有表
    Base.metadata.create_all(bind=engine)
