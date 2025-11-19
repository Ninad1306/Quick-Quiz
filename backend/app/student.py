from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Courses, Student_Courses_Map, Tests, Student_Test_Question_Attempt, Student_Test_Attempt, Questions
from datetime import datetime, timedelta
import json


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

	return jsonify(courses), 200


@student_bp.route('/list_quizzes', methods=['GET'])
@jwt_required()
def list_quizzes_for_student():
	"""List quizzes for the authenticated student with state.

	States: 'not_published', 'published', 'active', 'completed'
	- not_published: test.published_at is None
	- published: published_at is set but not currently active and not completed
	- active: published_at set and current time falls between published_at and published_at + duration_minutes
	- completed: the student has attempts recorded for this test

	Returns a JSON list of quizzes (for courses the student is enrolled in) with computed state and can_attempt flag.
	"""
	current_email = get_jwt_identity()
	user = User.query.filter_by(email=current_email).first()
	if not user:
		return jsonify({"error": "User not found"}), 404

	if user.role != 'student':
		return jsonify({"error": "Only students can view quizzes"}), 403

	enrolled_maps = Student_Courses_Map.query.filter_by(student_id=user.id).all()
	enrolled_ids = [em.course_id for em in enrolled_maps]

	if not enrolled_ids:
		return jsonify([]), 200

	tests = Tests.query.filter(Tests.course_id.in_(enrolled_ids)).all()

	now = datetime.utcnow()
	result = []

	for t in tests:
		start_time = getattr(t, 'start_time', None)

		# completed if any per-test attempt marked completed exists for this student and test
		completed = Student_Test_Attempt.query.filter_by(test_id=t.test_id, student_id=user.id, status='completed').first() is not None

		# determine active: if status == 'active' OR start_time exists and now between start and (start + duration)
		active = False
		if t.status == 'active':
			active = True
		elif start_time is not None:
			try:
				start = start_time
				end = start + timedelta(minutes=(t.duration_minutes or 0))
				if start <= now <= end:
					active = True
			except Exception:
				active = False

		# determine state primarily from stored status, fallback to computed values
		if getattr(t, 'status', None) in (None, 'not_published'):
			state = 'not_published'
		elif completed:
			state = 'completed'
		elif active:
			state = 'active'
		else:
			# If status explicitly says published, use that; otherwise default to 'published'
			state = t.status if getattr(t, 'status', None) else 'published'

		can_attempt = (state == 'active') and (not completed)

		result.append({
			"test_id": t.test_id,
			"title": t.title,
			"description": t.description,
			"course_id": t.course_id,
			"difficulty_level": t.difficulty_level,
			"duration_minutes": t.duration_minutes,
			"total_marks": t.total_marks,
			"passing_marks": t.passing_marks,
			"created_at": t.created_at.isoformat() if getattr(t, 'created_at', None) else None,
			"start_time": t.start_time.isoformat() if getattr(t, 'start_time', None) else None,
			"state": state,
			"can_attempt": can_attempt
		})

	return jsonify(result), 200




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

	return jsonify(courses), 200


@student_bp.route('/list_questions/<int:test_id>', methods=['GET'])
@jwt_required()
def list_questions_for_quiz(quiz_id: int):
	"""Return questions for a quiz if the quiz is active and the student hasn't attempted it.

	- Only students enrolled in the course can list questions.
	- Quiz must be 'active' (published_at not None and current time within published_at + duration_minutes).
	- If the student has any attempts recorded for the quiz, questions are not returned.

	Response: list of questions without the `correct_options` field.
	"""
	current_email = get_jwt_identity()
	user = User.query.filter_by(email=current_email).first()
	if not user:
		return jsonify({"error": "User not found"}), 404

	if user.role != 'student':
		return jsonify({"error": "Only students can view quiz questions"}), 403

	test = Tests.query.filter_by(test_id=test_id).first()
	if not test:
		return jsonify({"error": "Quiz not found"}), 404

	# Verify student is enrolled in the course for this test
	enrolled = Student_Courses_Map.query.filter_by(student_id=user.id, course_id=test.course_id).first()
	if not enrolled:
		return jsonify({"error": "Student not enrolled in this course"}), 403

	# Determine if quiz is active
	# Use status and start_time to determine published/active
	if getattr(test, 'status', None) in (None, 'not_published'):
		return jsonify({"error": "Quiz is not published"}), 403

	now = datetime.utcnow()
	start_time = getattr(test, 'start_time', None)
	is_active = False
	if test.status == 'active':
		is_active = True
	elif start_time is not None:
		try:
			start = start_time
			end = start + timedelta(minutes=(test.duration_minutes or 0))
			if start <= now <= end:
				is_active = True
		except Exception:
			is_active = False

	if not is_active:
		return jsonify({"error": "Quiz is not active"}), 403

	# Ensure student has not attempted this quiz (any attempt record)
	attempted = Student_Test_Attempt.query.filter_by(test_id=quiz_id, student_id=user.id).first() is not None
	if attempted:
		return jsonify({"error": "Quiz already attempted by student"}), 403

	# Fetch questions (do NOT return correct_options)
	qs = Questions.query.filter_by(test_id=quiz_id).all()
	questions = []
	for q in qs:
		questions.append({
			"question_id": q.question_id,
			"question_text": q.question_text,
			"options": json.loads(q.options) if getattr(q, 'options', None) else None,
			"marks": q.marks
		})

	return jsonify({"quiz_id": quiz_id, "questions": questions}), 200


