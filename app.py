from flask import Flask



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz_master.sqlite3"

from models import models

from controllers import routes

if __name__ == '__main__':
    app.run(debug=True)

