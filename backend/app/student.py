from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Courses, Student_Courses_Map


student_bp = Blueprint('student', __name__, url_prefix='/student')


@student_bp.route('/enroll', methods=['POST'])
@jwt_required()
def enroll_course():
	"""Enroll the current (JWT) user into a course.

	Expected JSON body: {"course_id": <id>}.
	Only users with role 'student' may enroll.
	"""
	data = request.get_json()
	
	course_id = data.get('course_id')

	if course_id is None:
		return jsonify({"error": "Missing 'course_id' in request body"}), 400

	# Identify current user
	current_email = get_jwt_identity()
	user = User.query.filter_by(email=current_email).first()
	if not user:
		return jsonify({"error": "User not found"}), 404

	if user.role != 'student':
		return jsonify({"error": "Only students can enroll in courses"}), 403

	# Try to find the course
	course = Courses.query.filter_by(course_id=course_id).first()
	if not course:
		return jsonify({"error": "Course not found"}), 404

	# Check if already enrolled
	existing = Student_Courses_Map.query.filter_by(student_id=user.id, course_id=course_id).first()
	if existing:
		return jsonify({"message": "Already enrolled in this course"}), 200

	# Enroll
	try:
		enroll = Student_Courses_Map(student_id=user.id, course_id=course_id)
		db.session.add(enroll)
		db.session.commit()
		return jsonify({"message": "Enrollment successful", "student_id": user.id, "course_id": course_id}), 201

	except Exception as e:
		db.session.rollback()
		return jsonify({"error": f"Could not enroll student. Exception: {str(e)}"}), 500


@student_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_enrolled_courses():
	"""Return all courses the current student is enrolled in."""
	current_email = get_jwt_identity()
	user = User.query.filter_by(email=current_email).first()
	if not user:
		return jsonify({"error": "User not found"}), 404

	if user.role != 'student':
		return jsonify({"error": "Only students have enrolled courses"}), 403

	enrolled_maps = Student_Courses_Map.query.filter_by(student_id=user.id).all()

	courses = []
	for em in enrolled_maps:
		course = Courses.query.filter_by(course_id=em.course_id).first()
		if course:
			courses.append({
				"course_id": course.course_id,
				"course_name": course.course_name,
				"taken_at": em.taken_at.isoformat() if getattr(em, 'taken_at', None) else None
			})

	return jsonify({"enrolled_courses": courses}), 200


@student_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_courses():
	"""Return all courses the current student is NOT enrolled in."""
	current_email = get_jwt_identity()
	user = User.query.filter_by(email=current_email).first()
	if not user:
		return jsonify({"error": "User not found"}), 404

	if user.role != 'student':
		return jsonify({"error": "Only students can view available courses"}), 403

	enrolled_maps = Student_Courses_Map.query.filter_by(student_id=user.id).all()
	enrolled_ids = [em.course_id for em in enrolled_maps]

	if enrolled_ids:
		available = Courses.query.filter(~Courses.course_id.in_(enrolled_ids)).all()
	else:
		available = Courses.query.all()

	courses = [{"course_id": c.course_id, "course_name": c.course_name} for c in available]

	return jsonify({"available_courses": courses}), 200