@student_bp.route('/start_attempt/<int:test_id>', methods=['POST'])
@jwt_required()
def start_attempt(test_id: int):
	"""Create a Student_Test_Attempt with status 'in_progress' for the authenticated student.

	If an in-progress attempt already exists, return it so the student can resume.
	"""
	current_email = get_jwt_identity()
	user = User.query.filter_by(email=current_email).first()
	if not user:
		return jsonify({"error": "User not found"}), 404

	if user.role != 'student':
		return jsonify({"error": "Only students can start attempts"}), 403

	test = Tests.query.filter_by(test_id=test_id).first()
	if not test:
		return jsonify({"error": "Test not found"}), 404

	# Verify student is enrolled
	enrolled = Student_Courses_Map.query.filter_by(student_id=user.id, course_id=test.course_id).first()
	if not enrolled:
		return jsonify({"error": "Student not enrolled in this course"}), 403

	# Check active
	now = datetime.utcnow()
	start_time = getattr(test, 'start_time', None)
	is_active = False
	if test.status == 'active':
		is_active = True
	elif start_time is not None:
		try:
			start = start_time
			end = start + timedelta(minutes=(test.duration_minutes or 0))
			if start <= now <= end:
				is_active = True
		except Exception:
			is_active = False

	if not is_active:
		return jsonify({"error": "Test is not active"}), 403

	# If there's already an in_progress attempt, return it
	existing = Student_Test_Attempt.query.filter_by(test_id=test_id, student_id=user.id, status='in_progress').first()
	if existing:
		return jsonify({"attempt_id": existing.attempt_id, "started_at": existing.started_at.isoformat() if existing.started_at else None}), 200

	# Create new attempt
	try:
		attempt = Student_Test_Attempt(student_id=user.id, test_id=test_id, status='in_progress')
		db.session.add(attempt)
		db.session.commit()
		return jsonify({"attempt_id": attempt.attempt_id, "started_at": attempt.started_at.isoformat() if attempt.started_at else None}), 201
	except Exception as e:
		db.session.rollback()
		return jsonify({"error": f"Could not start attempt: {str(e)}"}), 500


