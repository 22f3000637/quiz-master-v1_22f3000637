from flask import render_template, request, flash, session, redirect, url_for
from app import app,db
from models import User, Subject, Chapter, Quiz, Question
from datetime import datetime
from functools import wraps 


#admin verification decorator
def admin_required(func):
    @wraps(func)
    def inner1():
        email = session.get('email')
        if not email:
            flash('Please login first!!', 'warning')
            return redirect(url_for('login'))
        user = User.query.filter_by(email=email).first()
        if not user.is_admin:
            flash("You are not authorized to access this page!", "warning")
            return redirect(url_for('user_dashboard'))
        return func() 
    return inner1

#login verification decorator
def login_required(func):
    @wraps(func)
    def inner():
        email = session.get('email')
        if not email:
            flash('Please login first!!', 'warning')
            return redirect(url_for('login'))
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found.Please login first!!', 'warning')
            return redirect(url_for('login'))
        return func()
    return inner

#routes creation
@app.route("/" , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not exist. Enter email correctly!', 'error')
            return render_template('login.html')     
        if not user.check_password(plain_password=password):
            flash("Incorrect password. Please try again.", "error")
            return render_template('login.html')
        if user and password:
            if user.is_admin:
                session['email'] = email
                session['name'] = user.fullname
                flash('Login Successful', 'success')
                return redirect(url_for('admin_dashboard'))
            session['email'] = email
            session['name'] = user.fullname
            return redirect(url_for('user_dashboard'))    
    return render_template("login.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method=='POST':
        name = request.form.get('name')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')
        email = request.form.get('email').lower()
        password = request.form.get('password')
        
        user = User.query.filter_by(email = email).first()
        if user:
            flash("User already exist. Please login!", 'error')
            return redirect(url_for('login'))
        password_hash = User.hashing_password(password=password)
        user = User(email=email,
                    hashed_password = password_hash,
                    fullname = name,
                    dob = datetime.strptime(dob, '%Y-%m-%d'),
                    qualification = qualification)
        db.session.add(user)
        db.session.commit()
        session['email'] = email
        session['name'] = name
        return redirect(url_for('user_dashboard'))
    return render_template('register.html')

#          admin dashboard 
@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    name = session.get('name')
    subjects = Subject.query.all()
    return render_template('admin_dashboard.html', subjects = subjects, name = name)


#        Admin crud operations
#       Subject crud
@admin_required
@app.route("/new_subject", methods=['GET', 'POST'])
def new_subject():
    if request.method == 'POST':
        name = request.form.get('subject-name')
        description = request.form.get('subject-desc')
        subject = Subject.query.filter_by(name = name).first()
        if subject:
            flash(f'{subject.name} already exist', 'warning')
            return redirect("/new_subject")
        subject = Subject(name = name, description = description)
        db.session.add(subject)
        db.session.commit()
        flash(f'{name} subject added successfully!','success')
        return redirect(url_for('admin_dashboard'))
    return render_template('new_subject.html')

@admin_required
@app.route('/update_subject/<int:subject_id>', methods = ['GET', 'POST'])
def update_subject(subject_id):
    subject = Subject.query.filter_by(id = subject_id).first()
    if request.method == 'POST':
        name  = request.form.get('subject-name')
        description = request.form.get('subject-desc')
        subject.name = name
        subject.description = description
        db.session.commit()
        flash(f'{name} updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('/new_subject.html', subject = subject)

@admin_required
@app.route("/delete_subject/<int:subject_id>")
def delete_subject(subject_id):
    subject = Subject.query.filter_by(id = subject_id).first()
    db.session.delete(subject)
    db.session.commit()
    flash(f'{subject.name} subject got deleted!', 'error')
    return redirect(url_for('admin_dashboard'))



#      Chapter crud
@admin_required
@app.route("/new_chapter/<int:subject_id>", methods=['GET', 'POST'])
def new_chapter(subject_id):
    subject = Subject.query.filter_by(id = subject_id).first()
    if request.method == 'POST':   
        name = request.form.get('chapter-name')
        description = request.form.get('chapter-desc')
        chapter = Chapter(name=name, description = description, subject_id = subject_id)
        db.session.add(chapter)
        db.session.commit()
        flash(f"{name} chapter added to {subject.name} !", "success")   
        return redirect(url_for('admin_dashboard')) 
    return render_template('new_chapter.html', subject = subject)


@admin_required
@app.route("/chapter_update/<int:chapter_id>", methods=['GET', 'POST'])
def update_chapter(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()  
    if request.method == 'POST':
        name = request.form.get('chapter-name')
        description = request.form.get('chapter-desc')
        chapter.name = name
        chapter.description = description
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('new_chapter.html', chapter=chapter)

@admin_required
@app.route("/delete_chapter/<int:chapter_id>")
def delete_chapter(chapter_id):   
    chapter = Chapter.query.filter_by(id=chapter_id).first()  
    db.session.delete(chapter)
    db.session.commit()
    flash(f'{chapter.name} chapter got deleted!', 'error')
    return redirect(url_for('admin_dashboard'))


#             Questions Crud
@admin_required
@app.route('/new_question', methods = ['GET', 'POST'])
def new_question():
    chapters = Chapter.query.all()
    if request.method == 'POST':
        id = request.form.get('chapter_id')
        question_title = request.form.get('q-title')
        question = request.form.get('question')
        option_1 = request.form.get('option_1')
        option_2 = request.form.get('option_2')
        option_3 = request.form.get('option_3')
        option_4 = request.form.get('option_4')
        correct_answer = request.form.get('correct_answer')
        marks = request.form.get('marks')
        question = Question(
            question_title = question_title,
            question = question,
            option_1 = option_1,
            option_2 = option_2,
            option_3 = option_3,
            option_4 = option_4,
            correct_answer = correct_answer,
            marks = marks,
            chapter_id = id
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully', 'success')
        return redirect(url_for('quiz_dashboard'))
    return render_template('question_form.html', chapters = chapters)


@admin_required
@app.route("/update_question/<int:question_id>", methods=['GET', 'POST'])
def update_question(question_id):
    question = Question.query.filter_by(id = question_id).first()
    if request.method == 'POST':
        q_title = request.form.get('q-title')
        ques = request.form.get('question')
        option_1 = request.form.get('option_1')
        option_2 = request.form.get('option_2')
        option_3 = request.form.get('option_3')
        option_4 = request.form.get('option_4')
        correct_answer = request.form.get('correct_answer')
        marks = request.form.get('marks')
        question.question_title = q_title,
        question.question = ques,
        question.option_1 = option_1,
        question.option_2 = option_2,
        question.option_3 = option_3,
        question.option_4 = option_4,
        question.correct_answer = correct_answer,
        question.marks = marks
        db.session.commit()
        flash('Question updated successfully', 'success')
        return render_template(url_for('quiz_dashboard'))                            
    return render_template('question_form.html', question = question)



@admin_required
@app.route("/delete_question/<int:question_id>")
def delete_question(question_id):
    question = Question.query.filter_by(id = question_id).first()
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted','success')
    return redirect(url_for('quiz_dashboard'))



#   Quiz dashboard
@admin_required
@app.route('/quiz_management')
def quiz_dashboard():
    name = session.get('name')
    quizes = Quiz.query.all()
    chapters = Chapter.query.all()
    return render_template('quiz_management.html', name = name, quizes = quizes, chapters = chapters)


#  quiz crud
@admin_required
@app.route('/new_quiz', methods=['GET','POST'])
def new_quiz():
    chapters = Chapter.query.all()
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        date = request.form.get('date')
        duration = request.form.get('duration')
        if duration:
            if duration == "30":
                duration = datetime.strptime('00:30', '%H:%M').time()
            if duration == "60":
                duration = datetime.strptime('01:00', '%H:%M').time()
            if duration == "90":
                duration = datetime.strptime('01:30', '%H:%M').time()
            if duration == "120":
                duration = datetime.strptime('02:00', '%H:%M').time()
            if duration == "150":
                duration = datetime.strptime('02:30', '%H:%M').time()
            quiz = Quiz(chapter_id = chapter_id,
                        date_of_quiz = datetime.strptime(date, '%Y-%m-%d'),
                        time_duration = duration)
            db.session.add(quiz)
            db.session.commit()
            flash('Quiz added successfully', 'success')
            return redirect(url_for('quiz_dashboard'))
    return render_template('quiz_form.html', chapters = chapters)



@admin_required
@app.route('/update_quiz/<int:quiz_id>', methods = ['GET','POST'])
def update_quiz(quiz_id):
    quiz = Quiz.query.filter_by(id = quiz_id ).first()
    if request.method == 'POST':
        date = request.form.get('date')
        duration = request.form.get('duration')
        if duration:
            if duration == "30":
                duration = datetime.strptime('00:30', '%H:%M').time()
            if duration == "60":
                duration = datetime.strptime('01:00', '%H:%M').time()
            if duration == "90":
                duration = datetime.strptime('01:30', '%H:%M').time()
            if duration == "120":
                duration = datetime.strptime('02:00', '%H:%M').time()
            if duration == "150":
                duration = datetime.strptime('02:30', '%H:%M').time()
            quiz.date_of_quiz = date
            quiz.time_duration = duration
            db.session.commit()
    return render_template('quiz_form.html', quiz = quiz)

@admin_required
@app.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    quiz = Quiz.query.filter_by(id = quiz_id).first()
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted','success')
    return redirect(url_for('quiz_dashboard'))

#         user dashboard
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    name = session.get('name')
    return render_template('user_dashboard.html', name = name)








#            logout
@app.route('/logout')
def logout():
    session.pop('email')
    session.pop('name')
    return redirect(url_for('login'))