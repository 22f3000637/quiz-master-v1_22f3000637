from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from werkzeug.security import generate_password_hash, check_password_hash

from models.models import User, Subject, Chapter, Quiz, Question, Scores, Userattempt


