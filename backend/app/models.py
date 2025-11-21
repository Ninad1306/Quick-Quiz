from sqlalchemy.orm import mapped_column, relationship, validates
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy import sql, event
from flask_sqlalchemy import SQLAlchemy
from app.constants import *
import re, json

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(64), nullable=False)
    email = mapped_column(String(64), unique=True, nullable=False)
    role = mapped_column(String(64), nullable=False)
    password = mapped_column(String(128), nullable=False)
    creation_time = mapped_column(DateTime, default=sql.func.now(), nullable=False)


class Courses(db.Model):
    __tablename__ = "courses"

    course_id = mapped_column(String(8), primary_key=True)
    course_name = mapped_column(String(64), nullable=False)
    course_level = mapped_column(String(64), nullable=False)
    course_objectives = mapped_column(Text, nullable=True)

    teacher_courses_maps = relationship(
        "Teacher_Courses_Map", back_populates="course", cascade="all, delete-orphan"
    )

    @validates("course_id")
    def validate_course_id(self, key, course_id):
        if len(course_id) == 0:
            raise ValueError(f"Course ID should not be empty")
        if len(course_id) > MAX_COURSE_LENGTH:
            raise ValueError(
                f"Course ID should be {MAX_COURSE_LENGTH} character or less"
            )
        if not course_id.isalnum():
            raise ValueError(f"Course ID cannot be empty or include special characters")
        return course_id

    @validates("course_name")
    def validate_course_name(self, key, course_name):
        if not course_name or len(course_name) == 0:
            raise ValueError(f"Course name should not be empty")
        return course_name

    @validates("course_level")
    def validate_course_level(self, key, course_level):
        if course_level not in COURSE_LEVELS:
            raise ValueError("Invalid course level specified")
        return course_level


class Teacher_Courses_Map(db.Model):
    __tablename__ = "teacher_courses_map"

    teacher_id = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    course_id = mapped_column(
        String(64), ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False
    )
    offered_at = mapped_column(String(64), nullable=False)

    __table_args__ = (db.PrimaryKeyConstraint("teacher_id", "course_id", "offered_at"),)

    course = relationship(
        "Courses",
        back_populates="teacher_courses_maps",
    )

    @validates("offered_at")
    def validate_offered_at(self, key, offered_at):
        existing_mapping = Teacher_Courses_Map.query.filter_by(
            course_id=self.course_id, offered_at=offered_at
        ).first()
        if existing_mapping:
            raise ValueError(
                f"Course {self.course_id} is already being offered in {offered_at}"
            )

        if offered_at.isdigit():
            year = int(offered_at)
            if MIN_YEAR_COURSE_OFFERING <= year <= MAX_YEAR_COURSE_OFFERING:
                return offered_at
            else:
                raise ValueError(
                    f"Year must be between {MIN_YEAR_COURSE_OFFERING} and {MAX_YEAR_COURSE_OFFERING}"
                )

        semester_pattern = r"^(Fall|Spring)_(\d{4})$"
        match = re.match(semester_pattern, offered_at)

        if match:
            semester, year = match.groups()
            year = int(year)
            if MIN_YEAR_COURSE_OFFERING <= year <= MAX_YEAR_COURSE_OFFERING:
                return offered_at
            else:
                raise ValueError(
                    f"offered_at should be must be either a year within the range ({MIN_YEAR_COURSE_OFFERING}, {MAX_YEAR_COURSE_OFFERING}) or in the form Fall_Year/Spring_Year "
                )

        return offered_at


class Student_Courses_Map(db.Model):
    __tablename__ = "student_courses_map"

    student_id = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    course_id = mapped_column(
        String(64), ForeignKey("courses.course_id"), nullable=False
    )
    taken_at = mapped_column(DateTime, default=sql.func.now(), nullable=False)
    __table_args__ = (db.PrimaryKeyConstraint("student_id", "course_id"),)


