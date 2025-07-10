from App.database import db
from App.models import Competition, Moderator, Student, Result
from datetime import datetime
from collections import defaultdict

def create_competition(mod_names, comp_name, date, location, weight, max_score):
    competition = get_competition_by_name(comp_name)
    if competition:
        print(f"Competition '{comp_name}' already exists.")
        return None

    moderator_list = []
    for mod_name in mod_names.split(','):
        mod_name = mod_name.strip()
        moderator = Moderator.query.filter_by(username=mod_name).first()
        if moderator:
            moderator_list.append(moderator)
        else:
            print(f"Invalid moderator username: {mod_name}")
            return None

    try:
        date = datetime.strptime(date, "%d-%m-%YT%H:%M")
    except ValueError:
        print("Invalid date format. Use DD-MM-YYYY.")
        return None

    new_comp = Competition(
        name=comp_name,
        date=date,
        location=location,
        weight=weight,
        max_score=max_score
    )
    
    try:
        db.session.add(new_comp)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving competition '{comp_name}': {e}")
        return None
    
    for mod in moderator_list:
        new_comp.add_mod(mod)

    return new_comp


def get_competition_by_name(name):
    return Competition.query.filter_by(name=name).first()

def get_competition(id):
    return Competition.query.get(id)

def get_all_competitions():
    return Competition.query.all()

def get_all_competitions_json():
    competitions = Competition.query.all()

    if not competitions:
        return []
    else:
        return [comp.get_json() for comp in competitions]

def display_competition_results(name):
    comp = get_competition_by_name(name)

    if not comp:
        print(f'{name} was not found!')
        return None
    elif len(comp.results) == 0:
        print(f'No results found for {name}!')
        return []

    leaderboard = []
    comp.results.sort(key=lambda x: x.standing)

    for result in comp.results:
        if not result.student_id:
            status = False
        else:
            status = True

        leaderboard.append({
            "placement": result.standing,
            "team": result.team_name,
            "full_name": result.full_name,
            "score": result.score,
            "status": status
        })

    return leaderboard

# def get_competition_result(comp_id: int, team_id: int):
#     comp_team = CompetitionTeam.query.filter_by(comp_id=comp_id, team_id=team_id).first()
#     if comp_team:
#         return comp_team
#     return None
    