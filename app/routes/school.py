from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models.database import get_db
from ..models.models import Teacher, Course, Student, Grade
from pydantic import BaseModel

router = APIRouter(prefix="/school", tags=["school"])

# Pydantic 模型


class TeacherBase(BaseModel):
    name: str
    email: str


class TeacherCreate(TeacherBase):
    pass


class Teacher(TeacherBase):
    id: int

    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    name: str
    description: str


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: int
    teachers: List[Teacher] = []

    class Config:
        from_attributes = True


class StudentBase(BaseModel):
    name: str
    email: str


class StudentCreate(StudentBase):
    pass


class Student(StudentBase):
    id: int

    class Config:
        from_attributes = True


class GradeBase(BaseModel):
    score: float
    student_id: int
    course_id: int


class GradeCreate(GradeBase):
    pass


class Grade(GradeBase):
    id: int
    student: Student
    course: Course

    class Config:
        from_attributes = True

# 教师相关API


@router.post("/teachers/", response_model=Teacher)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = Teacher(**teacher.model_dump())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.get("/teachers/", response_model=List[Teacher])
def read_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teachers = db.query(Teacher).offset(skip).limit(limit).all()
    return teachers


@router.get("/teachers/{teacher_id}", response_model=Teacher)
def read_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

# 课程相关API


@router.post("/courses/", response_model=Course)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    db_course = Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@router.get("/courses/", response_model=List[Course])
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses


@router.get("/courses/{course_id}", response_model=Course)
def read_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# 学生相关API


@router.post("/students/", response_model=Student)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.get("/students/", response_model=List[Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(Student).offset(skip).limit(limit).all()
    return students


@router.get("/students/{student_id}", response_model=Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# 成绩相关API


@router.post("/grades/", response_model=Grade)
def create_grade(grade: GradeCreate, db: Session = Depends(get_db)):
    # 检查学生和课程是否存在
    student = db.query(Student).filter(Student.id == grade.student_id).first()
    course = db.query(Course).filter(Course.id == grade.course_id).first()

    if not student or not course:
        raise HTTPException(
            status_code=404, detail="Student or Course not found")

    db_grade = Grade(**grade.model_dump())
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade


@router.get("/grades/", response_model=List[Grade])
def read_grades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    grades = db.query(Grade).offset(skip).limit(limit).all()
    return grades


@router.get("/grades/{grade_id}", response_model=Grade)
def read_grade(grade_id: int, db: Session = Depends(get_db)):
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if grade is None:
        raise HTTPException(status_code=404, detail="Grade not found")
    return grade

# 教师-课程关联API


@router.post("/teachers/{teacher_id}/courses/{course_id}")
def add_teacher_to_course(teacher_id: int, course_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    course = db.query(Course).filter(Course.id == course_id).first()

    if not teacher or not course:
        raise HTTPException(
            status_code=404, detail="Teacher or Course not found")

    if course not in teacher.courses:
        teacher.courses.append(course)
        db.commit()

    return {"message": "Teacher added to course successfully"}
