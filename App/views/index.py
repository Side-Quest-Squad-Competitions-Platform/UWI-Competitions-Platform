from App.models.rank_history import RankHistory
from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, session
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import login_required, login_user, current_user, logout_user
from App.models import db
from App.controllers import *
import csv
from App.controllers import get_all_students

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def home_page():
    return render_template('homepage.html', user=current_user)


@index_views.route('/leaderboard', methods=['GET'])
def leaderboard_page():
    return render_template('leaderboard.html', leaderboard=display_rankings(), user=current_user)#, competitions=get_all_competitions(), moderators=get_all_moderators())


@index_views.route('/profile')
def profile():
    user_type = session['user_type']
    id = current_user.get_id()
    
    if user_type == 'moderator':
        template = moderator_profile(id)
    elif user_type == 'student':
        template = student_profile(id)
    else:
        # Handle unexpected user_type case
        template = render_template('login.html')

    return template


# @index_views.route('/student_profile/<int:id>', methods=['GET'])
# def student_profile(id):
#     student = get_student(id)

#     if not student:
#         return render_template('404.html')
    
#     profile_info = display_student_info(student.username)
#     competitions = profile_info['competitions']
#     """
#     competitions = Competition.query.filter(Competition.participants.any(id=user_id)).all()
#     ranking = Ranking.query.filter_by(student_id=user_id).first()
#     notifications= get_notifications(user.username)
#     """

#     return render_template('student_profile.html', student=student, competitions=competitions, user=current_user)


@index_views.route('/student_profile/<string:full_name>', methods=['GET'])
def student_profile_by_full_name(full_name):
    student = get_student_by_full_name(full_name)

    if not student:
        return render_template('404.html')
    
    profile_info = display_student_info(student.username)
    competitions = profile_info['competitions']
    """
    competitions = Competition.query.filter(Competition.participants.any(id=user_id)).all()
    ranking = Ranking.query.filter_by(student_id=user_id).first()
    notifications= get_notifications(user.username)
    """

    return render_template('student_profile.html', student=student, competitions=competitions, user=current_user)


@index_views.route('/student_profiles/<string:username>', methods=['GET'])
def student_profile_by_username(username):
    student = get_student_by_username(username)

    if not student:
        return render_template('404.html')
    
    profile_info = display_student_info(student.username)
    competitions = profile_info['competitions']
    """
    competitions = Competition.query.filter(Competition.participants.any(id=user_id)).all()
    ranking = Ranking.query.filter_by(student_id=user_id).first()
    notifications= get_notifications(user.username)
    """

    return render_template('student_profile.html', student=student, competitions=competitions, user=current_user)

@index_views.route('/moderator_profile/<int:id>', methods=['GET'])
def moderator_profile(id):   
    moderator = get_moderator(id)

    if not moderator:
        return render_template('404.html')
    """
    profile_info = display_student_info(student.username)
    competitions = profile_info['competitions']
    
    competitions = Competition.query.filter(Competition.participants.any(id=user_id)).all()
    ranking = Ranking.query.filter_by(student_id=user_id).first()
    notifications= get_notifications(user.username)
    """
    return render_template('moderator_profile.html', moderator=moderator, user=current_user)


@index_views.route('/init_postman', methods=['GET'])
def init_postman():
    
    db.drop_all()
    db.create_all()
    

    #creates students
    with open("students.csv") as student_file:
        reader = csv.DictReader(student_file)

        for student in reader:
            stud = create_student(student['username'], student['password'])
            #db.session.add(stud)
        #db.session.commit()
    
    student_file.close()

    #creates moderators
    with open("moderators.csv") as moderator_file:
        reader = csv.DictReader(moderator_file)

        for moderator in reader:
            mod = create_moderator(moderator['username'], moderator['password'])
            #db.session.add(mod)
        #db.session.commit()
    
    moderator_file.close()

    #creates competitions
    with open("competitions.csv") as competition_file:
        reader = csv.DictReader(competition_file)

        for competition in reader:
            comp = create_competition(competition['mod_names'], competition['comp_name'], competition['date'], competition['location'], competition['level'], competition['max_score'])
    
    competition_file.close()
    
    with open("results.csv") as results_file:
        reader = csv.DictReader(results_file)

        for result in reader:
            students = [result['student1'], result['student2'], result['student3']]
            team = add_team(result['mod_names'], result['comp_name'], result['team_name'], students)
            add_results(result['mod_names'], result['comp_name'], result['team_name'], int(result['score']))
            #db.session.add(comp)
        #db.session.commit()
    
    results_file.close()

    with open("competitions.csv") as competitions_file:
        reader = csv.DictReader(competitions_file)

        for competition in reader:
            update_ratings(competition['mod_names'], competition['comp_name'])
            UpdateLeaderboardCommand(moderator_id=None).execute()
            #db.session.add(comp)
        #db.session.commit()
    
    competitions_file.close()

    return (jsonify({'message': "database_initialized"}),200)


@index_views.route('/rank-history/<int:student_id>')
def rank_history(student_id):
    history = RankHistory.query.filter_by(student_id=student_id)\
        .order_by(RankHistory.recorded_at.asc()).all()

    return jsonify([
        {
            "competition": h.competition.name,
            "date": h.recorded_at.strftime("%Y-%m-%d"),
            "timestamp": h.recorded_at.strftime("%Y-%m-%d %H:%M:%S"),
            "rank": h.rank,
            "rating": h.rating
        }
        for h in history
    ])


@index_views.route('/student/<int:student_id>/rank-history')
def view_rank_history(student_id):
    student = Student.query.get(student_id)
    if not student:
        return "Student not found", 404
    return render_template('rank_history.html', student=student, user=current_user)


@index_views.route('/notifications', methods=['GET'])
@login_required
def notifications_view():
    if session.get('user_type') == 'student':
        user_notifications = list(reversed(current_user.notifications))
    else:
        user_notifications = []

    notifications_list = [notification.get_json() for notification in user_notifications]
    return render_template('notifications.html', notifications=notifications_list, user=current_user)