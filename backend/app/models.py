from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy import sql
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(64), nullable=False)
    email = mapped_column(String(64), unique=True, nullable=False)
    role = mapped_column(String(64), nullable=False)
    password = mapped_column(String(128), nullable=False)
    creation_time = mapped_column(DateTime, default=sql.func.now(), nullable=False)

class Courses(db.Model):
    __tablename__ = 'courses'

    course_id = mapped_column(Integer, primary_key=True)
    course_name = mapped_column(String(64), nullable=False)
    
class Teacher_Courses_Map(db.Model):
    __tablename__ = 'teacher_courses_map'

    teacher_id = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    course_name = mapped_column(String(64), ForeignKey('courses.course_id'), nullable=False)
    offered_at = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint('teacher_id', 'course_name'),
    )

class Student_Courses_Map(db.Model):
    __tablename__ = 'student_courses_map'

    student_id = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    course_name = mapped_column(String(64), ForeignKey('courses.course_id'), nullable=False)
    taken_at = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint('student_id', 'course_name'),
    )