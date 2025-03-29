from flask import render_template, request, flash, session, redirect, url_for
from app import db
from flask import current_app as app
from models import User, Subject, Chapter, Quiz, Question, Scores, Userattempt
from datetime import datetime, timedelta
from functools import wraps 
import matplotlib.pyplot as plt
import matplotlib
import random



matplotlib.use('Agg')


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
        user = User.query.filter_by(email=email, is_admin=False).first()
        if not user:
            flash('User not found.Please login first!!', 'warning')
            return redirect(url_for('login'))
        return func()
    return inner

#routes creation
@app.route('/')
def index():
    return render_template("index.html")


@app.route("/login" , methods=['GET', 'POST'])
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
        flash('User registered successfully', 'success')
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
@app.route('/new_question/<int:quiz_id>/<int:chapter_id>', methods = ['GET', 'POST'])
def new_question(quiz_id, chapter_id):
    quiz = Quiz.query.filter_by(id = quiz_id).first()
    chapter = Chapter.query.filter_by(id = chapter_id).first()
    if request.method == 'POST':
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
            chapter_id = chapter_id,
            quiz_id = quiz_id
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully', 'success')
        return redirect(url_for('quiz_dashboard'))
    return render_template('question_form.html', chapter = chapter, quiz = quiz)


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
        question.question_title = q_title
        question.question = ques
        question.option_1 = option_1
        question.option_2 = option_2
        question.option_3 = option_3
        question.option_4 = option_4
        question.correct_answer = correct_answer
        question.marks = marks
        db.session.commit()
        flash('Question updated successfully', 'success')
        return redirect(url_for('quiz_dashboard'))                            
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
        quiz.date_of_quiz = datetime.strptime(date, '%Y-%m-%d')
        quiz.time_duration = duration
        db.session.commit()
        flash('Quiz updated', 'success')
        return redirect(url_for('quiz_dashboard'))
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
    quizes = Quiz.query.all()
    current_date = datetime.now().date()
    return render_template('user_dashboard.html', name = name, quizes = quizes,current_date = current_date)

@login_required
@app.route('/quiz_detail/<int:quiz_id>')
def quiz_detail(quiz_id):
    quiz = Quiz.query.filter_by(id = quiz_id).first()
    return render_template('quiz_detail.html', quiz = quiz)



# quiz starter
@login_required
@app.route("/start_quiz/<int:quiz_id>/")
def start_quiz(quiz_id):
    email = session.get('email')
    user = User.query.filter_by(email=email).first()
    quiz = Quiz.query.filter_by(id=quiz_id).first()

    if not user or not quiz:
        flash("Invalid quiz or user!", "error")
        return redirect(url_for("user_dashboard"))
    
    # if datetime.today().date() < quiz.date_of_quiz:
    #     flash("Quiz is not yet available!", "error")
    #     return redirect(url_for("user_dashboard"))
    if quiz.questions == []:
        flash("Questions not added yet", "error")
        return redirect(url_for("user_dashboard"))
    
    time_duration = str(quiz.time_duration).strip().split(":")
    print(time_duration)
    hours = int(time_duration[0])
    print(hours)
    minutes = int(time_duration[1])
    print(minutes)
        
    first_question = quiz.questions[0]
    if hours:
        end_time = datetime.now() + timedelta(minutes=minutes, hours=hours)
    else:
        end_time = datetime.now() + timedelta(minutes=minutes)
    session["isotime"] = end_time.isoformat()
    session["format_time"] = end_time.strftime("%d-%m-%Y %I:%M:%S %p")
    return redirect(url_for("quiz_question", quiz_id=quiz_id, question_id=first_question.id))

