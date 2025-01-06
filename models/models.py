from models import db, app
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  email = db.Column(db.String(50), unique=True, nullable=False)
  hashed_password = db.Column(db.String(12), nullable=False)
  fullname = db.Column(db.String(50), nullable=False)
  dob = db.Column(db.Date(), nullable = False)
  qualification = db.Column(db.String(50), nullable=False)
  is_admin = db.Column(db.Boolean, default=False)

  def hashing_password(self, password):
    hash_password = generate_password_hash(password)
    return hash_password

  def check_password(self, password):
    return self.hashed_password == check_password_hash(self.hashed_password, password)

class Subject(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  name = db.Column(db.String(50), unique=True, nullable=False)
  description = db.Column(db.String(120), nullable=False)
  chapters = db.relationship('Chapter', backref='subject', lazy=True)
  

class Chapter(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  name = db.Column(db.String(50), unique=True, nullable=False)
  description = db.Column(db.String(120), nullable=False)
  subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
  questions = db.relationship('Question', backref='chapter', lazy=True)
  

class Quiz(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable= False)
  chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
  date_of_quiz = db.Column(db.Date(), nullable=False)
  time_duration = db.Column(db.Time(), nullable=False)
  remarks = db.Column(db.String(120), nullable=False)
  score = db.Column(db.Integer, nullable=False)

class Question(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  question = db.Column(db.String(120), nullable=False)
  option_1 = db.Column(db.String(120), nullable=False)
  option_2 = db.Column(db.String(120), nullable=False)
  option_3 = db.Column(db.String(120), nullable=False)
  option_4 = db.Column(db.String(120), nullable=False)
  quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
  chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable = False)
  correct_answer = db.Column(db.String(120), nullable=False)
  

class Scores(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
  time_stamp_of_attempt = db.Column(db.DateTime(), nullable=False)
  total_scored = db.Column(db.Integer, nullable=False)
  

with app.app_context():
  db.create_all()
  user = User.query.filter_by(email = ('Admin@gmail.com' or 'Quizmaster@gmail.com')).all()
  if not user:
    user1 = User(
      email='Admin@gmail.com',
      hashed_password = generate_password_hash('Admin'),
      dob = date(2001,11,16),
      fullname='Admin',
      qualification='Diploma',
      is_admin=True
    )
    user2 = User(
      email='QuizMaster@gmail.com',
      hashed_password = generate_password_hash('Quizmaster'),
      dob = date(2001,11,16),
      fullname='Quizmaster',
      qualification='Diploma',
      is_admin=True
    )
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()