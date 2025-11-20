from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import bcrypt, db
from app.models import User
import re
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email_id):
    pattern = r'[a-zA-Z0-9_]+([._-][a-zA-Z0-9]+)*@[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+'
    match = re.search(pattern, email_id)
    return True if match else False

def validate_password(password):
    if len(password) < 8 or len(password) > 16:
        return False
    
    if not any(c.isupper() for c in password):
        return False
    
    if not any(not c.isalnum() for c in password):
        return False
    
    if not any(c.isdigit() for c in password):
        return False
    
    return True

def validate_role(role):
    allowed_roles = ['admin', 'teacher', 'student']
    return True if role in allowed_roles else False

def user_granted_admin(email_id):
    allowed_admins = ['anuragborkar@cse.iitb.ac.in', 'aniketw@cse.iitb.ac.in', 'parikhninad@cse.iitb.ac.in']
    return True if email_id in allowed_admins else False

@auth_bp.route('/register', methods=['POST'])
def auth_register():
    data = request.get_json()

    email_id = data.get('email_id', None)
    name = data.get('name', None)
    password = data.get('password', None)
    role = data.get('role', None)

    if not email_id or not name or not password or not role:
        return jsonify({"error": "Missing Required Fields"}), 400
    
    if not validate_email(email_id):
        return jsonify({"error": "Invalid E-mail"}), 400
    
    if not validate_password(password):
        return jsonify({"error": "Password must have 8-16 characters, with at least 1 of special character, number and capital letter"}), 400
    
    if not validate_role(role):
        return jsonify({"error": "Role can only be one of teacher, student or admin"}), 400
    
    if role == 'admin' and not user_granted_admin(email_id):
        return jsonify({"error": "This user is not allowed to be an admin"}), 400
    
    user = User.query.filter_by(email=email_id).first()
    if user:
        return jsonify({"error": "User is already registered"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('UTF-8')

    new_user = User(email=email_id, name=name, role=role, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User Registered Successfully"}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Could not register user. Exception: {str(e)}"})
    
@auth_bp.route('/login', methods=['POST'])
def auth_login():
    data = request.get_json()
    
    email_id = data.get('email_id', None)
    password = data.get('password', None)
    
    if not email_id or not password:
        return jsonify({"error": "Missing Required Fields"}), 400
    
    user = User.query.filter_by(email=email_id).first()
    
    if not user:
        return jsonify({"error": "Invalid Credentials"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid Credentials"}), 401
    
    access_token = create_access_token(identity=email_id, additional_claims={"role": user.role, "name": user.name}, expires_delta=timedelta(days=2))
    
    return jsonify({
        "message": "login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }), 200

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    current_user = get_jwt_identity()
    return jsonify({"valid": True, "user": current_user}), 200