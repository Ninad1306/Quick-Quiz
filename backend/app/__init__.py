from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.models import db
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import text
import os

app = Flask(__name__)

app_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(app_dir)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f'sqlite:///{os.path.join(parent_dir, "users.db")}'
)
app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY", "default_key_sample_a5%@saw^97A"
)
app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY", "jwt_secret_key_sample_b8#@xzw^12B"
)


@app.before_request
def enable_foreign_keys():
    db.session.execute(text("PRAGMA foreign_keys = ON"))
    db.session.commit()


db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
cors = CORS(app)

scheduler = BackgroundScheduler()
scheduler.start()

from app.setup import setup_db

setup_db(app, db)

from app.auth_routes import auth_bp
from app.teacher_routes import teacher_bp
from app.student import student_bp

app.register_blueprint(auth_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)
