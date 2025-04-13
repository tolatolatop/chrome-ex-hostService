from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db
from app.models.school import (
    Teacher as TeacherModel,
    Course as CourseModel,
    Student as StudentModel,
    Grade as GradeModel
)
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/school",
    tags=["school"],
    responses={404: {"description": "Not found"}},
)

# Pydantic 模型


class TeacherBase(BaseModel):
    name: str = Field(..., description="教师姓名", example="张三")
    email: str = Field(..., description="教师邮箱", example="zhangsan@example.com")


class TeacherCreate(TeacherBase):
    pass


class Teacher(TeacherBase):
    id: int = Field(..., description="教师ID", example=1)

    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    name: str = Field(..., description="课程名称", example="高等数学")
    description: str = Field(..., description="课程描述", example="大学基础数学课程")


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: int = Field(..., description="课程ID", example=1)
    teachers: List[Teacher] = Field(default=[], description="授课教师列表")

    class Config:
        from_attributes = True


class StudentBase(BaseModel):
    name: str = Field(..., description="学生姓名", example="李四")
    email: str = Field(..., description="学生邮箱", example="lisi@example.com")


class StudentCreate(StudentBase):
    pass


class Student(StudentBase):
    id: int = Field(..., description="学生ID", example=1)

    class Config:
        from_attributes = True


class GradeBase(BaseModel):
    score: float = Field(..., description="成绩分数", example=85.5, ge=0, le=100)
    student_id: int = Field(..., description="学生ID", example=1)
    course_id: int = Field(..., description="课程ID", example=1)


class GradeCreate(GradeBase):
    pass


class Grade(GradeBase):
    id: int = Field(..., description="成绩ID", example=1)
    student: Student = Field(..., description="学生信息")
    course: Course = Field(..., description="课程信息")

    class Config:
        from_attributes = True

# 教师相关API


@router.post(
    "/teachers/",
    response_model=Teacher,
    summary="创建新教师",
    description="创建一个新的教师记录",
    response_description="返回创建的教师信息"
)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = TeacherModel(**teacher.model_dump())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.get(
    "/teachers/",
    response_model=List[Teacher],
    summary="获取教师列表",
    description="获取所有教师的列表，支持分页",
    response_description="返回教师列表"
)
def read_teachers(
    skip: int = Query(0, description="跳过的记录数", example=0),
    limit: int = Query(100, description="返回的最大记录数", example=100),
    db: Session = Depends(get_db)
):
    teachers = db.query(TeacherModel).offset(skip).limit(limit).all()
    return teachers


@router.get(
    "/teachers/{teacher_id}",
    response_model=Teacher,
    summary="获取教师详情",
    description="根据ID获取特定教师的详细信息",
    response_description="返回教师详细信息"
)
def read_teacher(
    teacher_id: int = Path(..., description="教师ID", example=1),
    db: Session = Depends(get_db)
):
    teacher = db.query(TeacherModel).filter(
        TeacherModel.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

# 课程相关API


@router.post(
    "/courses/",
    response_model=Course,
    summary="创建新课程",
    description="创建一个新的课程记录",
    response_description="返回创建的课程信息"
)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    db_course = CourseModel(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@router.get(
    "/courses/",
    response_model=List[Course],
    summary="获取课程列表",
    description="获取所有课程的列表，支持分页",
    response_description="返回课程列表"
)
def read_courses(
    skip: int = Query(0, description="跳过的记录数", example=0),
    limit: int = Query(100, description="返回的最大记录数", example=100),
    db: Session = Depends(get_db)
):
    courses = db.query(CourseModel).offset(skip).limit(limit).all()
    return courses


@router.get(
    "/courses/{course_id}",
    response_model=Course,
    summary="获取课程详情",
    description="根据ID获取特定课程的详细信息",
    response_description="返回课程详细信息"
)
def read_course(
    course_id: int = Path(..., description="课程ID", example=1),
    db: Session = Depends(get_db)
):
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# 学生相关API


@router.post(
    "/students/",
    response_model=Student,
    summary="创建新学生",
    description="创建一个新的学生记录",
    response_description="返回创建的学生信息"
)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = StudentModel(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.get(
    "/students/",
    response_model=List[Student],
    summary="获取学生列表",
    description="获取所有学生的列表，支持分页",
    response_description="返回学生列表"
)
def read_students(
    skip: int = Query(0, description="跳过的记录数", example=0),
    limit: int = Query(100, description="返回的最大记录数", example=100),
    db: Session = Depends(get_db)
):
    students = db.query(StudentModel).offset(skip).limit(limit).all()
    return students


@router.get(
    "/students/{student_id}",
    response_model=Student,
    summary="获取学生详情",
    description="根据ID获取特定学生的详细信息",
    response_description="返回学生详细信息"
)
def read_student(
    student_id: int = Path(..., description="学生ID", example=1),
    db: Session = Depends(get_db)
):
    student = db.query(StudentModel).filter(
        StudentModel.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# 成绩相关API


@router.post(
    "/grades/",
    response_model=Grade,
    summary="创建新成绩",
    description="创建一个新的成绩记录",
    response_description="返回创建的成绩信息"
)
def create_grade(grade: GradeCreate, db: Session = Depends(get_db)):
    # 检查学生和课程是否存在
    student = db.query(StudentModel).filter(
        StudentModel.id == grade.student_id).first()
    course = db.query(CourseModel).filter(
        CourseModel.id == grade.course_id).first()

    if not student or not course:
        raise HTTPException(
            status_code=404, detail="Student or Course not found")

    db_grade = GradeModel(**grade.model_dump())
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade


@router.get(
    "/grades/",
    response_model=List[Grade],
    summary="获取成绩列表",
    description="获取所有成绩的列表，支持分页",
    response_description="返回成绩列表"
)
def read_grades(
    skip: int = Query(0, description="跳过的记录数", example=0),
    limit: int = Query(100, description="返回的最大记录数", example=100),
    db: Session = Depends(get_db)
):
    grades = db.query(GradeModel).offset(skip).limit(limit).all()
    return grades


@router.get(
    "/grades/{grade_id}",
    response_model=Grade,
    summary="获取成绩详情",
    description="根据ID获取特定成绩的详细信息",
    response_description="返回成绩详细信息"
)
def read_grade(
    grade_id: int = Path(..., description="成绩ID", example=1),
    db: Session = Depends(get_db)
):
    grade = db.query(GradeModel).filter(GradeModel.id == grade_id).first()
    if grade is None:
        raise HTTPException(status_code=404, detail="Grade not found")
    return grade

# 教师-课程关联API


@router.post(
    "/teachers/{teacher_id}/courses/{course_id}",
    summary="分配教师到课程",
    description="将特定教师分配到特定课程",
    response_description="返回操作结果"
)
def add_teacher_to_course(
    teacher_id: int = Path(..., description="教师ID", example=1),
    course_id: int = Path(..., description="课程ID", example=1),
    db: Session = Depends(get_db)
):
    teacher = db.query(TeacherModel).filter(
        TeacherModel.id == teacher_id).first()
    course = db.query(CourseModel).filter(CourseModel.id == course_id).first()

    if not teacher or not course:
        raise HTTPException(
            status_code=404, detail="Teacher or Course not found")

    if course not in teacher.courses:
        teacher.courses.append(course)
        db.commit()

    return {"message": "Teacher added to course successfully"}
