from App.database import db
from App.models import Moderator, Competition, Team, CompetitionTeam
from App.models.commands.create_competition_command import CreateCompetitionCommand
from App.models.commands.update_leaderboard_command import UpdateLeaderboardCommand

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
                
def add_results(mod_name, comp_name, team_name, score):
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
    return None


def update_ratings(mod_name, comp_name):
    mod = Moderator.query.filter_by(username=mod_name).first()
    comp = Competition.query.filter_by(name=comp_name).first()

    if not mod:
        print(f'{mod_name} was not found!')
        return None
    elif not comp:
        print(f'{comp_name} was not found!')
        return None
    elif comp.confirm:
        print(f'Results for {comp_name} has already been finalized!')
        return None
    elif mod not in comp.moderators:
        print(f'{mod_name} is not authorized to add results for {comp_name}!')
        return None
    elif len(comp.teams) == 0:
        print(f'No teams found. Results can not be confirmed!')
        return None
    else:
        comp_teams = CompetitionTeam.query.filter_by(comp_id=comp.id).all()

        for comp_team in comp_teams:
            team = Team.query.filter_by(id=comp_team.team_id).first()

            for stud in team.students:
                stud.rating_score = (stud.rating_score*stud.comp_count + comp_team.rating_score)/(stud.comp_count+1)
                stud.comp_count += 1
                try:
                    db.session.add(stud)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()

        comp.confirm = True
        print("Results finalized!")
        return True

# Run create competition via command
def create_competition_by_moderator(moderator_id, mod_name, comp_name, date, location, level, max_score):
    cmd = CreateCompetitionCommand(moderator_id)
    competition = cmd.execute(mod_name, comp_name, date, location, level, max_score)
    if competition:
        return f"Competition '{competition.name}' created successfully"
    return "Failed to create competition"
