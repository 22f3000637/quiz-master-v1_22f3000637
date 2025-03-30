from . import db, generate_password_hash, check_password_hash


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  email = db.Column(db.String(50), unique=True, nullable=False)
  hashed_password = db.Column(db.String(), nullable=False)
  fullname = db.Column(db.String(50), nullable=False)
  dob = db.Column(db.Date(), nullable = False)
  qualification = db.Column(db.String(50), nullable=False)
  is_admin = db.Column(db.Boolean, default=False)
  scores = db.relationship('Scores', backref='user', cascade="all, delete-orphan")


  def hashing_password(password):
    hash_password = generate_password_hash(password)
    return hash_password

  def check_password(self, plain_password):
    return check_password_hash(self.hashed_password, plain_password)

class Subject(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  name = db.Column(db.String(50), unique=True, nullable=False)
  description = db.Column(db.String(120), nullable=False)
  chapters = db.relationship('Chapter', backref='subject', cascade="all, delete-orphan")
  

class Chapter(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  name = db.Column(db.String(50), unique=True, nullable=False)
  description = db.Column(db.String(120), nullable=False)
  subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
  questions = db.relationship('Question', backref='chapter', cascade="all, delete-orphan")
  quizes = db.relationship('Quiz', backref='chapter', cascade = "all, delete-orphan")
  

class Quiz(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable= False)
  chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
  date_of_quiz = db.Column(db.Date(), nullable=False)
  time_duration = db.Column(db.Integer(), nullable=False)
  scores = db.relationship('Scores', backref='quiz', cascade="all, delete-orphan")
  questions = db.relationship('Question', backref = 'quiz', cascade = "all, delete-orphan")
  

class Question(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  question_title = db.Column(db.String(255), nullable=False)
  question = db.Column(db.String(120), nullable=False)
  option_1 = db.Column(db.String(120), nullable=False)
  option_2 = db.Column(db.String(120), nullable=False)
  option_3 = db.Column(db.String(120), nullable=False)
  option_4 = db.Column(db.String(120), nullable=False)
  correct_answer = db.Column(db.String(120), nullable=False)
  marks = db.Column(db.Integer(), nullable = False)
  chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete='CASCADE'), nullable = False)
  quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable = False)
  attempts = db.relationship('Userattempt', backref='question', cascade="all, delete-orphan", lazy=True) 
  

class Scores(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
  quiz_id = db.Column(db.Integer(), db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
  time_stamp_of_attempt = db.Column(db.DateTime(), nullable=False)
  total_scored = db.Column(db.Integer, nullable=False, default =0)
  
class Userattempt(db.Model):
  id = db.Column(db.Integer, primary_key=True, nullable=False)
  user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
  quiz_id = db.Column(db.Integer(), db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
  question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable = False)
  user_answer = db.Column(db.String())


