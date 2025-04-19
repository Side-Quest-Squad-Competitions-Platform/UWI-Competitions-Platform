from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for, session
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import login_required, login_user, current_user, logout_user
from App.models import db
from App.controllers import *


from.index import index_views

from App.controllers import *

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def api_login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return "Missing username or password", 400

    student = get_student_by_username(username)
    moderator = get_moderator_by_username(username)

    if student and student.check_password(password):
        login_user(student)
        session['user_type'] = 'student'
        return f"Login successful as student (user: {username})", 200

    if moderator and moderator.check_password(password):
        login_user(moderator)
        session['user_type'] = 'moderator'
        return f"Login successful as moderator (user: {username})", 200

    return "Invalid credentials", 401

@auth_views.route('/api/signup', methods=['POST'])
def api_signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        if not username or not password or not user_type:
            return jsonify({'error': 'Missing required fields'}), 400

        if user_type == 'student':
            user = create_student(username, password)
            session['user_type'] = 'student'
        elif user_type == 'moderator':
            user = create_moderator(username, password)
            session['user_type'] = 'moderator'
        else:
            return jsonify({'error': 'Invalid user type'}), 400

        if user:
            login_user(user)
            return jsonify({'message': 'User created successfully', 'user': username, 'user_type': user_type}), 201
        else:
            return jsonify({'error': 'Signup failed'}), 500

@auth_views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        student = get_student_by_username(request.form['username'])
        moderator = get_moderator_by_username(request.form['username'])
        
        if student:
            if request.form['username'] == student.username and student.check_password(request.form['password']):
                login_user(student)
                session['user_type'] = 'student'
                return render_template('homepage.html', user=current_user)
        
        if moderator:
            if request.form['username'] == moderator.username and moderator.check_password(request.form['password']):
                login_user(moderator)
                session['user_type'] = 'moderator'
                return render_template('homepage.html', user=current_user)
            
    return render_template('login.html', user=current_user)

@auth_views.route('/logout')
@login_required
def logout():
    logout_user()
    session['user_type'] = None
    return render_template('homepage.html', leaderboard=display_rankings(), user=current_user)

@auth_views.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']  

        if user_type == 'student':
            user = create_student(username, password)
            session['user_type'] = 'student'
        elif user_type == 'moderator':
            user = create_moderator(username, password)
            session['user_type'] = 'moderator'
        else:
            return render_template('signup.html', error="Invalid user type")

        if user:
            login_user(user)
            return redirect('/profile')
        else:
            return render_template('signup.html', error="Signup failed")

    return render_template('signup.html')
