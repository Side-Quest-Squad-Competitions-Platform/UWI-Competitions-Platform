from App.database import db
from App.models import Moderator, Competition, Result, Student
from App.models.commands.create_competition_command import CreateCompetitionCommand
from App.models.commands.update_leaderboard_command import UpdateLeaderboardCommand
from collections import defaultdict

def create_moderator(username, password):
    mod = get_moderator_by_username(username)
    if mod:
        print(f'{username} already exists!')
        return None

    newMod = Moderator(username=username, password=password)
    try:
        db.session.add(newMod)
        db.session.commit()
        print(f'New Moderator: {username} created!')
        return newMod
    except Exception as e:
        db.session.rollback()
        print(f'Something went wrong creating {username}')
        return None

def get_moderator_by_username(username):
    return Moderator.query.filter_by(username=username).first()

def get_moderator(id):
    return Moderator.query.get(id)

def get_all_moderators():
    return Moderator.query.all()

def get_all_moderators_json():
    mods = Moderator.query.all()
    if not mods:
        return []
    mods_json = [mod.get_json() for mod in mods]
    return mods_json

def update_moderator(id, username):
    mod = get_moderator(id)
    if mod:
        mod.username = username
        try:
            db.session.add(mod)
            db.session.commit()
            print("Username was updated!")
            return mod
        except Exception as e:
            db.session.rollback()
            print("Username was not updated!")
            return None
    print("ID: {id} does not exist!")
    return None

def add_mod(mod1_name, comp_name, mod2_name):
    mod1 = Moderator.query.filter_by(username=mod1_name).first()
    comp = Competition.query.filter_by(name=comp_name).first()
    mod2 = Moderator.query.filter_by(username=mod2_name).first()

    if not mod1:
        print(f'Moderator: {mod1_name} not found!')
        return None
    elif not comp:
        print(f'Competition: {comp_name} not found!')
        return None
    elif not mod2:
        print(f'Moderator: {mod2_name} not found!')
        return None
    elif not mod1 in comp.moderators:
        print(f'{mod1_name} is not authorized to add results for {comp_name}!')
        return None
    else:
        return comp.add_mod(mod2)
                
def add_results(mod_names, comp_name, team_name, score):
    comp = Competition.query.filter_by(name=comp_name).first()
    teams = Team.query.filter_by(name=team_name).all()

    if not comp:
        print(f'{comp_name} was not found!')
        return None
    elif comp.confirm:
        print(f'Results for {comp_name} have already been finalized!')
        return None
    elif score > comp.max_score:
        print(f'Score {score} exceeds the maximum allowed score of {comp.max_score} for {comp_name}.')
        return None

    # Check if any moderator in mod_names is authorized
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

    for team in teams:
        comp_team = CompetitionTeam.query.filter_by(comp_id=comp.id, team_id=team.id).first()
        if comp_team:
            comp_team.points_earned = score
            comp_team.points = (score / comp.max_score) * 20 * comp.weight
            try:
                db.session.add(comp_team)
                db.session.commit()
                print(f'Score successfully added for {team_name}!')
                return comp_team
            except Exception as e:
                db.session.rollback()
                print("Something went wrong!")
                return None

    print(f'Team {team_name} not found in {comp_name}')
    return None


def update_ratings(mod_name, comp_name):
    mod = Moderator.query.filter_by(username=mod_name).first()
    comp = Competition.query.filter_by(name=comp_name).first()

    if not mod:
        print(f'{mod_name} not found.')
        return None
    if not comp:
        print(f'{comp_name} not found.')
        return None
    if comp.confirm:
        print(f'{comp_name} has already been finalized.')
        return None
    if mod not in comp.moderators:
        print(f'{mod_name} is not authorized to finalize {comp_name}.')
        return None

    results = Result.query.filter_by(comp_id=comp.id).all()
    if not results:
        print(f'No results found for {comp_name}.')
        return None

    winner_result = next((r for r in results if r.standing == 1), None)
    if not winner_result:
        print("No winner found (no standing == 1). Cannot compute ratios.")
        return None

    winner_score = winner_result.score
    comp_weight = comp.weight if comp.weight else 1

    updated_emails = set()
    for res in results:
        student = Student.query.filter_by(email=res.email).first()
        if not student:
            continue

        ratio = res.score / winner_score
        points = ratio * comp_weight

        student.points += points
        if student.email not in updated_emails:
            student.comp_count += 1
            updated_emails.add(student.email)

        db.session.add(student)
        db.session.add(res)

    try:
        comp.confirm = True
        db.session.add(comp)
        db.session.commit()
        print(f"Competition finalized and student points updated. - {comp.name}")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error finalizing results: {e}")
        return None

# Run create competition via command
def create_competition_by_moderator(moderator_id, mod_name, comp_name, date, location, weight, max_score):
    cmd = CreateCompetitionCommand(moderator_id)
    competition = cmd.execute(mod_name, comp_name, date, location, weight, max_score)
    if competition:
        return f"Competition '{competition.name}' created successfully"
    return "Failed to create competition"

def get_dynamic_k(student):
    # Example: lower K for experienced students
    if student.comp_count < 5:
        return 40
    elif student.comp_count < 10:
        return 30
    else:
        return 20
