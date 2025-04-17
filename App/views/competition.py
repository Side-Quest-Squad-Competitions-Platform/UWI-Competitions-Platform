from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for, session
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import current_user, login_required
import io
import csv
#from datetime import datetime

from.index import index_views

from App.controllers import *

comp_views = Blueprint('comp_views', __name__, template_folder='../templates')

##return the json list of competitions fetched from the db
@comp_views.route('/competitions', methods=['GET'])
def get_competitions():
    competitions = get_all_competitions_json()
    return render_template('competitions.html', competitions=get_all_competitions(), user=current_user)
    #return (jsonify(competitions),200) 
"""
##add new competition to the db
@comp_views.route('/competitions', methods=['POST'])
def add_new_comp():
    data = request.json
    response = create_competition(data['name'], data['date'], data['location'], data['level'], data['max score'])
    if response:
        return (jsonify({'message': "Competition created!"}), 201)
    return (jsonify({'error': "Error creating competition"}),500)
"""
#create new comp
@comp_views.route('/createcompetition', methods=['POST'])
@login_required
def create_comp():
    data = request.form
    
    if session.get('user_type') != 'moderator':
        flash("Unauthorized access")
        return redirect(url_for('comp_views.create_comp_page'))

    moderator = Moderator.query.filter_by(id=current_user.id).first()
    if not moderator:
        flash("Moderator not found")
        return redirect(url_for('comp_views.create_comp_page'))

    raw_date = data['date']
    
    date = f"{raw_date[8:10]}-{raw_date[5:7]}-{raw_date[0:4]}"
    
    moderator_usernames = request.form.getlist('moderators[]')

    result_msg = create_competition_by_moderator(
        moderator_id=moderator.id,
        mod_name=moderator.username,
        comp_name=data['name'],
        date=date,
        location=data['location'],
        level=data['level'],
        max_score=int(data['max_score'])
    )

    # Add additional moderators
    comp = get_competition_by_name(data['name'])
    if comp:
        for uname in moderator_usernames:
            if uname != moderator.username:
                add_mod(moderator.username, comp.name, uname)

    return render_template('competitions.html', competitions=get_all_competitions(), user=current_user)

#page to create new comp
@comp_views.route('/createcompetition', methods=['GET'])
def create_comp_page():
    return render_template('competition_creation.html', user=current_user)

"""
@comp_views.route('/competitions/moderator', methods=['POST'])
def add_comp_moderator():
    data = request.json
    response = add_mod()
    if response: 
        return (jsonify({'message': f"user added to competition"}),201)
    return (jsonify({'error': f"error adding user to competition"}),500)
"""
@comp_views.route('/competitions/<int:id>', methods=['GET'])
def competition_details(id):
    competition = get_competition(id)
    if not competition:
        return render_template('404.html')
    
    #team = get_all_teams()

    #teams = get_participants(competition_name)
    if current_user.is_authenticated:
        if session['user_type'] == 'moderator':
            moderator = Moderator.query.filter_by(id=current_user.id).first()
        else:
            moderator = None
    else:
        moderator = None
    
    leaderboard = display_competition_results(competition.name)
    return render_template('competition_details.html', competition=competition, moderator=moderator, leaderboard=leaderboard, user=current_user)#, team=team)

    #teams = get_participants(competition_name)
    #return render_template('Competition_Details.html', competition=competition)
    """
@index_views.route('/competition/<string:name>', methods=['GET'])
def competition_details(name):
    competition = get_competition_by_name(name)
    if not competition:
        return render_template('404.html')

    #teams = get_participants(competition_name)
    return render_template('competition_details.html', competition=competition)
"""
@comp_views.route('/competition/<string:name>', methods=['GET'])
def competition_details_by_name(name):
    competition = get_competition_by_name(name)
    if not competition:
        return render_template('404.html')

    #teams = get_participants(competition_name)
    if current_user.is_authenticated:
        if session['user_type'] == 'moderator':
            moderator = Moderator.query.filter_by(id=current_user.id).first()
        else:
            moderator = None
    else:
        moderator = None
    
    leaderboard = display_competition_results(name)

    return render_template('competition_details.html', competition=competition, moderator=moderator, leaderboard=leaderboard, user=current_user)
    
    """
@comp_views.route('/competitions/results', methods=['POST'])
def add_comp_results():
    data = request.json
    response = add_results(data['mod_name'], data['comp_name'], data['team_name'], data['score'])
    if response:
        return (jsonify({'message': "Results added successfully!"}),201)
    return (jsonify({'error': "Error adding results!"}),500)

@comp_views.route('/competitions/results/<int:id>', methods =['GET'])
def get_results(id):
    competition = get_competition(id)
    leaderboard = display_competition_results(competition.name)
    if not leaderboard:
        return jsonify({'error': 'Leaderboard not found!'}), 404 
    return (jsonify(leaderboard),200)
"""
#page to comp upload comp results
@comp_views.route('/add_results/<int:comp_id>', methods=['GET'])
def add_results_page(comp_id):
    competition = get_competition(comp_id)

    if not competition:
        return render_template('404.html')

    if session['user_type'] == 'moderator':
        moderator = Moderator.query.filter_by(id=current_user.id).first()
    else:
        moderator = None

    leaderboard = display_competition_results(competition.name)
    students = get_all_students()

    return render_template(
        'competition_results.html',
        competition=competition,
        moderator=moderator,
        leaderboard=leaderboard,
        students=students,  
        user=current_user
    )


