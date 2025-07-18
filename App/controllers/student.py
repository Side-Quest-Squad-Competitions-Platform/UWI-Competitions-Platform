from App.database import db
from App.models import Student, Competition, Notification
from App.controllers.result import get_results_by_student_id
from App.controllers.competition import get_competition

def create_student(username, password, fName, lName, email):
    student = get_student_by_username(username)
    if student:
        print(f'{username} already exists!')
        return None

    newStudent = Student(username=username, password=password, fName=fName, lName=lName, email=email)
    try:
        db.session.add(newStudent)
        db.session.commit()
        print(f'New Student: {username} created!')
        return newStudent
    except Exception as e:
        db.session.rollback()
        print(f'Something went wrong creating {username}: {e}')
        return None

def get_student_by_username(username):
    return Student.query.filter_by(username=username).first()

def get_student_by_full_name(full_name):
    parts = full_name.strip().split(" ", 1)
    fName = parts[0]
    lName = parts[1] if len(parts) > 1 else ""
    return Student.query.filter_by(fName=fName, lName=lName).first()

def get_student_by_email(email):
    return Student.query.filter_by(email=email).first()

def get_student(id):
    return Student.query.get(id)

def get_all_students():
    return Student.query.all()

def get_all_students_json():
    students = Student.query.all()
    if not students:
        return []
    students_json = [student.get_json() for student in students]
    return students_json

def update_student(id, username):
    student = get_student(id)
    if student:
        student.username = username
        try:
            db.session.add(student)
            db.session.commit()
            print("Username was updated!")
            return student
        except Exception as e:
            db.session.rollback()
            print("Username was not updated!")
            return None
    print("ID: {id} does not exist!")
    return None

def display_student_info(username):
    student = get_student_by_username(username)

    if not student:
        print(f'{username} does not exist!')
        return None
    else:
        competitions = []

        results = get_results_by_student_id(student.id)
        for result in results:
            competitions.append(get_competition(result.comp_id))
        
        profile_info = {
            "profile" : student.get_json(),
            "competitions" : competitions
        }

        return profile_info

def display_notifications(username):
    student = get_student_by_username(username)

    if not student:
        print(f'{username} does not exist!')
        return None
    else:
        return {"notifications":[notification.to_Dict() for notification in student.notifications]}

def display_rankings():
    students = get_all_students()

    students.sort(key=lambda x: (x.points, x.comp_count), reverse=True)

    leaderboard = []
    count = 1
    curr_high = students[0].points
    curr_rank = 1
        
    for student in students:
        if curr_high != student.points:
            curr_rank = count
            curr_high = student.points

        if student.comp_count != 0:
            leaderboard.append({"placement": curr_rank, "student": student.username, "rating score":student.points})
            count += 1

    # print("Rank\tStudent\tRating Score")

    # for position in leaderboard:
    #     print(f'{position["placement"]}\t{position["student"]}\t{position["rating score"]}')
    
    return leaderboard