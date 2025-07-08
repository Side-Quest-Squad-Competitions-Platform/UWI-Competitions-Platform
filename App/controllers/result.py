from App.database import db
from App.models import Competition, Moderator, CompetitionTeam, Student, Result #, Student, Admin, competition_student
from datetime import datetime

def add_result(comp_id, full_name, email, team_name, score):
    newResult = Result(comp_id=comp_id, full_name=full_name, email=email, team_name=team_name, score=score)
    try:
        db.session.add(newResult)
        db.session.commit()
        print(f"New Result: {team_name} - {full_name} - {score}")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error saving result for '{full_name}': {e}")
        return False

def add_results(results):
    for result in results:
        newResult = Result(comp_id=result['comp_id'], full_name=result['full_name'], email=result['email'], team_name=result['team_name'], score=result['score'])
        try:
            db.session.add(newResult)
            print(f"Added Result: {newResult}")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving result for '{result['full_name']}': {e}")
            return False
    try:
        db.session.commit()
        print("Results added successfully!")
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False

def get_results(comp_id, team_name):
    results = Result.query.filter_by(comp_id=comp_id, team_name=team_name).all()
    if results:
        return results
    else:
        return None