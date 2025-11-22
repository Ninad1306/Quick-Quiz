from app.constants import *
from app import db, app
from app.models import Tests, Questions
import datetime, random


def get_current_semester_and_year():
    now = datetime.datetime.now()
    year = now.year

    if 1 <= now.month <= 6:
        semester = f"Spring_{year}"
    else:
        semester = f"Fall_{year}"

    return semester, str(year)


def get_question_type():
    r = random.random()
    if r > 0.4:
        return "mcq"
    elif r > 0.1:
        return "msq"
    else:
        return "nat"


def get_question_level(test_level):
    r = random.random()

    if test_level.lower() == "easy":
        if r > 0.9:
            return "hard"
        elif r > 0.7:
            return "medium"
        else:
            return "easy"

    if test_level.lower() == "medium":
        if r > 0.8:
            return "hard"
        elif r > 0.3:
            return "medium"
        else:
            return "easy"

    # Else test level hard
    if r > 0.6:
        return "hard"
    elif r > 0.2:
        return "medium"
    else:
        return "easy"


def get_mark_distribution(difficulty_list, total_marks):
    question_points = []
    for i in difficulty_list:
        if i.lower() == "easy":
            question_points.append(1)
        elif i.lower() == "medium":
            question_points.append(2)
        else:
            question_points.append(3)

    total_points = sum(question_points)
    weightage = [p / total_points for p in question_points]
    marks_per_question = [round(total_marks * w, 1) for w in weightage]

    if len(marks_per_question) != 0:
        marks_per_question[-1] = total_marks - sum(marks_per_question[:-1])

    return marks_per_question


def activate_test(quiz_id):
    with app.app_context():
        test_obj = Tests.query.filter_by(test_id=quiz_id).with_for_update().first()
        test_obj.status = "active"
        db.session.commit()


def deactivate_test(quiz_id):
    with app.app_context():
        test_obj = Tests.query.filter_by(test_id=quiz_id).with_for_update().first()
        test_obj.status = "completed"
        db.session.commit()


def recalibrate_marks(quiz_id, total_marks):
    with app.app_context():
        question_objs = Questions.query.filter_by(test_id=quiz_id).all()
        difficulty_list = [obj.difficulty_level for obj in question_objs]

        question_marks_list = get_mark_distribution(difficulty_list, int(total_marks))

        for obj, new_marks in zip(question_objs, question_marks_list):
            obj.marks = new_marks

        db.session.commit()


def validate_options_list(options):
    if not isinstance(options, list):
        raise ValueError("Options must be a list.")

    for idx, item in enumerate(options):
        if not isinstance(item, dict):
            raise ValueError(f"options[{idx}] must be an object")
        if set(item.keys()) != {"id", "text"}:
            raise ValueError(f"options[{idx}] must have exactly 'id' and 'text'")
        if not all(isinstance(item[k], str) for k in item):
            raise ValueError(f"options[{idx}] values must be strings")

    return options