# next quiz
@login_required
@app.route("/quiz_question/<int:quiz_id>/<int:question_id>", methods=['GET', 'POST'])
def quiz_question(quiz_id, question_id):
    email = session.get('email')
    user = User.query.filter_by(email=email).first()
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    question = Question.query.filter_by(id=question_id).first()

    if not user or not quiz or not question:
        flash("Invalid quiz or question!", "error")
        return redirect(url_for("user_dashboard"))
    
    index_num = quiz.questions.index(question)
    attempt = Userattempt.query.filter_by(user_id=user.id, quiz_id=quiz_id, question_id=question.id).one_or_none()
    score = Scores.query.filter_by(user_id=user.id, quiz_id=quiz_id).first()
    
    if not attempt and score:
        score.total_scored = 0
        score.time_stamp_of_attempt = datetime.now()
        db.session.commit()
    
    if request.method == 'POST':
        selected_answer = request.form.get('option', None)
        action = request.form.get('action')
        correct_answer = question.correct_answer

        if not score:
            score = Scores(user_id=user.id, quiz_id=quiz_id, total_scored=0, time_stamp_of_attempt=datetime.now())
            db.session.add(score)

        if selected_answer:
            if not attempt:
                attempt = Userattempt(user_id=user.id, quiz_id=quiz_id, question_id=question.id, user_answer=selected_answer)
                db.session.add(attempt)
                if selected_answer == correct_answer:
                    score.total_scored += question.marks
            else:
                previous_correct = attempt.user_answer == correct_answer
                new_correct = selected_answer == correct_answer
                attempt.user_answer = selected_answer

                if not previous_correct and new_correct:
                    score.total_scored += question.marks
                elif previous_correct and not new_correct:
                    score.total_scored -= question.marks
        if selected_answer is None:
            if not attempt:
                attempt = Userattempt(user_id=user.id, quiz_id=quiz_id, question_id=question.id, user_answer=selected_answer)
            attempt.user_answer = selected_answer
            db.session.add(attempt)
        db.session.commit()

        if action == "submit":
            session.pop("format_time", None)
            session.pop("isotime", None)
            flash('Quiz submitted successfully', 'success')
            return redirect(url_for("quiz_result", quiz_id=quiz_id))
        
        if action == "clear":
            db.session.delete(attempt)
            db.session.commit()
            flash('Response cleared', 'error')
            return redirect(request.url)
        
        if index_num + 1 == len(quiz.questions):
            next_question = quiz.questions[(index_num + 1) % len(quiz.questions) ]
            return redirect(url_for("quiz_question", quiz_id=quiz_id, question_id=next_question.id)) 
        if index_num + 1 < len(quiz.questions):
            next_question = quiz.questions[index_num + 1]
            return redirect(url_for("quiz_question", quiz_id=quiz_id, question_id=next_question.id)) 
        return redirect(url_for("quiz_result", quiz_id=quiz_id))
    
    return render_template("question.html", quiz=quiz, question=question, num=index_num + 1,
                           end_time=session.get("format_time"), isotime=session.get("isotime"), attempt=attempt)


# submission
@login_required
@app.route("/quiz_result/<int:quiz_id>")
def quiz_result(quiz_id):
    email = session.get('email')
    user = User.query.filter_by(email=email).first()
    score = Scores.query.filter_by(user_id=user.id, quiz_id=quiz_id).first()
    results = (
        db.session.query(Userattempt.user_answer, Question.correct_answer, Question.marks, Question.question).filter_by(user_id = user.id)
        .join(Question, Userattempt.question_id == Question.id)
        .join(Quiz, Quiz.id == Question.quiz_id).filter_by(id = quiz_id).all()
    )
    total = 0
    for result in results:
        total += result.marks
    return render_template("quiz_result.html", results = results, score=score, name= session.get('name'), total =total)

# scores for user
@login_required
@app.route('/scores')
def scores():
    email = session.get('email')
    user = User.query.filter_by(email = email).first()
    scores = Scores.query.filter_by(user_id = user.id).all()
    quizzes = Quiz.query.all()
    return render_template('scores.html', scores = scores, quizzes = quizzes, name = session.get('name'))


#    Admin summary
@admin_required
@app.route('/admin_summary')
def admin_summary(): 
    subject_scores = {}
    subject_colors = {}
    subjects = Subject.query.all()
    for subject in subjects:
        for chapter in subject.chapters:
            for quiz in chapter.quizes:
                scores = Scores.query.filter_by(quiz_id=quiz.id).all()
                for score in scores:
                    if subject.name not in subject_scores or score.total_scored > subject_scores[subject.name]:
                        subject_scores[subject.name] = score.total_scored
                        subject_colors[subject.name] = (random.random(), random.random(), random.random())
    # Bar Graph
    plt.figure()
    subject_names = list(subject_scores.keys())
    scores = list(subject_scores.values())
    colors = [subject_colors[name] for name in subject_names]

    bar_container = plt.bar(subject_names, scores, color=colors)
    plt.bar_label(bar_container)
    plt.xlabel('Subjects', fontweight='bold')
    plt.ylabel('Scores', fontweight='bold')
    plt.title("Highest Scores of Each Subject", pad=30, fontweight='bold')
    plt.savefig('static/bar1.png')
    plt.clf()
    # Pie Graph
    query = (
        db.session.query(Subject.name, db.func.count(Scores.id))
        .join(Chapter, Subject.id == Chapter.subject_id)
        .join(Quiz, Chapter.id == Quiz.chapter_id)
        .join(Scores, Scores.quiz_id == Quiz.id)
        .group_by(Subject.name)
        .all()
    )
    
    subjects = [name for name, _ in query]
    counts = [count for _, count in query]
    colors = [subject_colors.get(name, (random.random(), random.random(), random.random())) for name in subjects]

    plt.figure()
    plt.pie(counts, colors=colors, labels=subjects, autopct='%1.1f%%', labeldistance=1)
    plt.title("Attempts of Each Subject", fontweight='bold')
    plt.savefig('static/circle1.png')
    plt.clf()

    return render_template('admin_summary.html', name = session.get('name'))



