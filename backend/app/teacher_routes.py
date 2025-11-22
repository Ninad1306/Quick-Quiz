from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, scheduler
from app.models import User, Courses, Teacher_Courses_Map, Tests, Questions, StudentTestAttempt, StudentQuestionAttempt
from functools import wraps
from app.utils import (
    get_current_semester_and_year,
    activate_test,
    deactivate_test,
    recalibrate_marks,
)
from app.quizgen import generate_quiz
import json, pytz, traceback
from datetime import datetime, timedelta, timezone
import numpy as np

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


def teacher_required(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.role != "teacher":
            return (
                jsonify({"error": "Only teachers are allowed to register courses"}),
                403,
            )

        kwargs["user"] = user
        return func(*args, **kwargs)

    return wrapper


@teacher_bp.route("/register_course", methods=["POST"])
@teacher_required
def register_course(user):
    data = request.get_json()
    course_id = data.get("course_id", None)
    course_name = data.get("course_name", None)
    course_level = data.get("course_level", None)
    course_objectives = data.get("course_objectives", "")
    offered_at = data.get("offered_at", None)

    course = Courses.query.filter_by(course_id=course_id).first()

    if not course:
        try:
            course_object = Courses(
                course_id=course_id,
                course_name=course_name,
                course_level=course_level,
                course_objectives=course_objectives,
            )
            tc_map_object = Teacher_Courses_Map(
                teacher_id=user.id, course_id=course_id, offered_at=offered_at
            )

            db.session.add(course_object)
            db.session.add(tc_map_object)
            db.session.commit()

            return jsonify({"message": "Course registered"}), 201

        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        except Exception as e:
            db.session.rollback()
            return (
                jsonify({"error": f"Could not register course. Exception: {str(e)}"}),
                500,
            )
    else:
        tc_map = Teacher_Courses_Map.query.filter_by(
            course_id=course_id, offered_at=offered_at
        ).first()

        if tc_map:
            return (
                jsonify({"error": "Course is already offered by a different teacher"}),
                400,
            )

        else:
            try:
                tc_map_object = Teacher_Courses_Map(
                    teacher_id=user.id, course_id=course_id, offered_at=offered_at
                )
                db.session.add(tc_map_object)
                db.session.commit()

                return jsonify({"message": "Course registered"}), 201

            except Exception as e:
                db.session.rollback()
                return (
                    jsonify(
                        {"error": f"Could not register course. Exception: {str(e)}"}
                    ),
                    500,
                )


@teacher_bp.route("/list_courses", methods=["GET"])
@teacher_required
def list_courses(user):
    status = request.args.get("status", "all")
    current_semester, current_year = get_current_semester_and_year()

    if status == "all":
        offered_courses = (
            Courses.query.join(Teacher_Courses_Map)
            .filter(Teacher_Courses_Map.teacher_id == user.id)
            .all()
        )

    elif status == "active":
        offered_courses = (
            Courses.query.join(Teacher_Courses_Map)
            .filter(
                Teacher_Courses_Map.teacher_id == user.id,
                (
                    (Teacher_Courses_Map.offered_at == current_semester)
                    | (Teacher_Courses_Map.offered_at == current_year)
                ),
            )
            .all()
        )

    else:
        offered_courses = (
            Courses.query.join(Teacher_Courses_Map)
            .filter(
                Teacher_Courses_Map.teacher_id == user.id,
                ~(
                    (Teacher_Courses_Map.offered_at == current_semester)
                    | (Teacher_Courses_Map.offered_at == current_year)
                ),
            )
            .all()
        )

    courses_list = []
    for course in offered_courses:
        offered_at = [tc.offered_at for tc in course.teacher_courses_maps]

        if status == "active":
            offered_at = [
                tc.offered_at
                for tc in course.teacher_courses_maps
                if (tc.offered_at == current_semester or tc.offered_at == current_year)
            ]

        elif status == "past":
            offered_at = [
                tc.offered_at
                for tc in course.teacher_courses_maps
                if (tc.offered_at != current_semester and tc.offered_at != current_year)
            ]

        if offered_at:
            courses_list.append(
                {
                    "course_id": course.course_id,
                    "course_name": course.course_name,
                    "course_level": course.course_level,
                    "course_objectives": course.course_objectives,
                    "offered_at": offered_at,
                }
            )

    return jsonify(courses_list), 200


@teacher_bp.route("/create_quiz", methods=["POST"])
@teacher_required
def create_quiz(user):
    data = request.get_json()
    course_id = data.get("course_id", None)
    title = data.get("title", None)
    description = data.get("description", None)
    difficulty_level = data.get("difficulty_level", None)
    duration_minutes = data.get("duration_minutes", None)
    total_questions = data.get("total_questions", None)
    total_marks = data.get("total_marks", 100)
    passing_marks = data.get("passing_marks", 40)

    try:
        if int(passing_marks) > int(total_marks):
            return jsonify({'error':'Passing marks cannot be greater than total marks.'}), 400
        if int(total_questions) < 0:
            return jsonify({'error':'Total questions cannot be negative.'}), 400
        if int(passing_marks) < 0 or int(total_marks) < 0:
            return jsonify({'error':'Passing/Total marks cannot be negative.'}), 400

        my_courses = {
            tc_map.course_id
            for tc_map in Teacher_Courses_Map.query.filter_by(teacher_id=user.id).all()
        }
        if course_id not in my_courses:
            raise ValueError(f"Course {course_id} not found for current user.")

        test_obj = Tests(
            course_id=course_id,
            title=title,
            description=description,
            difficulty_level=difficulty_level,
            duration_minutes=duration_minutes,
            total_questions=total_questions,
            total_marks=total_marks,
            passing_marks=passing_marks,
            created_by=user.id,
            status="not_published",
        )
        db.session.add(test_obj)
        db.session.flush()

        test_object = Tests.query.filter_by(course_id=course_id, title=title).first()
        course_obj = Courses.query.filter_by(course_id=course_id).first()

        result = generate_quiz(
            course_obj.course_name,
            course_obj.course_level,
            course_obj.course_objectives,
            title,
            description,
            difficulty_level,
            total_questions,
            total_marks,
        )
        question_objects = []

        for item in result:
            options = json.dumps(item["options"]) if "options" in item.keys() else ""
            tags = json.dumps(item["tags"])
            correct_answer = json.dumps(item["correct_answer"])
            obj = Questions(
                test_id=test_object.test_id,
                question_text=item["question_text"],
                question_type=item["question_type"],
                options=options,
                correct_answer=correct_answer,
                tags=tags,
                marks=item["marks"],
                difficulty_level=item["difficulty_level"],
            )
            question_objects.append(obj)

        db.session.add_all(question_objects)
        db.session.commit()

        return jsonify({"message": f"Test {title} created successfully."}), 201

    except ValueError as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": f"Could not create quiz. Exception: {str(e)}"}), 500


@teacher_bp.route("/list_quiz/<course_id>", methods=["GET"])
@teacher_required
def list_quiz(user, course_id):
    tests_obj = (
        Tests.query.filter_by(created_by=user.id, course_id=course_id)
        .order_by(Tests.created_at.desc())
        .all()
    )
    return jsonify([test.to_dict() for test in tests_obj]), 200


@teacher_bp.route("/list_questions/<quiz_id>", methods=["GET"])
@teacher_required
def list_questions(user, quiz_id):
    test_obj = Tests.query.filter_by(created_by=user.id, test_id=quiz_id).first()
    if not test_obj:
        return (
            jsonify({"error": f"Quiz with ID: {quiz_id} not found for current user."}),
            400,
        )

    questions_obj = Questions.query.filter_by(test_id=quiz_id).all()
    return jsonify([question.to_dict() for question in questions_obj]), 200


@teacher_bp.route("/publish_quiz/<quiz_id>", methods=["POST"])
@teacher_required
def publish_quiz(user, quiz_id):
    try:
        data = request.get_json()
        start_time_str = data["start_time"]
        start_time = datetime.fromisoformat(start_time_str)
        local_tz = pytz.timezone("Asia/Kolkata")
        start_time = local_tz.localize(start_time)
        now = datetime.now(local_tz)

        if start_time <= now:
            raise ValueError(f"Start time has already passed.")

        test_obj = (
            Tests.query.filter_by(created_by=user.id, test_id=quiz_id)
            .with_for_update()
            .first()
        )
        if not test_obj:
            return (
                jsonify(
                    {"error": f"Quiz with ID: {quiz_id} not found for current user."}
                ),
                400,
            )

        test_obj.status = "published"
        test_obj.start_time = start_time

        db.session.commit()

        duration = test_obj.duration_minutes
        end_time = start_time + timedelta(minutes=int(duration))

        scheduler.add_job(
            activate_test,
            "date",
            id=f"activate_test_{quiz_id}",
            run_date=start_time,
            args=[quiz_id],
            replace_existing=True,
        )
        scheduler.add_job(
            deactivate_test,
            "date",
            id=f"deactivate_test_{quiz_id}",
            run_date=end_time,
            args=[quiz_id],
            replace_existing=True,
        )

        return jsonify({"message": "Test published successfully."}), 200

    except Exception as e:
        return jsonify({"error": f"Exception occurred: {e}"}), 400


@teacher_bp.route("/modify_quiz_duration/<quiz_id>", methods=["POST"])
@teacher_required
def modify_quiz_duration(user, quiz_id):
    try:
        data = request.get_json()
        extra_time = data.get("extra_time", None)

        if extra_time is None:
            return jsonify({'error':"extra_time parameter needs to be set in request."}), 400

        test_obj = (
            Tests.query.filter_by(created_by=user.id, test_id=quiz_id)
            .with_for_update()
            .first()
        )
        if not test_obj:
            return (
                jsonify(
                    {"error": f"Quiz with ID: {quiz_id} not found for current user."}
                ),
                400,
            )
        if int(test_obj.duration_minutes) + extra_time <= 0:
            return jsonify({'error': "Test duration needs to be positive integer."}), 400

        test_obj.duration_minutes = int(test_obj.duration_minutes) + int(extra_time)

        db.session.commit()

        if not test_obj.start_time:
            return jsonify({"message": "Test duration modified successfully."}), 200

        start_time = test_obj.start_time
        end_time = start_time + timedelta(minutes=int(extra_time))

        scheduler.modify_job(f"deactivate_test_{quiz_id}", next_run_time=end_time)

        return jsonify({"message": "Test end time modified successfully."}), 200

    except Exception as e:
        return jsonify({"error": f"Exception occurred: {e}"}), 400


@teacher_bp.route("/delete_questions/<quiz_id>", methods=["POST"])
@teacher_required
def delete_questions(user, quiz_id):
    try:
        test_obj = Tests.query.filter_by(created_by=user.id, test_id=quiz_id).first()
        if not test_obj:
            return (
                jsonify(
                    {"error": f"Quiz with ID: {quiz_id} not found for current user."}
                ),
                400,
            )
        elif test_obj.status != 'not_published':
            return jsonify({'error': "Test can only be modified in not published state."}), 400

        data = request.get_json()
        question_ids = data["question_ids"]

        quest_objs = Questions.query.filter_by(test_id=quiz_id).all()
        test_question_ids = [obj.question_id for obj in quest_objs]

        if not set(question_ids).issubset(test_question_ids):
            return jsonify(
                {"error": "Some of the Question IDs not found for given test."}
            )
        
        question_objs = Questions.query.filter(Questions.question_id.in_(question_ids)).all()
        marks = [int(q.marks) for q in question_objs]
        test_obj.total_marks -= sum(marks)

        Questions.query.filter(Questions.question_id.in_(question_ids)).delete()
        
        db.session.commit()

        return jsonify({"message": "Deletion successful"}), 200

    except Exception as e:
        return jsonify({"error": f"Exception occurred: {e}"}), 400


@teacher_bp.route("/modify_quiz/<quiz_id>", methods=["POST"])
@teacher_required
def modify_quiz(user, quiz_id):
    try:
        test_obj = Tests.query.filter_by(created_by=user.id, test_id=quiz_id).first()
        if not test_obj:
            return (
                jsonify(
                    {"error": f"Quiz with ID: {quiz_id} not found for current user."}
                ),
                400,
            )
        elif test_obj.status != 'not_published':
            return jsonify({'error': "Test can only be modified in not published state."}), 400

        quiz_update_data = request.get_json()
        # quiz_update_data = data['quiz_obj']
        test_obj = Tests.query.get(quiz_id)

        old_num_questions = len(Questions.query.filter_by(test_id=quiz_id).all())
        delta_questions = int(quiz_update_data.get("total_questions", 0))
        new_num_questions = old_num_questions + delta_questions

        if new_num_questions < 0:
            return jsonify({'error':"Number of questions cannot be negative."}), 400

        new_total_marks = (
            quiz_update_data["total_marks"]
            if "total_marks" in quiz_update_data.keys()
            else test_obj.total_marks
        )

        if new_total_marks < 0:
            return jsonify({'error':"Total marks cannot be negative."}), 400

        if old_num_questions < new_num_questions:

            course_obj = Courses.query.filter_by(course_id=test_obj.course_id).first()

            question_objs = Questions.query.filter_by(test_id=quiz_id).all()
            old_questions = ".\n".join([q.question_text for q in question_objs])
            description = (
                test_obj.description
                + ". These are the old questions, do not repeat them: <questions_start>"
                + old_questions
                + "<questions_end>"
            )

            result = generate_quiz(
                course_obj.course_name,
                course_obj.course_level,
                course_obj.course_objectives,
                test_obj.title,
                description,
                test_obj.difficulty_level,
                new_num_questions - old_num_questions,
                new_total_marks,
            )
            question_objects = []

            for item in result:
                options = (
                    json.dumps(item["options"]) if "options" in item.keys() else ""
                )
                tags = json.dumps(item["tags"])
                correct_answer = (
                    item["correct_answer"]
                    if item["question_type"] == "nat"
                    else json.dumps(item["correct_answer"])
                )

                obj = Questions(
                    test_id=quiz_id,
                    question_text=item["question_text"],
                    question_type=item["question_type"],
                    options=options,
                    correct_answer=correct_answer,
                    tags=tags,
                    marks=item["marks"],
                    difficulty_level=item["difficulty_level"],
                )
                question_objects.append(obj)

            db.session.add_all(question_objects)

        if old_num_questions > new_num_questions:
            for q in Questions.query.filter_by(test_id=quiz_id).limit(
                old_num_questions - new_num_questions
            ):
                db.session.delete(q)

        db.session.commit()
        recalibrate_marks(quiz_id, new_total_marks)

        if "total_questions" in quiz_update_data:
            quiz_update_data["total_questions"] = new_num_questions

        for field in [
            "title",
            "description",
            "difficulty_level",
            "duration_minutes",
            "total_questions",
            "total_marks",
            "passing_marks",
        ]:
            if field in quiz_update_data:
                setattr(test_obj, field, quiz_update_data[field])

        db.session.commit()

        return jsonify({"message": "Modified quiz object successfully."}), 200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"Exception occurred: {e}"}), 400