class Tests(db.Model):
    __tablename__ = "tests"

    test_id = mapped_column(Integer, primary_key=True)
    course_id = mapped_column(
        String(64), ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False
    )
    title = mapped_column(String(128), nullable=False)
    description = mapped_column(String(512), nullable=True)
    difficulty_level = mapped_column(
        String(32), nullable=False
    )  # Options: Easy, Medium, Hard
    created_at = mapped_column(DateTime, default=sql.func.now(), nullable=False)
    start_time = mapped_column(DateTime, nullable=True)
    duration_minutes = mapped_column(
        Integer, nullable=False
    )  # Duration of the test in minutes
    total_questions = mapped_column(Integer, nullable=False)
    total_marks = mapped_column(Integer, nullable=False)
    passing_marks = mapped_column(Integer, nullable=False)
    created_by = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )  # Teacher who created the test
    status = mapped_column(
        String(32), nullable=False
    )  # One of NotPublished, Published, Active, Completed

    __table_args__ = (
        db.UniqueConstraint("course_id", "title", name="uix_course_title"),
    )

    questions = relationship(
        "Questions",
        back_populates="test",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    attempts = relationship(
        "StudentTestAttempt",
        back_populates="test",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @validates("course_id")
    def validate_course_id(self, key, course_id):
        course = Courses.query.filter_by(course_id=course_id).first()
        if not course:
            raise ValueError("Invalid course ID")
        return course_id

    @validates("title")
    def validate_title(self, key, title):
        if len(title) == 0:
            raise ValueError("Title cannot be empty")
        return title

    @validates("difficulty_level")
    def validate_difficulty_level(self, key, difficulty_level):
        if difficulty_level.lower() not in ["easy", "medium", "hard"]:
            raise ValueError("Difficulty level should be one of Easy, Medium or Hard")
        return difficulty_level

    @validates("duration_minutes")
    def validate_duration(self, key, duration):
        if not isinstance(duration, int):
            raise ValueError("Duration should be an integer value")
        return duration

    @validates("total_questions")
    def validate_total_questions(self, key, total_questions):
        if not isinstance(total_questions, int):
            raise ValueError("Total marks should be an integer value")
        if total_questions > MAX_QUESTIONS:
            raise ValueError(f"Maximum of {MAX_QUESTIONS} allowed")
        return total_questions

    @validates("total_marks")
    def validate_total_marks(self, key, total_marks):
        if not isinstance(total_marks, int):
            raise ValueError("Total marks should be an integer value")
        return total_marks

    @validates("passing_marks")
    def validate_passing_marks(self, key, passing_marks):
        if not isinstance(passing_marks, int):
            raise ValueError("Passing marks should be an integer value")
        return passing_marks

    @validates("status")
    def validate_status(self, key, status):
        if status not in ["not_published", "published", "active", "completed"]:
            raise ValueError(
                "Status must be one of not_published, published, active, completed"
            )
        return status

    def to_dict(self):
        return {
            "test_id": self.test_id,
            "course_id": self.course_id,
            "title": self.title,
            "description": self.description,
            "difficulty_level": self.difficulty_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "duration_minutes": self.duration_minutes,
            "total_questions": self.total_questions,
            "total_marks": self.total_marks,
            "passing_marks": self.passing_marks,
            "created_by": self.created_by,
            "status": self.status,
        }


class Questions(db.Model):
    __tablename__ = "questions"

    question_id = mapped_column(Integer, primary_key=True)
    question_type = mapped_column(String(32), nullable=False)
    test_id = mapped_column(
        Integer, ForeignKey("tests.test_id", ondelete="CASCADE"), nullable=False
    )
    question_text = mapped_column(String(1024), nullable=False)
    options = mapped_column(String(1024), nullable=True)
    correct_answer = mapped_column(
        String(32), nullable=False
    )  # e.g., 'A', 'B', 'C', 'D' or ['A','B'] for multiple correct options
    tags = mapped_column(String(512), nullable=False)
    marks = mapped_column(Float, nullable=False)
    difficulty_level = mapped_column(String(32), nullable=False)
    created_at = mapped_column(DateTime, default=sql.func.now(), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("test_id", "question_text", name="uix_test_question"),
    )

    test = relationship("Tests", back_populates="questions")

    question_attempts = relationship(
        "StudentQuestionAttempt",
        back_populates="question",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @validates("question_text")
    def validates_question_text(self, key, question_text):
        if not isinstance(question_text, str):
            raise ValueError("question_type should be string")
        if len(question_text) == 0:
            raise ValueError("question_text cannot be empty")
        return question_text

    @validates("question_type")
    def validates_question_type(self, key, question_type):
        if question_type.lower() not in {"mcq", "msq", "nat"}:
            raise ValueError("question_type should be one of mcq, msq or nat.")
        return question_type

    @validates("options")
    def validate_options(self, key, options):
        if isinstance(options, str):
            try:
                options = json.loads(options)
            except Exception:
                raise ValueError("Failed to convert options to JSON")

        if not isinstance(options, list):
            raise ValueError("Options must be JSON-serializable list")

        return json.dumps(options)

    @validates("correct_answer")
    def validate_correct_answer(self, key, correct_answer):
        if isinstance(correct_answer, str):
            try:
                if len(correct_answer) > 1:
                    correct_answer = json.loads(correct_answer)
            except Exception as e:
                raise ValueError(f"Failed to convert correct_answer to JSON: {e}")
        return json.dumps(correct_answer)

    @validates("tags")
    def validate_tags(self, key, tags):
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except Exception as e:
                raise ValueError(f"Failed to convert tags to JSON: {e}")

        if not (isinstance(tags, list) and all(isinstance(tag, str) for tag in tags)):
            raise ValueError("tags should be a list of strings.")
        return json.dumps(tags)

    @validates("difficulty_level")
    def validate_difficulty_level(self, key, difficulty_level):
        if difficulty_level.lower() not in {"easy", "medium", "hard"}:
            raise ValueError("difficulty_level should be one of easy, medium or hard.")
        return difficulty_level

    def to_dict(self, include_answer=False):
        result = {
            "question_id": self.question_id,
            "test_id": self.test_id,
            "question_text": self.question_text,
            "options": json.loads(self.options) if self.options else None,
            "difficulty_level": self.difficulty_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tags": json.loads(self.tags),
            "marks": self.marks,
            "question_type": self.question_type,
        }

        if include_answer:
            result["correct_answer"] = json.loads(self.correct_answer)

        return result


@event.listens_for(Questions, "before_insert")
@event.listens_for(Questions, "before_update")
def validate_question(mapper, connection, target):
    qtype = target.question_type.lower()
    options = (
        json.loads(target.options)
        if isinstance(target.options, str)
        else target.options
    )

    if isinstance(target.correct_answer, str):
        if target.correct_answer.isdigit():
            answer = int(target.correct_answer)
        elif len(target.correct_answer) == 3:
            answer = target.correct_answer
        else:
            answer = json.loads(target.correct_answer)
    elif isinstance(target.correct_answer, list):
        answer = json.loads(target.correct_answer)
    else:
        raise ValueError(f"Invalid correct_answer data type.")

    if qtype in ("mcq", "msq") and not (isinstance(options, list) and options):
        raise ValueError(
            f"{qtype.upper()} question requires a non-empty list of options"
        )

    if qtype == "mcq" and not isinstance(answer, str):
        raise ValueError("MCQ correct_answer must be a single string")

    if qtype == "msq" and not (
        isinstance(answer, list) and all(isinstance(a, str) for a in answer)
    ):
        raise ValueError("MSQ correct_answer must be a list of strings")

    if qtype == "nat" and not isinstance(answer, int):
        raise ValueError("NAT correct_answer must be an integer")


# IMPROVED SCHEMA FOR STUDENT ATTEMPTS


class StudentTestAttempt(db.Model):
    """
    Main attempt record - one per test attempt by a student.
    Tracks overall attempt metadata and scoring.
    """

    __tablename__ = "student_test_attempt"

    attempt_id = mapped_column(Integer, primary_key=True)
    student_id = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    test_id = mapped_column(
        Integer, ForeignKey("tests.test_id", ondelete="CASCADE"), nullable=False
    )

    # Timestamps
    started_at = mapped_column(DateTime, default=sql.func.now(), nullable=False)
    submitted_at = mapped_column(DateTime, nullable=True)

    # Scoring
    total_score = mapped_column(Float, default=0.0, nullable=False)
    percentage = mapped_column(Float, nullable=True)
    passed = mapped_column(Boolean, nullable=True)

    # Status tracking
    status = mapped_column(
        String(32), nullable=False, default="in_progress"
    )  # in_progress, submitted, auto_submitted

    # Duration tracking (actual time taken in seconds)
    time_taken_seconds = mapped_column(Integer, nullable=True)

    # IP and session tracking for security/analytics
    ip_address = mapped_column(String(45), nullable=True)
    user_agent = mapped_column(String(256), nullable=True)

    # Relationships
    test = relationship("Tests", back_populates="attempts")
    question_attempts = relationship(
        "StudentQuestionAttempt",
        back_populates="test_attempt",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="StudentQuestionAttempt.answered_at",
    )

    @validates("status")
    def validate_status(self, key, status):
        allowed_statuses = ["in_progress", "submitted", "auto_submitted"]
        if status not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return status

    def calculate_score(self):
        """Calculate total score from all question attempts"""
        self.total_score = sum(qa.marks_obtained or 0 for qa in self.question_attempts)

        # Calculate percentage
        if self.test and self.test.total_marks:
            self.percentage = round((self.total_score / self.test.total_marks) * 100, 2)

            # Determine pass/fail
            if self.test.passing_marks:
                self.passed = self.total_score >= self.test.passing_marks

        return self.total_score

    def to_dict(self, include_questions=False):
        result = {
            "attempt_id": self.attempt_id,
            "student_id": self.student_id,
            "test_id": self.test_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "submitted_at": (
                self.submitted_at.isoformat() if self.submitted_at else None
            ),
            "total_score": self.total_score,
            "percentage": self.percentage,
            "passed": self.passed,
            "status": self.status,
            "time_taken_seconds": self.time_taken_seconds,
        }

        if include_questions:
            result["questions"] = [qa.to_dict() for qa in self.question_attempts]

        return result


class StudentQuestionAttempt(db.Model):
    """
    Individual question attempt within a test attempt.
    Tracks answer given, correctness, and timing.
    """

    __tablename__ = "student_question_attempt"

    id = mapped_column(Integer, primary_key=True)
    attempt_id = mapped_column(
        Integer,
        ForeignKey("student_test_attempt.attempt_id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id = mapped_column(
        Integer, ForeignKey("questions.question_id", ondelete="CASCADE"), nullable=False
    )

    # Answer tracking
    selected_answer = mapped_column(
        Text, nullable=True
    )  # JSON string: can be single value, list, or numeric
    is_correct = mapped_column(Boolean, nullable=True)
    marks_obtained = mapped_column(Float, default=0.0, nullable=False)

    # Timing
    answered_at = mapped_column(DateTime, default=sql.func.now(), nullable=False)
    time_spent_seconds = mapped_column(
        Integer, nullable=True
    )  # Time spent on this specific question

    # Answer change tracking (for analytics)
    answer_changed = mapped_column(Boolean, default=False, nullable=False)
    answer_change_count = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    test_attempt = relationship(
        "StudentTestAttempt", back_populates="question_attempts"
    )
    question = relationship("Questions", back_populates="question_attempts")

    __table_args__ = (
        db.UniqueConstraint("attempt_id", "question_id", name="uix_attempt_question"),
    )

    def check_answer(self):
        """
        Evaluate if the answer is correct and calculate marks.
        Returns: (is_correct, marks_obtained)
        """
        if not self.question:
            return False, 0.0

        try:
            # Parse correct answer
            correct_answer = json.loads(self.question.correct_answer)

            # Parse selected answer
            if self.selected_answer:
                selected = json.loads(self.selected_answer)
            else:
                selected = None

            question_type = self.question.question_type.lower()
            is_correct = False

            if question_type == "mcq":
                # Single correct answer
                is_correct = selected == correct_answer

            elif question_type == "msq":
                # Multiple correct answers - must match exactly
                if isinstance(selected, list) and isinstance(correct_answer, list):
                    is_correct = sorted(selected) == sorted(correct_answer)

            elif question_type == "nat":
                # Numeric answer with tolerance
                if selected is not None:
                    try:
                        is_correct = abs(float(selected) - float(correct_answer)) < 0.01
                    except (ValueError, TypeError):
                        is_correct = False

            # Calculate marks
            marks = float(self.question.marks) if is_correct else 0.0

            self.is_correct = is_correct
            self.marks_obtained = marks

            return is_correct, marks

        except Exception as e:
            print(f"Error checking answer: {e}")
            self.is_correct = False
            self.marks_obtained = 0.0
            return False, 0.0

    def to_dict(self, include_correct_answer=False):
        result = {
            "id": self.id,
            "attempt_id": self.attempt_id,
            "question_id": self.question_id,
            "selected_answer": (
                json.loads(self.selected_answer) if self.selected_answer else None
            ),
            "is_correct": self.is_correct,
            "marks_obtained": self.marks_obtained,
            "answered_at": self.answered_at.isoformat() if self.answered_at else None,
            "time_spent_seconds": self.time_spent_seconds,
            "answer_changed": self.answer_changed,
            "answer_change_count": self.answer_change_count,
        }

        if include_correct_answer and self.question:
            result["correct_answer"] = json.loads(self.question.correct_answer)
            result["question_text"] = self.question.question_text

        return result
