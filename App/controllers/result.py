from App.database import db
from App.models import Competition, Moderator, Student, Result
from datetime import datetime

def add_result(comp_id, full_name, email, team_name, score, standing):
    from App.controllers.student import get_student_by_full_name, get_student_by_email

    student = get_student_by_email(email)
    if not student and full_name:
        get_student_by_full_name(full_name)
        
    newResult = Result(comp_id=comp_id, full_name=full_name, email=email, team_name=team_name, score=score, standing=standing)
    if student:
        newResult.student_id = student.id
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
    from App.controllers.student import get_student_by_full_name, get_student_by_email

    for result in results:
        student = get_student_by_email(result['email'])
        if not student and result.full_name:
            student = get_student_by_full_name(result['full_name'])

        newResult = Result(comp_id=result['comp_id'], full_name=result['full_name'], email=result['email'], team_name=result['team_name'], score=result['score'], standing=result['standing'])
        if student:
            newResult.student_id = student.id
        try:
            db.session.add(newResult)
            print(f"Added Result: {newResult}")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving result for '{result['full_name']}': {e}")
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
    
def get_results_by_student_id(student_id):
    results = Result.query.filter_by(student_id=student_id).all()
    if results:
        return results
    else:
        return None

def get_all_results():
    return Result.query.all()