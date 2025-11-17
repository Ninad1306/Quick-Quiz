from sqlalchemy.orm import mapped_column, relationship, validates
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy import sql
from flask_sqlalchemy import SQLAlchemy
from app.constants import *
import re

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

    course_id = mapped_column(String(8), primary_key=True)
    course_name = mapped_column(String(64), nullable=False)
    course_level = mapped_column(String(64), nullable=False)
    course_objectives = mapped_column(Text, nullable=True)

    teacher_courses_maps = relationship(
        'Teacher_Courses_Map',
        back_populates='course',
        cascade='all, delete-orphan'
    )

    @validates('course_id')
    def validate_course_id(self, key, course_id):
        if len(course_id) == 0:
            raise ValueError(f"Course ID should not be empty")
        if len(course_id) > MAX_COURSE_LENGTH:
            raise ValueError(f"Course ID should be {MAX_COURSE_LENGTH} character or less")
        if not course_id.isalnum():
            raise ValueError(f"Course ID cannot be empty or include special characters")
        return course_id

    @validates('course_name')
    def validate_course_name(self, key, course_name):
        if not course_name or len(course_name)==0:
            raise ValueError(f"Course name should not be empty")
        return course_name

    @validates('course_level')
    def validate_course_level(self, key, course_level):
        if course_level not in COURSE_LEVELS:
            raise ValueError("Invalid course level specified")
        return course_level
    
class Teacher_Courses_Map(db.Model):
    __tablename__ = 'teacher_courses_map'

    teacher_id = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    course_id = mapped_column(String(64), ForeignKey('courses.course_id'), nullable=False)
    offered_at = mapped_column(String(64), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('teacher_id', 'course_id', 'offered_at'),
    )

    course = relationship(
        'Courses',
        back_populates='teacher_courses_maps',
    )


    @validates('offered_at')
    def validate_offered_at(self, key, offered_at):
        existing_mapping = Teacher_Courses_Map.query.filter_by(course_id=self.course_id, offered_at=offered_at).first()
        if existing_mapping:
            raise ValueError(f"Course {self.course_id} is already being offered in {offered_at}")

        if offered_at.isdigit():
            year = int(offered_at)
            if MIN_YEAR_COURSE_OFFERING <= year <= MAX_YEAR_COURSE_OFFERING:
                return offered_at
            else:
                raise ValueError(f"Year must be between {MIN_YEAR_COURSE_OFFERING} and {MAX_YEAR_COURSE_OFFERING}")
        
        semester_pattern = r"^(Fall|Spring)_(\d{4})$"
        match = re.match(semester_pattern, offered_at)

        if match:
            semester, year = match.groups()
            year = int(year)
            if MIN_YEAR_COURSE_OFFERING <= year <= MAX_YEAR_COURSE_OFFERING:
                return offered_at
            else:
                raise ValueError(f"offered_at should be must be either a year within the range ({MIN_YEAR_COURSE_OFFERING}, {MAX_YEAR_COURSE_OFFERING}) or in the form Fall_Year/Spring_Year ")
        
        return offered_at

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
    
    