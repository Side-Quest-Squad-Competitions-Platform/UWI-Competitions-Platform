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

"""
@auth_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)


@auth_views.route('/identify', methods=['GET'])
@login_required
def identify_page():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})


@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    user = login(data['username'], data['password'])
    if user:
        login_user(user)
        return 'user logged in!'
    return 'bad username or password given', 401 """
"""
@auth_views.route('/logout', methods=['GET'])
@login_required
def logout_action():
    data = request.form
    user = login(data['username'], data['password'])
    logout_user()
    return 'logged out!'
"""
'''
API Routes
'''
"""
@auth_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@auth_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.json
    response = create_user(data['username'], data['password'])
    if response:
        return jsonify({'message': f"user created"}), 201
    return jsonify(error='error creating user'), 500

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = jwt_authenticate(data['username'], data['password'])
  if not token:
    return jsonify(error='bad username or password given'), 401
  return jsonify(access_token=token)

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user_action():
    return jsonify({'message': f"username: {jwt_current_user.username}, id : {jwt_current_user.id}"})
"""

@auth_views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student = get_student_by_username(request.form['username'])
        moderator = get_moderator_by_username(request.form['username'])
        if student:
            if request.form['username'] == student.username and student.check_password(request.form['password']):
                login_user(student)
                session['user_type'] = 'student'
                #flash("Login successful!", category='success')
                return render_template('homepage.html', user=current_user)
            #else:
            #flash("Invalid Credentials!", category='error')
            #return render_template('login.html', user=current_user)
        
        if moderator:
            if request.form['username'] == moderator.username and moderator.check_password(request.form['password']):
                login_user(moderator)
                session['user_type'] = 'moderator'
                #flash("Login successful!", category='success')
                return render_template('homepage.html', user=current_user)
            #else:
            #flash("Invalid Credentials!", category='error')
            #return render_template('login.html', user=current_user)
    
            #if not student and not moderator:
            #flash("Username not found!", category='error')
            #return render_template('404.html')
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
        student = create_student(request.form['username'], request.form['password'])
        
        if student:
            #flash('Username not available!', category="error")
            #return jsonify({'message': 'Username already used!'})
            if request.form['username'] == student.username:
            #flash('Account created successfully!', category="success")
                login_user(student)
                session['user_type'] = 'student'
                return render_template('homepage.html', user=current_user)#, competitions=get_all_competitions())
    
    return render_template('signup.html', user=current_user)
