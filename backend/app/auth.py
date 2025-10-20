from flask import Blueprint, jsonify, request
from app import bcrypt, db
from app.models import User
import re

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
        return jsonify({"error": "missing required fields"}), 400
    
    if not validate_email(email_id):
        return jsonify({"error": "invalid email"}), 400
    
    if not validate_password(password):
        return jsonify({"error": "password must have 8-16 characters, with at least 1 of special character, number and capital letter"}), 400
    
    if not validate_role(role):
        return jsonify({"error": "role can only be one of teacher, student or admin"}), 400
    
    if role == 'admin' and not user_granted_admin(email_id):
        return jsonify({"error": "this user is not allowed to be an admin"}), 400
    
    hashed_password = bcrypt.generate_password_hash(password).decode('UTF-8')

    new_user = User(email=email_id, name=name, role=role, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "user registered successfully"}), 201
    
    except Exception as e:
        db.session().rollback()
        return jsonify({"error": f"could not register user. exception: {str(e)}"})