@teacher_bp.route("/add_quiz_questions/<quiz_id>", methods=["POST"])
@teacher_required
def add_quiz_questions(user, quiz_id):
    try:
        test_obj = Tests.query.filter_by(created_by=user.id, test_id=quiz_id).first()
        if not test_obj:
            return (
                jsonify(
                    {"error": f"Quiz with ID: {quiz_id} not found for current user."}
                ),
                400,
            )
        elif test_obj.status != 'not_published':
            return jsonify({'error': "Test can only be modified in not published state."}), 400

        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({"error": "Payload should be list of question objects"}), 400

        questions = []
        marks_to_add = 0

        for item in data:
            obj = Questions(
                test_id=quiz_id,
                question_text=item.get("question_text", ""),
                question_type=item.get("question_type", None),
                options=item.get("options", None),
                correct_answer=item.get("correct_answer", None),
                tags=item.get("tags", None),
                marks=item.get("marks", None),
                difficulty_level=item.get("difficulty_level", None),
            )
            m = item.get("marks", 0)
            if m <= 0:
                return jsonify({'error':'Marks need to be positive'}), 400

            marks_to_add += m
            questions.append(obj)

        db.session.add_all(questions)

        test_obj.total_questions += len(questions)
        test_obj.total_marks += marks_to_add

        db.session.commit()

        return jsonify({"message": "Questions added successfully."}), 201

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"Exception occurred: {e}"}), 400


