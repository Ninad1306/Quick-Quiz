from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, String, DateTime
from sqlalchemy import sql
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(64), nullable=False)
    email = mapped_column(String(64), unique=True, nullable=False)
    role = mapped_column(String(64), nullable=False)
    password = mapped_column(String(128), nullable=False)
    creation_time = mapped_column(DateTime, default=sql.func.now(), nullable=False)

    def __repr__(self):
        return f'<User {self.id}>'
