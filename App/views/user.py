from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for, session
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import current_user, login_required

from flask_login import login_required, login_user, current_user, logout_user

from.index import index_views

from App.controllers import *

user_views = Blueprint('user_views', __name__, template_folder='../templates')

"""
@user_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_students_json()
    return jsonify(users)

#@user_views.route('/api/users', methods=['POST'])
#def create_user_endpoint():
#    data = request.json
#    response = create_user(data['username'], data['password'])
#    if response:
#        return (jsonify({'message': f"user created"}),201)
#    return (jsonify({'error': f"error creating user"}),500)

@user_views.route('/host_join', methods=['POST'])
def join_competition():
    data = request.json
    Hosting  = join_comp(data['username'], data['CompName'])
    if Hosting is None:
      return jsonify({'message': f"Error"}), 409
    return jsonify({'message': f" {Hosting.username} has joined {Hosting.CompName}"})

@user_views.route('/Create_Host', methods=['POST'])
def create_host_action():
    data = request.json
    Host  = create_host(data['username'], data['password'],data['host_id'])
    if Host is None:
      return jsonify({'message': f"user {data['username']} already exists"}), 409
    return jsonify({'message': f"user {Host.username} created"})

@user_views.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')

@user_views.route('/tester', methods=['GET'])
def random_function():
    flash(f"hello user this test has been successful") 
    return "yes"

@user_views.route('/all_rankings', methods=['GET'])
def get_user_rankings():
    users = display_rankings()
    rankings = [u.to_dict() for u in users]
    return jsonify(rankings)

@user_views.route('/users/competitions/<int:id>', methods = ['GET'])
def get_user_comps(id):
    data = request.form
    # comps = get_user_competitions(data['id'])
    comps = get_competition(id)
    # userCompetitions =  [c.toDict() for c in comps]
    return jsonify(comps)

@user_views.route('/api/students', methods=['POST'])
def create_student_endpoint():
    data = request.json
    student  = create_student(data['username'], data['password'])
    if student is None:
      return jsonify({'message': f"user {data['username']} already exists"}), 409
    return jsonify({'message': f"user {student.username} created"})

@user_views.route('/create_competition', methods=['POST'])
def create_competition():
    data = request.json
    admin = Admin.query.filter_by(staff_id=data['CreatorId']).first()
    if admin:
      comp=get_competition_by_name(data['name'])
      if comp is None:
        comp=create_competition(data['name'], data['CreatorId'])
        return jsonify({'message': f"Competition {comp.name} created"})
      return jsonify({'message': f"Competition {comp.name} already exists"}), 409
    return jsonify({'message': f"Admin {data['CreatorId']} does not exist! Stop the shenanigans students"}), 409

@user_views.route('/AllNotifications', methods=['GET'])
def get_all_notifications():
    notifications = display_notifications()
    return jsonify(notifications)
"""