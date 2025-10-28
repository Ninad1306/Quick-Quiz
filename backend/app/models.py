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
    course_id = mapped_column(String(64), ForeignKey('courses.course_id'), nullable=False)
    offered_at = mapped_column(DateTime, default=sql.func.now(), nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint('teacher_id', 'course_id'),
    )

class Student_Courses_Map(db.Model):
    __tablename__ = 'student_courses_map'

    student_id = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    course_id = mapped_column(String(64), ForeignKey('courses.course_id'), nullable=False)
    taken_at = mapped_column(DateTime, default=sql.func.now(), nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint('student_id', 'course_id'),
    )

class Tests(db.Model):
    __tablename__ = 'tests'

    test_id = mapped_column(Integer, primary_key=True)
    course_id = mapped_column(String(64), ForeignKey('courses.course_id'), nullable=False)
    title = mapped_column(String(128), nullable=False)
    description = mapped_column(String(256), nullable=True)
    difficulty_level = mapped_column(String(32), nullable=False) # e.g., Easy, Medium, Hard
    created_at = mapped_column(DateTime, default=sql.func.now(), nullable=False)
    published_at = mapped_column(DateTime, nullable=True)
    duration_minutes = mapped_column(Integer, nullable=False)  # Duration of the test in minutes
    total_marks = mapped_column(Integer, nullable=False)
    passing_marks = mapped_column(Integer, nullable=False)
    created_by = mapped_column(Integer, ForeignKey('user.id'), nullable=False)  # Teacher who created the test
    __table_args__ = (
        db.UniqueConstraint('course_id', 'title', name='uix_course_title'),
    )
class Questions(db.Model):
    __tablename__ = 'questions'

    question_id = mapped_column(Integer, primary_key=True)
    test_id = mapped_column(Integer, ForeignKey('tests.test_id'), nullable=False)
    question_text = mapped_column(String(512), nullable=False)
    options = mapped_column(String(512), nullable=False)
    correct_options = mapped_column(String(32), nullable=False)  # e.g., 'A', 'B', 'C', 'D' or ['A','B'] for multiple correct options
    marks = mapped_column(Integer, nullable=False)
    created_at = mapped_column(DateTime, default=sql.func.now(), nullable=False)
    __table_args__ = (
        db.UniqueConstraint('test_id', 'question_text', name='uix_test_question'),
    )
class Student_Test_Question_Attempt(db.Model):
    __tablename__ = 'student_test_question_attempt'

    question_id = mapped_column(Integer, ForeignKey('tests.test_id'), nullable=False)
    student_id = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    test_id = mapped_column(Integer, ForeignKey('tests.test_id'), nullable=False)
    selected_options = mapped_column(String(32), nullable=False)  # e.g., 'A', 'B', 'C', 'D' or ['A','B'] for multiple selected options
    marks_obtained = mapped_column(Integer, nullable=False)

    attempted_at = mapped_column(DateTime, default=sql.func.now(), nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint('question_id', 'student_id', 'test_id'),
    )
    
    