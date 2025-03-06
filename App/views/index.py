from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, session
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import login_required, login_user, current_user, logout_user
from App.models import db
from App.controllers import *
import csv

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def home_page():
    return render_template('homepage.html', leaderboard=display_rankings(), user=current_user)

@index_views.route('/leaderboard', methods=['GET'])
def leaderboard_page():
    return render_template('leaderboard.html', leaderboard=display_rankings(), user=current_user)#, competitions=get_all_competitions(), moderators=get_all_moderators())

@index_views.route('/init', methods=['GET'])
def init():
    """
    db.drop_all()
    db.create_all()
    create_student('bob', 'bobpass')
    create_student('alice', 'alicepass')
    create_student('charlie', 'charliepass')
    create_student('david', 'davidpass')
    create_admin('admin', 'adminpass',1)
    create_host('admin2', 'adminpass2',2)
    create_host('admin3', 'adminpass3',3)
    create_competition('RunTime', 1)
    join_comp('admin2', 'RunTime')
    register_student('bob', 'RunTime')
    register_student('alice', 'RunTime')
    register_student('charlie', 'RunTime')
    register_student('david', 'RunTime')
    create_competition('RunTime2', 1)
    add_results('admin2', 'bob', "RunTime",5)
    add_results('admin2', 'alice', "RunTime",10)
    add_results('admin2', 'charlie', "RunTime",15)
    create_competition('RunTime3', 1)
    join_comp('admin3', 'RunTime3')
    register_student('bob', 'RunTime3')
    register_student('alice', 'RunTime3')
    register_student('charlie', 'RunTime3')
    add_results('admin3', 'bob', "RunTime3",5)
    add_results('admin3', 'alice', "RunTime3",10)
    add_results('admin3', 'charlie', "RunTime3",15)
    """
    db.drop_all()
    db.create_all()
    """
    stud1 = create_student('stud1', 'stud1pass')
    stud2 = create_student('stud2', 'stud2pass')
    stud3 = create_student('stud3', 'stud3pass')
    stud4 = create_student('stud4', 'stud4pass')
    stud5 = create_student('stud5', 'stud5pass')
    stud6 = create_student('stud6', 'stud6pass')
    stud7 = create_student('stud7', 'stud7pass')
    stud8 = create_student('stud8', 'stud8pass')
    stud9 = create_student('stud9', 'stud9pass')
    stud10 = create_student('stud10', 'stud10pass')
    mod1 = create_moderator('mod1', 'mod1pass')
    mod2 = create_moderator('mod2', 'mod2pass')
    mod3 = create_moderator('mod3', 'mod3pass')
    comp1 = create_competition('mod1', 'comp1', '09-02-2024', 'CSL', 1, 25)
    comp2 = create_competition('mod2', 'comp2', '09-02-2024', 'CSL', 2, 20)
    mod = add_mod('mod1', 'comp1', 'mod3')

    students = ["stud1", "stud2", "stud3"]
    add_team('mod1', 'comp1', "A", students)
    add_results('mod1', 'comp1', "A", 16)
    
    students = ["stud4", "stud5", "stud6"]
    add_team('mod1', 'comp1', "B", students)
    add_results('mod1', 'comp1', "B", 15)

    students = ["stud7", "stud8", "stud9"]
    add_team('mod1', 'comp1', "C", students)
    add_results('mod1', 'comp1', "C", 12)

    students = ["stud10", "stud4", "stud7"]
    add_team('mod2', 'comp2', "A", students)
    add_results('mod2', 'comp2', "A", 10)
    
    students = ["stud2", "stud5", "stud8"]
    add_team('mod2', 'comp2', "B", students)
    add_results('mod2', 'comp2', "B", 15)

    students = ["stud3", "stud6", "stud9"]
    add_team('mod2', 'comp2', "C", students)
    add_results('mod2', 'comp2', "C", 12)

    update_ratings('mod1', 'comp1')
    update_rankings()

    update_ratings('mod2', 'comp2')
    update_rankings()
    """

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
            comp = create_competition(competition['mod_name'], competition['comp_name'], competition['date'], competition['location'], competition['level'], competition['max_score'])
    
    competition_file.close()
    
    with open("results.csv") as results_file:
        reader = csv.DictReader(results_file)

        for result in reader:
            students = [result['student1'], result['student2'], result['student3']]
            team = add_team(result['mod_name'], result['comp_name'], result['team_name'], students)
            add_results(result['mod_name'], result['comp_name'], result['team_name'], int(result['score']))
            #db.session.add(comp)
        #db.session.commit()
    
    results_file.close()

    with open("competitions.csv") as competitions_file:
        reader = csv.DictReader(competitions_file)

        for competition in reader:
            if competition['comp_name'] != 'TopCoder':
                update_ratings(competition['mod_name'], competition['comp_name'])
                update_rankings()
            #db.session.add(comp)
        #db.session.commit()
    
    competitions_file.close()

    return render_template('leaderboard.html', leaderboard=display_rankings(), user=current_user)
    """
@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})

@index_views.route('/healthcheck', methods=['GET'])
def health():
    return jsonify({'status':'healthy'})

#@index_views.route('/Student_Profile/<int:user_id>')
#def Student_Profile(user_id):
 #   return render_template('Student_Profile.html', user_id=user_id)
"""

