from App.database import db
from App.models import Team, Competition, Student, Moderator, Notification

def create_team(team_name, students):
    team = Team(name=team_name)
    count = 0
    for s in students:
        stud = Student.query.filter_by(username=s).first()
        if stud:
            team.add_student(stud)
        else:
            count += 1
            print(f'{s} was not found!')
    
    if count == 3:
        return None
    else:
        try:
            db.session.add(team)
            db.session.commit()
            print(f'New Team: {team_name} created!')
            return team
        except Exception as e:
            db.session.rollback()
            print("Something went wrong!")
            return None

def get_team_by_name(name):
    return Team.query.filter_by(name=name).first()

def get_team(id):
    return Team.query.get(id)

def get_all_teams():
    return Team.query.all()

def get_all_teams_json():
    teams = Team.query.all()

    if not teams:
        return []
    else:
        return [team.get_json() for team in teams]
    
def find_team(team_name, students):
    teams = Team.query.filter_by(name=team_name).all()
    
    for team in teams:
        team_stud = []
        for stud in team.students:
            team_stud.append(stud.username)
        
        if set(team_stud) == set(students):
            return team

    return None

def add_team(mod_names, comp_name, team_name, students):
    comp = Competition.query.filter_by(name=comp_name).first()
    if not comp:
        print(f'Competition: {comp_name} not found!')
        return None
    elif comp.confirm:
        print(f'Results for {comp_name} have already been finalized!')
        return None

    authorized = False
    for mod_name in mod_names.split(','):
        mod_name = mod_name.strip()
        mod = Moderator.query.filter_by(username=mod_name).first()
        if mod and mod in comp.moderators:
            authorized = True
            break

    if not authorized:
        print(f'No authorized moderators found in {mod_names} for {comp_name}!')
        return None

    team = find_team(team_name, students)
    if team:
        return comp.add_team(team)

    comp_students = []
    for team in comp.teams:
        for stud in team.students:
            comp_students.append(stud.username)

    for stud in students:
        if stud in comp_students:
            print(f'{stud} is already registered for {comp_name}!')
            print('Team was not created!')
            return None

        team = create_team(team_name, students)
        
        if team:
            comp_team = comp.add_team(team)
            if comp_team:
                # After successfully adding the team, notify each student
                for stud in team.students:
                    message = f'You have been added to the competition: {comp.name}.'
                    notification = Notification(stud.id, message)
                    stud.add_notification(notification)
                return comp_team
            else:
                return None
        else:
            return None

"""
def add_results(mod_name, comp_name, team_name, students, score):
    add_team(mod_name, comp_name, team_name, students)
    
    mod = Moderator.query.filter_by(username=mod_name).first()
    comp = Competition.query.filter_by(name=comp_name).first()
    teams = Team.query.filter_by(name=team_name).all()

    if not mod:
        print(f'{mod_name} was not found!')
        return None
    else:
        if not comp:
            print(f'{comp_name} was not found!')
            return None
        elif comp.confirm:
            print(f'Results for {comp_name} have already been finalized!')
            return None
        elif mod not in comp.moderators:
            print(f'{mod_name} is not authorized to add results for {comp_name}!')
            return None
        else:
            for team in teams:
                comp_team = CompetitionTeam.query.filter_by(comp_id=comp.id, team_id=team.id).first()

                if comp_team:
                    comp_team.points_earned = score
                    comp_team.rating_score = (score/comp.max_score) * 20 * comp.level
                    try:
                        db.session.add(comp_team)
                        db.session.commit()
                        print(f'Score successfully added for {team_name}!')
                        return comp_team
                    except Exception as e:
                        db.session.rollback()
                        print("Something went wrong!")
                        return None
"""