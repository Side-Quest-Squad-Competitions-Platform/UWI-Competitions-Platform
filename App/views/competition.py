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


# Form for creating new competition
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
    raw_time = data['time']

    datetime_string = f"{raw_date}T{raw_time}"
    datetime_obj = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M")
    formatted = datetime_obj.strftime("%d-%m-%YT%H:%M")
    
    moderator_usernames = request.form.getlist('moderators[]')

    result_msg = create_competition_by_moderator(
        moderator_id=moderator.id,
        mod_name=moderator.username,
        comp_name=data['name'],
        date=formatted,
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


@comp_views.route('/createcompetition', methods=['GET'])
@login_required
def create_comp_page():
    if session.get('user_type') != 'moderator':
        return redirect('/login')

    moderators = get_all_moderators()
    students = get_all_students()

    mod_usernames = [mod.username for mod in moderators]
    student_usernames = [stud.username for stud in students]

    return render_template(
        'competition_creation.html',
        moderators=mod_usernames,
        students=student_usernames,
        user=current_user
    )


# Competition Results Viewing
@comp_views.route('/competitions/<int:id>', methods=['GET'])
def competition_details(id):
    competition = get_competition(id)
    if not competition:
        return render_template('404.html')
    
    if current_user.is_authenticated:
        if session['user_type'] == 'moderator':
            moderator = Moderator.query.filter_by(id=current_user.id).first()
        else:
            moderator = None
    else:
        moderator = None
    
    leaderboard = display_competition_results(competition.name)
    return render_template('competition_details.html', competition=competition, moderator=moderator, leaderboard=leaderboard, user=current_user)#, team=team)
    

#Redirecting to page to add competition results
@comp_views.route('/add_results/<int:comp_id>', methods=['GET'])
def add_results_page(comp_id):
    competition = get_competition(comp_id)

    if not competition:
        return render_template('404.html')

    if session['user_type'] == 'moderator':
        moderator = Moderator.query.filter_by(id=current_user.id).first()
    else:
        moderator = None

    return render_template('competition_results.html', competition=competition, user=current_user)


# Fixed, uploads CSV file for Result model format now
@comp_views.route('/add_results/<int:comp_id>', methods=['POST'])
def add_results_csv(comp_id):
    file = request.files.get('csv_file')
    if not file or not file.filename.endswith('.csv'):
        flash("Please upload a valid CSV file.")
        return redirect(request.referrer)

    competition = get_competition(comp_id)
    if not competition:
        flash("Competition not found.")
        return redirect(request.referrer)

    moderator = Moderator.query.filter_by(id=current_user.id).first()
    if not moderator:
        flash("Unauthorized.")
        return redirect(request.referrer)

    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.DictReader(stream)

    array = list(csv_input)
    add_results(array)
    
    flash("CSV uploaded successfully.")
    return redirect(url_for("comp_views.competition_details", id=comp_id))


# Works for updating leaderboard
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


# Working, not flashing errors for authentication though
@comp_views.route('/editcompetition/<int:comp_id>', methods=['GET', 'POST'])
@login_required
def edit_competition(comp_id):
    comp = Competition.query.get_or_404(comp_id)
    
    moderator = Moderator.query.filter_by(id=current_user.id).first()
    if moderator not in comp.moderators:
        flash("Unauthorized.")
        return redirect(request.referrer)

    all_mods = Moderator.query.order_by(Moderator.username).all()

    if request.method == 'POST':
        raw_date = request.form['date']            
        raw_time = request.form['time']            
        comp.name       = request.form['name']
        comp.datetime   = datetime.strptime(f"{raw_date}T{raw_time}", "%Y-%m-%dT%H:%M")
        comp.location   = request.form['location']
        comp.level      = float(request.form['level'])
        comp.max_score  = int(request.form['max_score'])

        
        
        sel_usernames = request.form.getlist('moderators[]')
        comp.moderators.clear()
        for uname in sel_usernames:
            m = Moderator.query.filter_by(username=uname).first()
            if m:
                comp.moderators.append(m)

        db.session.commit()
        flash("Competition updated!", "success")
        return redirect(url_for('comp_views.get_competitions'))
    
    selected_usernames = [m.username for m in comp.moderators]

    
    return render_template(
        'edit_competition.html',
        competition=comp,
        moderators=all_mods,
        selected_mods = selected_usernames,
        user=current_user
        
    )


# Fixed, not flashing unauthorized and not updating score and rankings
@comp_views.route('/competitions/<int:comp_id>/delete/<string:team_name>', methods=['GET','POST'])
@login_required
def delete_result(comp_id,team_name):
    comp = Competition.query.get_or_404(comp_id)
    if not comp:
        ConnectionAbortedError(404)

    moderator = Moderator.query.filter_by(id=current_user.id).first()
    if moderator not in comp.moderators:
        flash("Unauthorized.")
        return redirect(request.referrer)
    
    results = get_results(comp_id, team_name)
    if not results:
        ConnectionAbortedError(404)

    if session['user_type'] == 'moderator':
        moderator = Moderator.query.filter_by(id=current_user.id).first()
    else:
        moderator = None    

    for result in results:
        db.session.delete(result) 
    db.session.commit()   
    return redirect(url_for('comp_views.competition_details', id=comp_id))          