@student_bp.route('/submit_attempt/<int:attempt_id>', methods=['POST'])
@jwt_required()
def submit_attempt(attempt_id: int):
	"""Submit answers for an attempt, create question-attempt rows, 
	compute score, and mark attempt completed.

	Expected JSON body: {"answers": [{"question_id": <id>, "selected_options": <str|list|int>} , ...]}
	"""
	current_email = get_jwt_identity()
	user = User.query.filter_by(email=current_email).first()
	if not user:
		return jsonify({"error": "User not found"}), 404

	if user.role != 'student':
		return jsonify({"error": "Only students can submit attempts"}), 403

	attempt = Student_Test_Attempt.query.filter_by(attempt_id=attempt_id, student_id=user.id).first()
	if not attempt:
		return jsonify({"error": "Attempt not found"}), 404

	if attempt.status != 'in_progress':
		return jsonify({"error": "Attempt is not in progress"}), 400

	data = request.get_json() or {}
	answers = data.get('answers', [])
	if not isinstance(answers, list):
		return jsonify({"error": "Invalid answers format"}), 400

	# Remove any existing question attempts for this attempt (in case of re-submit)
	try:
		Student_Test_Question_Attempt.query.filter_by(attempt_id=attempt_id).delete()
	except Exception:
		pass

	total_score = 0.0
	per_question = []

	for ans in answers:
		qid = ans.get('question_id')
		sel = ans.get('selected_options')
		if qid is None:
			continue

		q = Questions.query.filter_by(question_id=qid, test_id=attempt.test_id).first()
		if not q:
			continue

		# Normalize selected options
		sel_norm = sel
		if isinstance(sel_norm, (list, dict)):
			sel_serialized = json.dumps(sel_norm)
		else:
			# string or int
			sel_serialized = json.dumps(sel_norm)

		# Load correct answer from stored JSON
		try:
			correct = json.loads(q.correct_answer)
		except Exception:
			correct = q.correct_answer

		marks_awarded = 0.0
		# Scoring rules: exact match for MCQ/MSQ; numeric equality for NAT
		qtype = getattr(q, 'question_type', '').lower()
		try:
			if qtype == 'mcq':
				if isinstance(correct, str) and isinstance(sel_norm, str) and sel_norm == correct:
					marks_awarded = float(q.marks)
			elif qtype == 'msq':
				# treat both as lists of strings
				if isinstance(correct, list) and isinstance(sel_norm, list) and sorted(correct) == sorted(sel_norm):
					marks_awarded = float(q.marks)
			elif qtype == 'nat':
				# numeric comparison
				try:
					if round(float(correct), 3) == round(float(sel_norm),3):
						marks_awarded = float(q.marks)
				except Exception:
					marks_awarded = 0.0
		except Exception:
			marks_awarded = 0.0

		total_score += marks_awarded

		qt = Student_Test_Question_Attempt(attempt_id=attempt_id, question_id=qid, selected_options=sel_serialized, marks_obtained=marks_awarded)
		db.session.add(qt)
		per_question.append({"question_id": qid, "marks_obtained": marks_awarded})

	# finalize attempt
	try:
		attempt.score = total_score
		attempt.completed_at = datetime.utcnow()
		attempt.status = 'completed'
		db.session.commit()
		return jsonify({"attempt_id": attempt.attempt_id, "score": total_score, "per_question": per_question}), 200
	except Exception as e:
		db.session.rollback()
		return jsonify({"error": f"Could not submit attempt: {str(e)}"}), 500


@student_bp.route('/attempts/<int:test_id>', methods=['GET'])
@jwt_required()
def list_attempts_for_test(test_id: int):
	"""List all attempts by the authenticated student for a given test_id, 
	including per-question answers."""
	current_email = get_jwt_identity()
	user = User.query.filter_by(email=current_email).first()
	if not user:
		return jsonify({"error": "User not found"}), 404

	if user.role != 'student':
		return jsonify({"error": "Only students can view attempts"}), 403

	test = Tests.query.filter_by(test_id=test_id).first()
	if not test:
		return jsonify({"error": "Test not found"}), 404

	# Verify student is enrolled in the course for this test
	enrolled = Student_Courses_Map.query.filter_by(student_id=user.id, course_id=test.course_id).first()
	if not enrolled:
		return jsonify({"error": "Student not enrolled in this course"}), 403

	attempts = Student_Test_Attempt.query.filter_by(test_id=test_id, student_id=user.id).order_by(Student_Test_Attempt.started_at.desc()).all()

	out = []
	for a in attempts:
		a_dict = a.to_dict() if hasattr(a, 'to_dict') else {
			"attempt_id": a.attempt_id,
			"student_id": a.student_id,
			"test_id": a.test_id,
			"started_at": a.started_at.isoformat() if getattr(a, 'started_at', None) else None,
			"completed_at": a.completed_at.isoformat() if getattr(a, 'completed_at', None) else None,
			"score": a.score,
			"status": a.status
		}

		# attach per-question attempts
		q_rows = Student_Test_Question_Attempt.query.filter_by(attempt_id=a.attempt_id).all()
		q_list = []
		for q in q_rows:
			try:
				sel = json.loads(q.selected_options)
			except Exception:
				sel = q.selected_options
			q_list.append({
				"question_id": q.question_id,
				"selected_options": sel,
				"marks_obtained": q.marks_obtained,
				"attempted_at": q.attempted_at.isoformat() if getattr(q, 'attempted_at', None) else None
			})

		a_dict["questions"] = q_list
		out.append(a_dict)

	return jsonify({"attempts": out}), 200