@teacher_bp.route("/delete_quiz/<quiz_id>", methods=["POST"])
@teacher_required
def delete_quiz(user, quiz_id):
    try:
        test_obj = Tests.query.filter_by(created_by=user.id, test_id=quiz_id).first()
        if not test_obj:
            return (
                jsonify(
                    {"error": f"Quiz with ID: {quiz_id} not found for current user."}
                ),
                400,
            )

        test = Tests.query.filter_by(test_id=quiz_id).first()
        db.session.delete(test)
        db.session.commit()

        return (
            jsonify({"message": "Test and associated questions have been deleted."}),
            200,
        )

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"Exception occurred: {e}"}), 400


@teacher_bp.route("/delete_course/<course_id>", methods=["POST"])
@teacher_required
def delete_course(user, course_id):
    try:
        obj = Teacher_Courses_Map.query.filter_by(
            teacher_id=user.id, course_id=course_id
        ).first()
        if not obj:
            return (
                jsonify(
                    {
                        "error": f"Course with ID: {course_id} not found for current user."
                    }
                ),
                400,
            )

        course = Courses.query.get(course_id)
        db.session.delete(course)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Course with ID {course_id} and its related data have been deleted."
                }
            ),
            200,
        )

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"Exception occurred: {e}"}), 400

@teacher_bp.route('/quiz_analytics/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_teacher_quiz_analytics(quiz_id):
    # ... Verify teacher access logic here ...
    
    test = Tests.query.get(quiz_id)
    
    # Check if quiz is finished (Teacher sees analytics only after end time)
    end_dt = test.start_time + timedelta(minutes=test.duration_minutes)
    # if datetime.now(test.start_time.tzinfo) < end_dt:
    #    return jsonify({"status": "pending"}), 200

    attempts = StudentTestAttempt.query.filter_by(test_id=quiz_id, status='submitted').all()
    
    if not attempts:
        return jsonify({"error": "No attempts yet"}), 400

    scores = [a.total_score for a in attempts]
    
    # 1. Statistical Metrics
    metrics = {
        "mean": round(float(np.mean(scores)), 2),
        "median": round(float(np.median(scores)), 2),
        "std_dev": round(float(np.std(scores)), 2),
        "min": float(np.min(scores)),
        "max": float(np.max(scores)),
        "count": len(scores)
    }

    # 2. Topic Ranking (Where did they lose marks?)
    # Get all question attempts for this quiz
    q_attempts = db.session.query(StudentQuestionAttempt, Questions)\
        .join(Questions)\
        .filter(Questions.test_id == quiz_id)\
        .filter(StudentQuestionAttempt.attempt_id.in_([a.attempt_id for a in attempts]))\
        .all()

    topic_loss = {} # {tag: [lost_marks, total_possible_marks]}
    
    for qa, q in q_attempts:
        marks_lost = q.marks - (qa.marks_obtained or 0)
        try:
            tags = json.loads(q.tags)
            for tag in tags:
                if tag not in topic_loss: topic_loss[tag] = 0
                topic_loss[tag] += marks_lost
        except: pass
        
    # Convert to list and sort by most marks lost
    topic_ranking = [{"topic": k, "marks_lost": round(v, 2)} for k, v in topic_loss.items()]
    topic_ranking.sort(key=lambda x: x['marks_lost'], reverse=True)

    return jsonify({
        "metrics": metrics,
        "topic_ranking": topic_ranking
    })