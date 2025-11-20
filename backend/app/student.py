from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    db, User, Courses, Student_Courses_Map, Tests, Questions,
    StudentTestAttempt, StudentQuestionAttempt
)
from datetime import datetime, timedelta
import json
import pytz

student_bp = Blueprint('student', __name__, url_prefix='/student')


def get_current_student():
    """Helper to get current authenticated student"""
    current_email = get_jwt_identity()
    user = User.query.filter_by(email=current_email).first()
    
    if not user:
        return None, jsonify({"error": "User not found"}), 404
    
    if user.role != 'student':
        return None, jsonify({"error": "Only students can access this resource"}), 403
    
    return user, None, None


def is_test_active(test):
    """Check if a test is currently active"""
    if test.status == 'active':
        return True
    
    if not test.start_time:
        return False
    
    now = datetime.now(pytz.UTC)
    start_time = test.start_time
    
    # Make start_time timezone aware if it isn't
    if start_time.tzinfo is None:
        start_time = pytz.UTC.localize(start_time)
    
    end_time = start_time + timedelta(minutes=test.duration_minutes)
    
    return start_time <= now <= end_time


# ==================== COURSE ENROLLMENT ====================

@student_bp.route('/unenroll', methods=['DELETE'])
@jwt_required()
def unenroll_course():
    """Unenroll student from a course"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code

    data = request.get_json()
    course_id = data.get('course_id')

    if not course_id:
        return jsonify({"error": "Missing course_id"}), 400

    # Check if enrollment exists
    enrollment = Student_Courses_Map.query.filter_by(
        student_id=user.id,
        course_id=course_id
    ).first()

    if not enrollment:
        return jsonify({"error": "Not enrolled in this course"}), 404

    try:
        db.session.delete(enrollment)
        db.session.commit()
        return jsonify({
            "message": "Unenrolled successfully",
            "student_id": user.id,
            "course_id": course_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unenrollment failed: {str(e)}"}), 500

@student_bp.route('/enroll', methods=['POST'])
@jwt_required()
def enroll_course():
    """Enroll student in a course"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    data = request.get_json()
    course_id = data.get('course_id')
    
    if not course_id:
        return jsonify({"error": "Missing course_id"}), 400
    
    # Check if course exists
    course = Courses.query.filter_by(course_id=course_id).first()
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    # Check if already enrolled
    existing = Student_Courses_Map.query.filter_by(
        student_id=user.id, 
        course_id=course_id
    ).first()
    
    if existing:
        return jsonify({"message": "Already enrolled in this course"}), 200
    
    try:
        enrollment = Student_Courses_Map(student_id=user.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            "message": "Enrollment successful",
            "student_id": user.id,
            "course_id": course_id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Enrollment failed: {str(e)}"}), 500


@student_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_enrolled_courses():
    """Get all courses student is enrolled in"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    enrollments = Student_Courses_Map.query.filter_by(student_id=user.id).all()
    
    courses = []
    for enrollment in enrollments:
        course = Courses.query.filter_by(course_id=enrollment.course_id).first()
        if course:
            courses.append({
                "course_id": course.course_id,
                "course_name": course.course_name,
                "course_level": course.course_level,
                "enrolled_at": enrollment.taken_at.isoformat() if enrollment.taken_at else None
            })
    
    return jsonify(courses), 200


@student_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_courses():
    """Get courses student is NOT enrolled in"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    enrolled_ids = [
        em.course_id 
        for em in Student_Courses_Map.query.filter_by(student_id=user.id).all()
    ]
    
    if enrolled_ids:
        available = Courses.query.filter(~Courses.course_id.in_(enrolled_ids)).all()
    else:
        available = Courses.query.all()
    
    courses = [
        {
            "course_id": c.course_id,
            "course_name": c.course_name,
            "course_level": c.course_level
        }
        for c in available
    ]
    
    return jsonify(courses), 200


# ==================== QUIZ LISTING ====================

