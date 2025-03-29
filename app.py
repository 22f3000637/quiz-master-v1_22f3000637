from flask import Flask
from datetime import date
from flask_cors import CORS


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz_master.sqlite3"
app.config["SECRET_KEY"] = '81c34f7f2dcef68de4bc0c365df13f9f'

from models import db, User, generate_password_hash
from flask_restful import Api
db.init_app(app)
api = Api(app)
CORS(app)

with app.app_context():
  from controllers import routes, api

  db.create_all()
  user = User.query.filter_by(is_admin = True).all()
  if not user:
    user1 = User(
      email='admin@gmail.com',
      hashed_password = generate_password_hash('Admin'),
      dob = date(2001,11,16),
      fullname='Admin',
      qualification='Diploma',
      is_admin=True
    )
    user2 = User(
      email='quizmaster@gmail.com',
      hashed_password = generate_password_hash('Quizmaster'),
      dob = date(2001,11,16),
      fullname='Quizmaster',
      qualification='Diploma',
      is_admin=True
    )
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()



if __name__ == '__main__':
    app.run(debug=True)

