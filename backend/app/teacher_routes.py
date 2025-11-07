from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Courses, Teacher_Courses_Map
from functools import wraps
from app.utils import get_current_semester_and_year

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