from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

# 教师-课程关联表
teacher_course = Table(
    'teacher_course',
    Base.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # 关系
    courses = relationship(
        "Course", secondary=teacher_course, back_populates="teachers")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

    # 关系
    teachers = relationship(
        "Teacher", secondary=teacher_course, back_populates="courses")
    grades = relationship("Grade", back_populates="course")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # 关系
    grades = relationship("Grade", back_populates="student")


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    score = Column(Float)
    student_id = Column(Integer, ForeignKey("students.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    # 关系
    student = relationship("Student", back_populates="grades")
    course = relationship("Course", back_populates="grades")
