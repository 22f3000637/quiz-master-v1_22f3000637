from flask import render_template, request, flash, session, redirect, url_for
from app import app,db
from models import User, Subject, Chapter, Quiz, Question
from datetime import datetime

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
            return render_template('login.html')
        if user and password:
            if user.is_admin:
                session['email'] = email
                flash('Login Successful', 'success')
                return redirect(url_for('admin_dashboard'))
            session['email'] = email
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
        return redirect(url_for('user_dashboard'))
    return render_template('register.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    email = session.get('email')
    if not email:
        flash('Please login first!!', 'warning')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = email).first()
    if not user.is_admin:
        if user:
            flash('You are not authorised!', 'warning')
            return redirect(url_for('user_dashboard'))
    subjects = Subject.query.all()
    return render_template('admin_dashboard.html', subjects = subjects, name = user.fullname)



@app.route('/user_dashboard')
def user_dashboard():
    email = session.get('email')
    user = User.query.filter_by(email = email).first()
    return render_template('user_dashboard.html', name = user.fullname)