#all users
@admin_required
@app.route("/user_details")
def user_details():
    users = User.query.filter_by(is_admin = False).all()
    return render_template('user_list.html', users = users, name = session.get('name', None))

@admin_required
@app.route("/edit_user/<int:user_id>", methods=['GET','POST'])
def edit_user(user_id):
    user = User.query.filter_by(id = user_id).first()
    if request.method == "POST":
        name = request.form.get('name')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')
        user.fullname = name
        user.qualification = qualification
        user.dob = datetime.strptime(dob, "%Y-%m-%d")
        db.session.commit()
        return redirect(url_for('user_details'))
    return render_template('register.html', user = user)

@admin_required
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.filter_by(id = user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(request.referrer)



# User summary

@app.route('/user_summary')
@login_required
def user_summary():
    email = session.get('email')
    user = User.query.filter_by(email = email).first()
    subjects = []
    counts = []
    random_colors = []
    query = (
        db.session.query(Subject.name, db.func.count(Scores.id))
        .join(Chapter, Subject.id == Chapter.subject_id)
        .join(Quiz, Chapter.id == Quiz.chapter_id)
        .join(Scores, Scores.quiz_id == Quiz.id)
        .join(User, User.id == user.id)
        .group_by(Subject.name)
        .all()
    )
    for subject_name, count in query:
        subjects.append(subject_name)
        counts.append(count)
        random_colors.append((random.random(), random.random(), random.random()))
    #bar graph
    bar_container = plt.bar(subjects, counts, color = random_colors )
    plt.bar_label(bar_container)
    plt.xlabel('Subjects',fontweight ='bold')
    plt.ylabel('Attempts',fontweight ='bold')
    plt.title("Subject wise no.of quizzes", pad=30, fontweight ='bold')
    plt.savefig('static/bar2.png')
    plt.clf()
    quiz_attempt = {}
    scores = Scores.query.filter_by(user_id = user.id).all()
    for score in scores:
        month = score.time_stamp_of_attempt
        month = datetime.strftime(month, "%m/%Y")
        if month in quiz_attempt:
            quiz_attempt[month] += 1
        else:
            quiz_attempt[month] = 1
    # pie graph
    month = list(quiz_attempt.keys())
    counts = list(quiz_attempt.values())
    plt.figure()
    plt.pie(counts, colors=random_colors, labels=month,
            autopct=lambda pct: f'{int(pct * sum(counts) / 100):02d} ({pct:.1f}%)', labeldistance=1)
    plt.title("Month wise no.of quizzes attempted", fontweight='bold')
    plt.savefig('static/circle2.png')
    plt.clf()
    return render_template('user_summary.html', name = session.get('name'), user = user)



# Search functions

@app.route('/searched')
def searched():
    email = session.get('email')
    user = User.query.filter_by(email = email).first()
    category = request.args.get('category')
    word = request.args.get('query')
    word = "%{}%".format(word)
    if user.is_admin:
        if category == "Subject":
            results = Subject.query.filter(Subject.name.like(word)).all() 
        elif category == "User":
            results = User.query.filter(User.fullname.like(word)).filter_by(is_admin = False).all()
        elif category == 'Quiz':
            results = Chapter.query.filter(Chapter.name.like(word)).all()
    else:
        if category == "Score":
            results = Scores.query.filter_by(user_id = user.id).filter(Scores.total_scored.like(word)).all()
        if category == "Date":
            results = Quiz.query.filter(Quiz.date_of_quiz.like(word)).all()
    return render_template('searched.html', results = results, admin = user.is_admin, category = category,name = session.get('name')) 
    

#            logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'error')
    return redirect(url_for('index'))