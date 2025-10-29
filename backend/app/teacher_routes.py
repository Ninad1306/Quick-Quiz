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
    
    # print(type(user))
    return jsonify({"message": "Course Registered Successfully"}), 200