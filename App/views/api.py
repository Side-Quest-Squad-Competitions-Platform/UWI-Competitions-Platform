from App.controllers.competition import create_competition, display_competition_results, get_all_competitions_json, get_competition, get_competition_by_name
from App.controllers.moderator import add_results
from App.controllers.student import get_student_by_username
from flask import Blueprint, jsonify, request, session
from flask_login import login_required, current_user
from App.controllers import display_rankings
from App.models.rank_history import RankHistory

api_views = Blueprint('api_views', __name__, url_prefix='/api')

@api_views.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    rankings = display_rankings()
    return jsonify(rankings)

@api_views.route('/student_profile/<string:name>', methods=['GET'])
def get_student_profile(name):
    student = get_student_by_username(name)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    profile_info = display_student_info(student.username)
    return jsonify(profile_info)

@api_views.route('/student/<int:student_id>/rank-history', methods=['GET'])
def get_rank_history(student_id):
    records = RankHistory.query.filter_by(student_id=student_id).order_by(RankHistory.recorded_at.asc()).all()
    
    history = [
        {
            "competition": record.competition.name if record.competition else "Unknown",
            "date": record.recorded_at.strftime("%Y-%m-%d") if record.recorded_at else "N/A",
            "timestamp": record.recorded_at.strftime("%Y-%m-%d %H:%M:%S") if record.recorded_at else "N/A",
            "rank": record.rank,
            "rating": record.rating
        }
        for record in records
    ]
    return jsonify(history)

@api_views.route('/competitions', methods=['GET'])
def get_competitions():
    competitions = get_all_competitions_json()
    return jsonify(competitions), 200

@api_views.route('/competitions', methods=['POST'])
def create_competition_api():
    data = request.json
    response = create_competition('robert', data['name'], data['date'], data['location'], data['weight'], data['max_score'])
    if response:
        return jsonify({'message': "Competition created!"}), 201
    return jsonify({'error': "Error creating competition"}), 500

@api_views.route('/competitions/<int:id>', methods=['GET'])
def competition_details_api(id):
    competition = get_competition(id)
    if not competition:
        return jsonify({'error': "Competition not found"}), 404
    # Optional: handle moderator logic if needed
    leaderboard = display_competition_results(competition.name)
    return jsonify(competition.toDict()), 200

# @api_views.route('/competitions/<string:comp_name>/results', methods=['POST'])
# def add_competition_results_api(comp_name):
#     competition = get_competition_by_name(comp_name)
#     data = request.json
#     students = [data['student1'], data['student2'], data['student3']]
#     response = add_team('robert', comp_name, data['team_name'], students)
#     if response:
#         response = add_results('robert', comp_name, data['team_name'], int(data['score']))
#     if response:
#         return jsonify({'message': "Results added successfully!"}), 201
#     return jsonify({'error': "Error adding results!"}), 500

@api_views.route('/notifications', methods=['GET'])
@login_required
def notifications_api():
    if session.get('user_type') == 'student':
        user_notifications = list(reversed(current_user.notifications))
    else:
        user_notifications = []
    
    notifications_list = [notification.get_json() for notification in user_notifications]
    return jsonify({"notifications": notifications_list}), 200
