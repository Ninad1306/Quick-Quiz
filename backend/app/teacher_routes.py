from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Courses, Teacher_Courses_Map, Tests, Questions
from functools import wraps
from app.utils import get_current_semester_and_year
from app.quizgen import generate_quiz
import json

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

def teacher_required(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.role != 'teacher':
            return jsonify({'error': 'Only teachers are allowed to register courses'}), 403
        
        kwargs['user'] = user
        return func(*args, **kwargs)
    
    return wrapper

@teacher_bp.route('/register_course', methods=['POST'])
@teacher_required
def register_course(user):
    data = request.get_json()
    course_id = data.get('course_id', None)
    course_name = data.get('course_name', None)
    course_level = data.get('course_level', None)
    course_objectives = data.get('course_objectives', '')
    offered_at = data.get('offered_at', None)
    
    course = Courses.query.filter_by(course_id=course_id).first()
    
    if not course:
        
        try:
            course_object = Courses(course_id=course_id, course_name=course_name, course_level=course_level, course_objectives=course_objectives)
            tc_map_object = Teacher_Courses_Map(teacher_id=user.id, course_id=course_id, offered_at=offered_at)

            db.session.add(course_object)
            db.session.add(tc_map_object)
            db.session.commit()
            
            return jsonify({'message': 'Course registered'}), 201
        
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Could not register course. Exception: {str(e)}"}), 500
    else:
        
        tc_map = Teacher_Courses_Map.query.filter_by(course_id=course_id, offered_at=offered_at).first()
        
        if tc_map:
            return jsonify({'error': 'Course is already offered by a different teacher'}), 400
        
        else:
            try:
                tc_map_object = Teacher_Courses_Map(teacher_id=user.id, course_id=course_id, offered_at=offered_at)
                db.session.add(tc_map_object)
                db.session.commit()

                return jsonify({'message': 'Course registered'}), 201
            
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": f"Could not register course. Exception: {str(e)}"}), 500

@teacher_bp.route('/list_courses', methods=['GET'])
@teacher_required
def list_courses(user):
    status = request.args.get('status', 'all')
    current_semester, current_year = get_current_semester_and_year()

    if status == 'all':
        offered_courses = Courses.query.join(Teacher_Courses_Map).filter(
            Teacher_Courses_Map.teacher_id == user.id
        ).all()

    elif status == 'active':
        offered_courses = Courses.query.join(Teacher_Courses_Map).filter(
            Teacher_Courses_Map.teacher_id == user.id,
            ( (Teacher_Courses_Map.offered_at == current_semester) | (Teacher_Courses_Map.offered_at == current_year) )
        ).all()
    
    else:
        offered_courses = Courses.query.join(Teacher_Courses_Map).filter(
            Teacher_Courses_Map.teacher_id == user.id,
            ~( (Teacher_Courses_Map.offered_at == current_semester) | (Teacher_Courses_Map.offered_at == current_year) )
        ).all()
    
    courses_list = []
    for course in offered_courses:
        offered_at = [tc.offered_at for tc in course.teacher_courses_maps]
        
        if status == 'active':
            offered_at = [tc.offered_at for tc in course.teacher_courses_maps if 
                          (tc.offered_at == current_semester or tc.offered_at == current_year)]

        elif status == 'past':
            offered_at = [tc.offered_at for tc in course.teacher_courses_maps if
                          (tc.offered_at != current_semester and tc.offered_at != current_year)]

        if offered_at:
            courses_list.append({
                "course_id": course.course_id,
                "course_name": course.course_name,
                "course_level": course.course_level,
                "course_objectives": course.course_objectives,
                "offered_at": offered_at
            })

    return jsonify(courses_list), 200

@teacher_bp.route('/create_quiz', methods=['POST'])
@teacher_required
def create_quiz(user):

    data = request.get_json()
    course_id = data.get('course_id', None)
    title = data.get('title', None)
    description = data.get('description', None)
    difficulty_level = data.get('difficulty_level', None)
    duration = data.get('duration', None)
    total_questions = data.get('total_questions', None)
    total_marks = data.get('total_marks', 100)
    passing_marks = data.get('passing_marks', 40)

    try:
        my_courses = {tc_map.course_id for tc_map in Teacher_Courses_Map.query.filter_by(teacher_id=user.id).all()}
        if course_id not in my_courses:
            raise ValueError(f"Course {course_id} not found for current user.")

        test_obj = Tests(course_id=course_id, title=title, description=description, difficulty_level=difficulty_level, duration_minutes=duration, total_questions=total_questions, total_marks=total_marks, passing_marks=passing_marks, created_by=user.id, status="NotPublished")
        db.session.add(test_obj)
        db.session.flush()

        test_object = Tests.query.filter_by(course_id=course_id, title=title).first()
        course_obj = Courses.query.filter_by(course_id=course_id).first()

        result = generate_quiz(course_obj.course_name, course_obj.course_level, course_obj.course_objectives, title, description, difficulty_level, total_questions, total_marks)
        question_objects = []
  
        for item in result:

            options = json.dumps(item['options'])
            tags = json.dumps(item['tags'])
            correct_answer = json.dumps(item['correct_answer'])

            obj = Questions(
                test_id=test_object.test_id, 
                question_text=item['question_text'],
                options=options,
                correct_answer=correct_answer,
                tags=tags,
                marks=item['marks'],
                difficulty_level=item['difficulty_level'],
                question_type=item['question_type']
            )
            question_objects.append(obj)
        
        db.session.add_all(question_objects)
        db.session.commit()

        return jsonify({'message': f'Test {title} created successfully.'}), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Could not create quiz. Exception: {str(e)}"}), 500

@teacher_bp.route('/list_quiz', methods=['GET'])
@teacher_required
def list_quiz(user):

    tests_obj = Tests.query.filter_by(created_by=user.id).order_by(Tests.created_at.desc()).all()
    return jsonify([test.to_dict() for test in tests_obj]), 200

@teacher_bp.route('/list_questions/<quiz_id>', methods=['GET'])
@teacher_required
def list_questions(user, quiz_id):

    test_obj = Tests.query.filter_by(created_by=user.id, test_id=quiz_id).first()
    if not test_obj:
        return jsonify({'error': f"Quiz with ID: {quiz_id} not found for current user."})
    
    questions_obj = Questions.query.filter_by(test_id=quiz_id).all()
    return jsonify([question.to_dict() for question in questions_obj]), 200