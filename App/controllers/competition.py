from App.database import db
from App.models import Competition, Moderator, CompetitionTeam, Team, Student#, Student, Admin, competition_student
from datetime import datetime

def create_competition(mod_name, comp_name, date, location, level, max_score):
    competition = get_competition_by_name(comp_name)
    if competition:
        print(f"Competition '{comp_name}' already exists.")
        return None

    moderator = Moderator.query.filter_by(username=mod_name).first()
    if not moderator:
        print("Invalid moderator username.")
        return None

    try:
        date = datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        print("Invalid date format. Use DD-MM-YYYY.")
        return None

    new_comp = Competition(
        name=comp_name,
        date=date,
        location=location,
        level=level,
        max_score=max_score
    )

    new_comp.add_mod(moderator)
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
    elif len(comp.teams) == 0:
        print(f'No teams found for {name}!')
        return []
    else:
        comp_teams = CompetitionTeam.query.filter_by(comp_id=comp.id).all()
        comp_teams.sort(key=lambda x: x.points_earned, reverse=True)

        leaderboard = []
        count = 1
        curr_high = comp_teams[0].points_earned
        curr_rank = 1
        
        for comp_team in comp_teams:
            if curr_high != comp_team.points_earned:
                curr_rank = count
                curr_high = comp_team.points_earned

            team = Team.query.filter_by(id=comp_team.team_id).first()
            leaderboard.append({"placement": curr_rank, "team": team.name, "members" : [student.username for student in team.students], "score":comp_team.points_earned})
            count += 1
        
        return leaderboard