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
            comp_team.rating_score = (score / comp.max_score) * 20 * comp.level
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
        print(f'{mod_name} was not found!')
        return None
    elif not comp:
        print(f'{comp_name} was not found!')
        return None
    elif comp.confirm:
        print(f'Results for {comp_name} have already been finalized!')
        return None
    elif mod not in comp.moderators:
        print(f'{mod_name} is not authorized to confirm results for {comp_name}!')
        return None
    elif len(comp.teams) == 0:
        print(f'No teams found. Results cannot be confirmed!')
        return None

    comp_teams = CompetitionTeam.query.filter_by(comp_id=comp.id).all()

    # Get average rating of each team
    team_ratings = {}
    for comp_team in comp_teams:
        team = Team.query.get(comp_team.team_id)
        if team and team.students:
            avg_rating = sum([s.rating_score for s in team.students]) / len(team.students)
            team_ratings[team.id] = avg_rating

    # Sort teams by score (descending)
    sorted_teams = sorted(comp_teams, key=lambda ct: ct.points_earned, reverse=True)

    # Perform pairwise Elo updates
    for i, comp_team in enumerate(sorted_teams):
        team = Team.query.get(comp_team.team_id)
        team_avg = team_ratings.get(team.id, 0)

        for j, other_team_ct in enumerate(sorted_teams):
            if i == j:
                continue

            other_team = Team.query.get(other_team_ct.team_id)
            opp_avg = team_ratings.get(other_team.id, 0)

            # actual score: 1 if this team ranked higher, 0 if lower
            actual_score = 1 if i < j else 0
            expected_score = 1 / (1 + 10 ** ((opp_avg - team_avg) / 400))

            for student in team.students:
                k = get_dynamic_k(student)
                delta = k * (actual_score - expected_score)
                student.rating_score = max(0, student.rating_score + delta)

    # Finalize: update comp_count and commit
    for comp_team in comp_teams:
        team = Team.query.get(comp_team.team_id)
        for student in team.students:
            student.comp_count += 1
            db.session.add(student)

    try:
        comp.confirm = True
        db.session.add(comp)
        db.session.commit()
        print("Results finalized with Elo rating updates.")
        return True
    except Exception as e:
        db.session.rollback()
        print("Failed to finalize results:", e)
        return None

# Run create competition via command
def create_competition_by_moderator(moderator_id, mod_name, comp_name, date, location, level, max_score):
    cmd = CreateCompetitionCommand(moderator_id)
    competition = cmd.execute(mod_name, comp_name, date, location, level, max_score)
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
