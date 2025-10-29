from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import bcrypt, db
from app.models import User
# , Teacher_Course_Map

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/register_course', methods=['POST'])
@jwt_required()
def register_course():

    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.role != 'teacher':
        return jsonify({'error': 'Only teachers are allowed to register courses'}), 403
    
    data = request.get_json()
    

    
    return jsonify({"message": "Course Registered Successfully"}), 200