@student_bp.route('/results', methods=['GET'])
@jwt_required()
def student_results():
	"""Return summarized results for each test the student has attempted.

	For each test the student attempted, return:
	  - test_id, title, course_id
	  - attempts_count: total attempts created
	  - completed_count: completed attempts
	  - best_score: highest completed score (or null)
	  - last_score, last_attempted_at: most recent completed attempt
	  - passed: boolean if best_score >= test.passing_marks (null if unknown)
	"""
	current_email = get_jwt_identity()
	user = User.query.filter_by(email=current_email).first()
	if not user:
		return jsonify({"error": "User not found"}), 404

	if user.role != 'student':
		return jsonify({"error": "Only students can view results"}), 403

	attempts = Student_Test_Attempt.query.filter_by(student_id=user.id).all()
	if not attempts:
		return jsonify({"results": []}), 200

	# Group by test_id
	grouped = {}
	for a in attempts:
		grouped.setdefault(a.test_id, []).append(a)

	results = []
	for tid, atts in grouped.items():
		test = Tests.query.filter_by(test_id=tid).first()

		attempts_count = len(atts)
		completed = [a for a in atts if a.status == 'completed']
		completed_count = len(completed)

		best_score = None
		last_score = None
		last_attempted_at = None
		if completed:
			scores = [a.score or 0 for a in completed]
			best_score = max(scores)
			last = max(completed, key=lambda x: x.completed_at or datetime.min)
			last_score = last.score
			last_attempted_at = last.completed_at.isoformat() if last.completed_at else None

		passed = None
		if test and best_score is not None and getattr(test, 'passing_marks', None) is not None:
			try:
				passed = float(best_score) >= float(test.passing_marks)
			except Exception:
				passed = None

		results.append({
			"test_id": tid,
			"title": test.title if test else None,
			"course_id": test.course_id if test else None,
			"attempts_count": attempts_count,
			"completed_count": completed_count,
			"best_score": best_score,
			"last_score": last_score,
			"last_attempted_at": last_attempted_at,
			"passed": passed
		})

	return jsonify({"results": results}), 200


@student_bp.route('/results/<int:test_id>', methods=['GET'])
@jwt_required()
def student_results_for_test(test_id: int):
	"""Return detailed results for a specific test the student has attempted.

	Response includes per-attempt metadata and per-question details. Correct answers
	are included only for completed attempts. Enrollment is enforced.
	"""
	current_email = get_jwt_identity()
	user = User.query.filter_by(email=current_email).first()
	if not user:
		return jsonify({"error": "User not found"}), 404

	if user.role != 'student':
		return jsonify({"error": "Only students can view results"}), 403

	test = Tests.query.filter_by(test_id=test_id).first()
	if not test:
		return jsonify({"error": "Test not found"}), 404

	# Verify enrollment
	enrolled = Student_Courses_Map.query.filter_by(student_id=user.id, course_id=test.course_id).first()
	if not enrolled:
		return jsonify({"error": "Student not enrolled in this course"}), 403

	attempts = Student_Test_Attempt.query.filter_by(test_id=test_id, student_id=user.id).order_by(Student_Test_Attempt.started_at.desc()).all()

	detailed = {
		"test_id": test.test_id,
		"title": test.title,
		"course_id": test.course_id,
		"duration_minutes": test.duration_minutes,
		"total_marks": test.total_marks,
		"passing_marks": test.passing_marks,
		"attempts": []
	}

	for a in attempts:
		attempt_obj = {
			"attempt_id": a.attempt_id,
			"status": a.status,
			"started_at": a.started_at.isoformat() if getattr(a, 'started_at', None) else None,
			"completed_at": a.completed_at.isoformat() if getattr(a, 'completed_at', None) else None,
			"score": a.score,
		}

		# compute percentage if possible
		try:
			attempt_obj["percentage"] = (float(a.score) / float(test.total_marks) * 100) if (a.score is not None and getattr(test, 'total_marks', None)) else None
		except Exception:
			attempt_obj["percentage"] = None

		attempt_obj["passed"] = None
		if attempt_obj.get("score") is not None and getattr(test, 'passing_marks', None) is not None:
			try:
				attempt_obj["passed"] = float(attempt_obj["score"]) >= float(test.passing_marks)
			except Exception:
				attempt_obj["passed"] = None

		# per-question rows
		q_rows = Student_Test_Question_Attempt.query.filter_by(attempt_id=a.attempt_id).all()
		q_list = []
		for q in q_rows:
			q_rec = {
				"question_id": q.question_id,
				"selected_options": None,
				"marks_obtained": q.marks_obtained,
				"attempted_at": q.attempted_at.isoformat() if getattr(q, 'attempted_at', None) else None
			}
			try:
				q_rec["selected_options"] = json.loads(q.selected_options)
			except Exception:
				q_rec["selected_options"] = q.selected_options

			# include question text and correct answer only for completed attempts
			q_model = Questions.query.filter_by(question_id=q.question_id).first()
			if q_model:
				q_rec["question_text"] = q_model.question_text
				if a.status == 'completed':
					try:
						q_rec["correct_answer"] = json.loads(q_model.correct_answer)
					except Exception:
						q_rec["correct_answer"] = q_model.correct_answer

			q_list.append(q_rec)

		attempt_obj["questions"] = q_list
		detailed["attempts"].append(attempt_obj)

	return jsonify(detailed), 200



