from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from app import app
db.init_app(app)
from models.models import User, Subject, Chapter, Quiz, Question, Scores