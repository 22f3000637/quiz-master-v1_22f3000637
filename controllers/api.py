from flask import make_response,json, jsonify
from flask_restful import Resource, marshal_with,request, fields
from werkzeug.exceptions import HTTPException
from models import User, Subject, Chapter
from app import api, db
from datetime import datetime





# === Exceptions ===

class CustomError(HTTPException):
    def __init__(self, status_code, error_msg):
        message = {"error_msg": error_msg}
        self.response = make_response(json.dumps(message),status_code) 

# === Api creation ===
class LoginApi(Resource):
    def post(self):
        email = request.json.get("email").lower()
        user_password = request.json.get("password")
        user = User.query.filter_by(email=email).first()
        if not email or not user_password:
            raise CustomError(status_code=400, error_msg="Both email and password needed")
        if not user:
            raise CustomError(status_code=404, error_msg="User not Found")
        if not user.check_password(plain_password=user_password):
            raise CustomError(status_code=401, error_msg="Incorrect Password")
        if user and user_password:
            return {"message":"Login Successfull"},200
            

        
class RegisterApi(Resource):
    def post(self):
        name = request.json.get('name')
        qualification = request.json.get('qualification')
        dob = request.json.get('dob')
        email = request.json.get('email').lower()
        password = request.json.get('password')
        user = User.query.filter_by(email=email).first()
        if not name or not qualification or not dob or not email or not password:
            raise CustomError(status_code=400, error_msg="Required fields: name, qualification, dob, email, password")
        if  user:
            raise CustomError(status_code=409, error_msg = "User already exists")
        password_hash = User.hashing_password(password=password)
        user = User(email=email,
                    hashed_password = password_hash,
                    fullname = name,
                    dob = datetime.strptime(dob, '%Y-%m-%d'),
                    qualification = qualification)
        db.session.add(user)
        db.session.commit()
        return {"message":"User created successfully"}, 201



subject_output = {
    "id" : fields.Integer,
    "name": fields.String,
    "description":fields.String
}
    
class SubjectApi(Resource):
    @marshal_with(subject_output)
    def get(self, subject_id = None):
        if subject_id == None:
            subjects = Subject.query.all()
            return subjects,200
        subject = Subject.query.filter_by(id = subject_id).first()
        if subject:
            return subject,200
        raise CustomError(status_code=404, error_msg="No subject found")
    
    def post(self):
        name = request.json.get("name")
        description = request.json.get("description")
        if not name or not description:
            raise CustomError(status_code=400, error_msg="Both name and description required")
        subject = Subject.query.filter_by(name = name).first()
        if subject:
            raise CustomError(status_code=409, error_msg="Subject alraedy exists")
        subject = Subject(name = name, description =description)
        db.session.add(subject)
        db.session.commit()
        return {"message": "Subject created successfully"}, 201

    @marshal_with(subject_output)
    def put(self, subject_id = None):
        if subject_id is None:
            raise CustomError(status_code=400, error_msg="Subject_id needed in the request")
        name = request.json.get("name")
        description = request.json.get("description")
        if not name or not description:
            raise CustomError(status_code=400, error_msg="Both name and description required")
        subject = Subject.query.filter_by(id = subject_id).first()
        if not subject:
            raise CustomError(status_code=404, error_msg="Subject not found")
        subject.name = name
        subject.description = description
        db.session.commit()
        return subject, 200
    
    def delete(self, subject_id = None ):
        if subject_id is None:
            raise CustomError(status_code=400, error_msg="Subject_id needed in the request")
        subject = Subject.query.filter_by(id = subject_id).first()
        if not subject:
            raise CustomError(status_code=404, error_msg="Subject not found")
        db.session.delete(subject)
        db.session.commit()
        return {"message": "Subject deleted successfully"}, 200


chapter_output = {
    "id" : fields.Integer,
    "name": fields.String,
    "description":fields.String
}

class ChapterApi(Resource):
    @marshal_with(chapter_output)
    def get(self, chapter_id = None, subject_id = None ):
        if chapter_id == None:
            chapters = Chapter.query.all()
            return chapters, 200
        chapter = Chapter.query.filter_by(id = chapter_id).first()
        if chapter:
            return chapter, 200
        return CustomError(status_code=404, error_msg="Subject not found")
    


# === resource add ===
api.add_resource(LoginApi, "/api/login")
api.add_resource(RegisterApi, "/api/register")
api.add_resource(SubjectApi, "/api/subjects", "/api/subjects/<int:subject_id>")