@student_bp.route('/list_quizzes/<course_id>', methods=['GET'])
@jwt_required()
def list_quizzes_for_student(course_id):
    """List all quizzes for a course with attempt status"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    # Verify enrollment
    enrolled = Student_Courses_Map.query.filter_by(
        student_id=user.id,
        course_id=course_id
    ).first()
    
    if not enrolled:
        return jsonify({"error": "Not enrolled in this course"}), 403
    
    # Get all published/active tests for this course
    tests = Tests.query.filter(
        Tests.course_id == course_id,
        Tests.status.in_(['published', 'active', 'completed'])
    ).order_by(Tests.created_at.desc()).all()
    
    result = []
    for test in tests:
        # Check if student has submitted attempts
        submitted_attempt = StudentTestAttempt.query.filter_by(
            test_id=test.test_id,
            student_id=user.id,
            status='submitted'
        ).first()
        
        # Check if student has in-progress attempt
        in_progress_attempt = StudentTestAttempt.query.filter_by(
            test_id=test.test_id,
            student_id=user.id,
            status='in_progress'
        ).first()
        
        # Determine state
        is_active = is_test_active(test)
        has_submitted = submitted_attempt is not None
        
        if has_submitted:
            state = 'completed'
            can_attempt = False
        elif is_active:
            state = 'active'
            can_attempt = True
        elif test.status == 'completed':
            state = 'completed'
            can_attempt = False
        else:
            state = 'published'
            can_attempt = False
        
        result.append({
            "test_id": test.test_id,
            "title": test.title,
            "description": test.description,
            "course_id": test.course_id,
            "difficulty_level": test.difficulty_level,
            "duration_minutes": test.duration_minutes,
            "total_marks": test.total_marks,
            "passing_marks": test.passing_marks,
            "total_questions": test.total_questions,
            "created_at": test.created_at.isoformat() if test.created_at else None,
            "start_time": test.start_time.isoformat() if test.start_time else None,
            "state": state,
            "can_attempt": can_attempt,
            "has_in_progress": in_progress_attempt is not None,
            "attempt_id": in_progress_attempt.attempt_id if in_progress_attempt else None
        })
    
    return jsonify(result), 200


# ==================== QUIZ ATTEMPT FLOW ====================

@student_bp.route('/start_attempt/<int:test_id>', methods=['POST'])
@jwt_required()
def start_attempt(test_id):
    """Start a new test attempt or resume existing in-progress attempt"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    # Get test
    test = Tests.query.filter_by(test_id=test_id).first()
    if not test:
        return jsonify({"error": "Test not found"}), 404
    
    # Verify enrollment
    enrolled = Student_Courses_Map.query.filter_by(
        student_id=user.id,
        course_id=test.course_id
    ).first()
    
    if not enrolled:
        return jsonify({"error": "Not enrolled in this course"}), 403
    
    # Check if test is active
    if not is_test_active(test):
        return jsonify({"error": "Test is not currently active"}), 403
    
    # Check for existing submitted attempt
    submitted_attempt = StudentTestAttempt.query.filter_by(
        test_id=test_id,
        student_id=user.id,
        status='submitted'
    ).first()
    
    if submitted_attempt:
        return jsonify({"error": "Test already submitted"}), 403
    
    # Check for in-progress attempt
    existing_attempt = StudentTestAttempt.query.filter_by(
        test_id=test_id,
        student_id=user.id,
        status='in_progress'
    ).first()
    
    if existing_attempt:
        return jsonify({
            "message": "Resuming existing attempt",
            "attempt_id": existing_attempt.attempt_id,
            "started_at": existing_attempt.started_at.isoformat(),
            "test_duration_minutes": test.duration_minutes
        }), 200
    
    # Create new attempt
    try:
        attempt = StudentTestAttempt(
            student_id=user.id,
            test_id=test_id,
            status='in_progress',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:255]
        )
        
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            "message": "Attempt started successfully",
            "attempt_id": attempt.attempt_id,
            "started_at": attempt.started_at.isoformat(),
            "test_duration_minutes": test.duration_minutes
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to start attempt: {str(e)}"}), 500