@comp_views.route('/add_results/<string:comp_name>', methods=['POST'])
def add_competition_results(comp_name):
    competition = get_competition_by_name(comp_name)
    if session['user_type'] == 'moderator':
        moderator = Moderator.query.filter_by(id=current_user.id).first()
    else:
        moderator = None
        
    #if request.method == 'POST':
    data = request.form
    
    students = [data['student1'], data['student2'], data['student3']]
    response = add_team(moderator.username, comp_name, data['team_name'], students)

    if response:
        response = add_results(moderator.username, comp_name, data['team_name'], int(data['score']))
    #response = add_results(data['mod_name'], data['comp_name'], data['team_name'], int(data['score']))
    #if response:
    #    return (jsonify({'message': "Results added successfully!"}),201)
    #return (jsonify({'error': "Error adding results!"}),500)
    
    leaderboard = display_competition_results(comp_name)

    return render_template('competition_details.html', competition=competition, moderator=moderator, leaderboard=leaderboard, user=current_user)
    
@comp_views.route('/confirm_results/<string:comp_name>', methods=['GET', 'POST'])
def confirm_results(comp_name):
    if session['user_type'] == 'moderator':
        moderator = Moderator.query.filter_by(id=current_user.id).first()
    else:
        moderator = None
    
    competition = get_competition_by_name(comp_name)

    if update_ratings(moderator.username, competition.name):
        UpdateLeaderboardCommand(moderator.id).execute()

    leaderboard = display_competition_results(comp_name)

    return render_template('competition_details.html', competition=competition, moderator=moderator, leaderboard=leaderboard, user=current_user)
"""
@comp_views.route('/confirm_results/<string:comp_name>', methods=['POST'])
def confirm_results(comp_name):
    pass
"""
@comp_views.route('/upload_csv/<string:comp_name>', methods=['POST'])
def upload_results_csv(comp_name):
    file = request.files.get('csv_file')
    if not file or not file.filename.endswith('.csv'):
        flash("Please upload a valid CSV file.")
        return redirect(request.referrer)

    competition = get_competition_by_name(comp_name)
    if not competition:
        flash("Competition not found.")
        return redirect(request.referrer)

    moderator = Moderator.query.filter_by(id=current_user.id).first()
    if not moderator:
        flash("Unauthorized.")
        return redirect(request.referrer)

    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.DictReader(stream)

    for row in csv_input:
        students = [row['student1'], row['student2'], row['student3']]
        add_team(moderator.username, comp_name, row['team_name'], students)
        add_results(moderator.username, comp_name, row['team_name'], int(row['score']))

    flash("CSV uploaded successfully.")
    return redirect(url_for('comp_views.competition_details_by_name', name=comp_name))