@index_views.route('/profile')
def profile():
    user_type = session['user_type']
    id = current_user.get_id()
    
    if user_type == 'moderator':
        template = moderator_profile(id)

    if user_type == 'student':
        template = student_profile(id)

    return template

@index_views.route('/student_profile/<int:id>', methods=['GET'])
def student_profile(id):
    student = get_student(id)

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

@index_views.route('/student_profile/<string:name>', methods=['GET'])
def student_profile_by_name(name):
    student = get_student_by_username(name)

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

    """
@index_views.route('/register_competition', methods=['POST'])
def Register_Competition():
    username = request.form.get('username')
    competition_name = request.form.get('competition_name')

    result = register_student(username, competition_name)
    if result:
        return f'Successfully registered {username} for {competition_name}'
    else:
        return 'Registration failed'

@index_views.route('/student_ranking/<int:id>')
def student_rank(id):
    student =get_student(id)

    if not student:
        return render_template('404.html')
    
    competitions = Competition.query.filter(Competition.participants.any(id=user_id)).all()
    ranking = Ranking.query.filter_by(student_id=user_id).first()

    ranking= ranking.curr_ranking
    
    return jsonify(student.curr_rank) 

@index_views.route('/api/moderator', methods=['POST'])
def create_moderator():
    data = request.json
    mod = create_moderator(data['username'], data['password'])
    if mod:
        return jsonify({'message': f"Moderator: {mod.username} created!"})
    else:
        return jsonify({'message': "Failed to create moderator!"})
"""       
"""
@index_views.route('/login')
def login():
    return render_template('login.html')

    
@index_views.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        create_student(request.form['username'], request.form['password'])
        return render_template('login.html')#, students=get_all_students())#,get_ranking=get_ranking,display_rankings=display_rankings,competitions=get_all_competitions())
    return render_template('signup.html')
"""

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
            comp = create_competition(competition['mod_name'], competition['comp_name'], competition['date'], competition['location'], competition['level'], competition['max_score'])
    
    competition_file.close()
    
    with open("results.csv") as results_file:
        reader = csv.DictReader(results_file)

        for result in reader:
            students = [result['student1'], result['student2'], result['student3']]
            team = add_team(result['mod_name'], result['comp_name'], result['team_name'], students)
            add_results(result['mod_name'], result['comp_name'], result['team_name'], int(result['score']))
            #db.session.add(comp)
        #db.session.commit()
    
    results_file.close()

    with open("competitions.csv") as competitions_file:
        reader = csv.DictReader(competitions_file)

        for competition in reader:
            update_ratings(competition['mod_name'], competition['comp_name'])
            update_rankings()
            #db.session.add(comp)
        #db.session.commit()
    
    competitions_file.close()

    return (jsonify({'message': "database_initialized"}),200)