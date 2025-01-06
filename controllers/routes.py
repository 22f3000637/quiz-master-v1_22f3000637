from flask import render_template, request, flash, session, redirect, url_for
from app import app
from models import User


@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        passwor = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not exist. Enter email correctly!')
            password = User.check_password(password=passwor)
        if not password:
            flash('Wrong password')
        if user and password and email == ('Admin@gmail.com' or 'Quizmaster@gmail.com') :
            session['email'] = email
            return redirect(url_for('admin_dashboard'))
        session['email'] = email
        return redirect(url_for('user_dashboard'))

        
    return render_template("login.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method=='POST':
        pass
    return render_template('register.html')


@app.route('/admin-dashboard')
def admin_dashboard():
    email = session.get('email')
    if email != ('Admin@gmail.com' or 'Quizmaster@gmail.com'):
        flash('You are not authorised!')
        return redirect(url_for('login'))
    return render_template('')