@student_bp.route('/list_questions/<int:test_id>', methods=['GET'])
@jwt_required()
def list_questions_for_quiz(test_id):
    """Get questions for a test (without correct answers)"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    # Get test
    test = Tests.query.filter_by(test_id=test_id).first()
    if not test:
        return jsonify({"error": "Test not found"}), 404
    
    # Verify enrollment
    enrolled = Student_Courses_Map.query.filter_by(
        student_id=user.id,
        course_id=test.course_id
    ).first()
    
    if not enrolled:
        return jsonify({"error": "Not enrolled in this course"}), 403
    
    # Check if test is active
    if not is_test_active(test):
        return jsonify({"error": "Test is not currently active"}), 403
    
    # Check for in-progress attempt
    attempt = StudentTestAttempt.query.filter_by(
        test_id=test_id,
        student_id=user.id,
        status='in_progress'
    ).first()
    
    if not attempt:
        return jsonify({"error": "No active attempt found. Start an attempt first."}), 403
    
    # Get questions
    questions = Questions.query.filter_by(test_id=test_id).all()
    
    # Get previously saved answers for this attempt
    saved_answers = {
        qa.question_id: json.loads(qa.selected_answer) if qa.selected_answer else None
        for qa in StudentQuestionAttempt.query.filter_by(attempt_id=attempt.attempt_id).all()
    }
    
    questions_data = []
    for q in questions:
        q_dict = q.to_dict(include_answer=False)
        q_dict['saved_answer'] = saved_answers.get(q.question_id)
        questions_data.append(q_dict)
    
    return jsonify({
        "test_id": test_id,
        "attempt_id": attempt.attempt_id,
        "questions": questions_data,
        "started_at": attempt.started_at.isoformat(),
        "duration_minutes": test.duration_minutes
    }), 200


@student_bp.route('/save_answer/<int:attempt_id>', methods=['POST'])
@jwt_required()
def save_answer(attempt_id):
    """Save/update answer for a single question (autosave functionality)"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    # Get attempt
    attempt = StudentTestAttempt.query.filter_by(
        attempt_id=attempt_id,
        student_id=user.id,
        status='in_progress'
    ).first()
    
    if not attempt:
        return jsonify({"error": "Active attempt not found"}), 404
    
    # Verify test is still active
    if not is_test_active(attempt.test):
        return jsonify({"error": "Test time has expired"}), 403
    
    data = request.get_json()
    question_id = data.get('question_id')
    selected_answer = data.get('selected_answer')
    
    if question_id is None:
        return jsonify({"error": "question_id is required"}), 400
    
    # Verify question belongs to this test
    question = Questions.query.filter_by(
        question_id=question_id,
        test_id=attempt.test_id
    ).first()
    
    if not question:
        return jsonify({"error": "Question not found in this test"}), 404
    
    try:
        # Check if answer already exists
        question_attempt = StudentQuestionAttempt.query.filter_by(
            attempt_id=attempt_id,
            question_id=question_id
        ).first()
        
        if question_attempt:
            # Update existing answer
            old_answer = question_attempt.selected_answer
            question_attempt.selected_answer = json.dumps(selected_answer)
            question_attempt.answered_at = datetime.utcnow()
            
            if old_answer != question_attempt.selected_answer:
                question_attempt.answer_changed = True
                question_attempt.answer_change_count += 1
        else:
            # Create new answer
            question_attempt = StudentQuestionAttempt(
                attempt_id=attempt_id,
                question_id=question_id,
                selected_answer=json.dumps(selected_answer)
            )
            db.session.add(question_attempt)
        
        db.session.commit()
        
        return jsonify({
            "message": "Answer saved successfully",
            "question_id": question_id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save answer: {str(e)}"}), 500


@student_bp.route('/submit_attempt/<int:attempt_id>', methods=['POST'])
@jwt_required()
def submit_attempt(attempt_id):
    """Submit test attempt and calculate score"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    # Get attempt
    attempt = StudentTestAttempt.query.filter_by(
        attempt_id=attempt_id,
        student_id=user.id,
        status='in_progress'
    ).first()
    
    if not attempt:
        return jsonify({"error": "Active attempt not found"}), 404
    
    data = request.get_json() or {}
    answers = data.get('answers', [])
    
    try:
        # Process all answers
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            selected_answer = answer_data.get('selected_options')
            
            if question_id is None:
                continue
            
            # Verify question belongs to this test
            question = Questions.query.filter_by(
                question_id=question_id,
                test_id=attempt.test_id
            ).first()
            
            if not question:
                continue

            # Check if answer already exists
            question_attempt = StudentQuestionAttempt.query.filter_by(
                attempt_id=attempt_id,
                question_id=question_id
            ).first()
            
            if question_attempt:
                # Update existing
                old_answer = question_attempt.selected_answer
                question_attempt.selected_answer = json.dumps(selected_answer)
                question_attempt.answered_at = datetime.utcnow()
                
                if old_answer != question_attempt.selected_answer:
                    question_attempt.answer_changed = True
                    question_attempt.answer_change_count += 1
            else:
                # Create new
                question_attempt = StudentQuestionAttempt(
                    attempt_id=attempt_id,
                    question_id=question_id,
                    selected_answer=json.dumps(selected_answer)
                )
                db.session.add(question_attempt)
            question_attempt.question = question
            # Check answer and calculate marks
            question_attempt.check_answer()
        
        # Calculate time taken
        time_taken = (datetime.utcnow() - attempt.started_at).total_seconds()
        attempt.time_taken_seconds = int(time_taken)
        
        # Calculate total score
        attempt.calculate_score()
        
        # Mark as submitted
        attempt.status = 'submitted'
        attempt.submitted_at = datetime.utcnow()
        
        db.session.commit()
        
        
        return jsonify({
            "message": "Test submitted successfully",
            "attempt_id": attempt.attempt_id,
            "total_score": attempt.total_score,
            "percentage": attempt.percentage,
            "passed": attempt.passed,
            "time_taken_seconds": attempt.time_taken_seconds
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to submit attempt: {str(e)}"}), 500


# ==================== RESULTS & ANALYTICS ====================

@student_bp.route('/attempts/<int:test_id>', methods=['GET'])
@jwt_required()
def list_attempts_for_test(test_id):
    """List all attempts by student for a specific test"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    # Get test
    test = Tests.query.filter_by(test_id=test_id).first()
    if not test:
        return jsonify({"error": "Test not found"}), 404
    
    # Verify enrollment
    enrolled = Student_Courses_Map.query.filter_by(
        student_id=user.id,
        course_id=test.course_id
    ).first()
    
    if not enrolled:
        return jsonify({"error": "Not enrolled in this course"}), 403
    
    # Get all attempts
    attempts = StudentTestAttempt.query.filter_by(
        test_id=test_id,
        student_id=user.id
    ).order_by(StudentTestAttempt.started_at.desc()).all()
    
    attempts_data = []
    for attempt in attempts:
        attempt_dict = attempt.to_dict(include_questions=True)
        
        # Add question details for submitted attempts
        if attempt.status == 'submitted':
            for qa_dict in attempt_dict['questions']:
                question = Questions.query.get(qa_dict['question_id'])
                if question:
                    qa_dict['question_text'] = question.question_text
                    qa_dict['correct_answer'] = json.loads(question.correct_answer)
                    qa_dict['marks'] = question.marks
        
        attempts_data.append(attempt_dict)
    
    return jsonify({"attempts": attempts_data}), 200


@student_bp.route('/results', methods=['GET'])
@jwt_required()
def student_results():
    """Get summary of all test attempts by student"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    attempts = StudentTestAttempt.query.filter_by(student_id=user.id).all()
    
    if not attempts:
        return jsonify({"results": []}), 200
    
    # Group by test_id
    test_attempts = {}
    for attempt in attempts:
        if attempt.test_id not in test_attempts:
            test_attempts[attempt.test_id] = []
        test_attempts[attempt.test_id].append(attempt)
    
    results = []
    for test_id, atts in test_attempts.items():
        test = Tests.query.get(test_id)
        if not test:
            continue
        
        submitted_attempts = [a for a in atts if a.status == 'submitted']
        
        best_score = None
        best_percentage = None
        last_score = None
        last_attempted_at = None
        
        if submitted_attempts:
            best_attempt = max(submitted_attempts, key=lambda a: a.total_score or 0)
            best_score = best_attempt.total_score
            best_percentage = best_attempt.percentage
            
            last_attempt = max(submitted_attempts, key=lambda a: a.submitted_at or datetime.min)
            last_score = last_attempt.total_score
            last_attempted_at = last_attempt.submitted_at.isoformat() if last_attempt.submitted_at else None
        
        results.append({
            "test_id": test_id,
            "title": test.title,
            "course_id": test.course_id,
            "total_marks": test.total_marks,
            "passing_marks": test.passing_marks,
            "attempts_count": len(atts),
            "submitted_count": len(submitted_attempts),
            "best_score": best_score,
            "best_percentage": best_percentage,
            "last_score": last_score,
            "last_attempted_at": last_attempted_at,
            "passed": best_score >= test.passing_marks if best_score is not None else None
        })
    
    return jsonify({"results": results}), 200


@student_bp.route('/results/<int:test_id>', methods=['GET'])
@jwt_required()
def student_results_for_test(test_id):
    """Get detailed results for a specific test"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    # Get test
    test = Tests.query.filter_by(test_id=test_id).first()
    if not test:
        return jsonify({"error": "Test not found"}), 404
    
    # Verify enrollment
    enrolled = Student_Courses_Map.query.filter_by(
        student_id=user.id,
        course_id=test.course_id
    ).first()
    
    if not enrolled:
        return jsonify({"error": "Not enrolled in this course"}), 403
    
    # Get all attempts
    attempts = StudentTestAttempt.query.filter_by(
        test_id=test_id,
        student_id=user.id
    ).order_by(StudentTestAttempt.started_at.desc()).all()
    
    attempts_data = []
    for attempt in attempts:
        attempt_dict = {
            "attempt_id": attempt.attempt_id,
            "status": attempt.status,
            "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
            "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
            "total_score": attempt.total_score,
            "percentage": attempt.percentage,
            "passed": attempt.passed,
            "time_taken_seconds": attempt.time_taken_seconds,
            "questions": []
        }
        
        # Get question-level details
        question_attempts = StudentQuestionAttempt.query.filter_by(
            attempt_id=attempt.attempt_id
        ).all()
        
        for qa in question_attempts:
            question = Questions.query.get(qa.question_id)
            if not question:
                continue
            
            qa_dict = {
                "question_id": qa.question_id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "selected_answer": json.loads(qa.selected_answer) if qa.selected_answer else None,
                "is_correct": qa.is_correct,
                "marks_obtained": qa.marks_obtained,
                "max_marks": question.marks,
                "answered_at": qa.answered_at.isoformat() if qa.answered_at else None
            }
            
            # Include correct answer for submitted attempts
            if attempt.status == 'submitted':
                qa_dict["correct_answer"] = json.loads(question.correct_answer)
                qa_dict["options"] = json.loads(question.options) if question.options else None
            
            attempt_dict["questions"].append(qa_dict)
        
        attempts_data.append(attempt_dict)
    
    return jsonify({
        "test_id": test.test_id,
        "title": test.title,
        "course_id": test.course_id,
        "duration_minutes": test.duration_minutes,
        "total_marks": test.total_marks,
        "passing_marks": test.passing_marks,
        "attempts": attempts_data
    }), 200


@student_bp.route('/analytics/<int:test_id>', methods=['GET'])
@jwt_required()
def student_analytics(test_id):
    """Get detailed analytics for a test"""
    user, error_response, status_code = get_current_student()
    if error_response:
        return error_response, status_code
    
    # Get test
    test = Tests.query.filter_by(test_id=test_id).first()
    if not test:
        return jsonify({"error": "Test not found"}), 404
    
    # Get all submitted attempts
    attempts = StudentTestAttempt.query.filter_by(
        test_id=test_id,
        student_id=user.id,
        status='submitted'
    ).all()
    
    if not attempts:
        return jsonify({"message": "No submitted attempts found"}), 200
    
    # Aggregate analytics
    analytics = {
        "test_id": test_id,
        "total_attempts": len(attempts),
        "average_score": sum(a.total_score for a in attempts) / len(attempts),
        "best_score": max(a.total_score for a in attempts),
        "worst_score": min(a.total_score for a in attempts),
        "average_percentage": sum(a.percentage for a in attempts if a.percentage) / len(attempts),
        "pass_count": sum(1 for a in attempts if a.passed),
        "average_time_seconds": sum(a.time_taken_seconds for a in attempts if a.time_taken_seconds) / len(attempts),
        "topic_performance": {},
        "difficulty_performance": {}
    }
    
    # Topic-wise and difficulty-wise performance
    topic_stats = {}
    difficulty_stats = {'easy': [], 'medium': [], 'hard': []}
    
    for attempt in attempts:
        for qa in attempt.question_attempts:
            question = qa.question
            if not question:
                continue
            
            # Topic performance
            tags = json.loads(question.tags)
            for tag in tags:
                if tag not in topic_stats:
                    topic_stats[tag] = {'correct': 0, 'total': 0}
                topic_stats[tag]['total'] += 1
                if qa.is_correct:
                    topic_stats[tag]['correct'] += 1
            
            # Difficulty performance
            diff = question.difficulty_level.lower()
            if diff in difficulty_stats:
                difficulty_stats[diff].append(1 if qa.is_correct else 0)
    
    # Calculate percentages
    analytics['topic_performance'] = {
        tag: {
            'accuracy': (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0,
            'total_questions': stats['total']
        }
        for tag, stats in topic_stats.items()
    }
    
    analytics['difficulty_performance'] = {
        diff: {
            'accuracy': (sum(scores) / len(scores) * 100) if scores else 0,
            'total_questions': len(scores)
        }
        for diff, scores in difficulty_stats.items()
    }
    
    return jsonify(analytics), 200