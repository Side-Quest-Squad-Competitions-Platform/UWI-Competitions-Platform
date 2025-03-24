from App.models.commands import Command
from App.models import Student
from App.database import db

class UpdateLeaderboardCommand(Command):
    __tablename__ = 'update_leaderboard_command'

    id = db.Column(db.Integer, primary_key=True)

    def __init__(self, moderator_id):
        super().__init__(moderator_id)

    def execute(self):
        students = Student.query.order_by(Student.rating_score.desc()).all()

        for curr_rank, student in enumerate(students, start=1):
            student.prev_rank = student.curr_rank
            student.curr_rank = curr_rank

        db.session.add(self)
        db.session.commit()
        print("Leaderboard updated.")

    def get_json(self):
        return super().get_json()