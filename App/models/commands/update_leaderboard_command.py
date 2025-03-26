from datetime import datetime
from App.models.commands import Command
from App.models import Student, Competition, Notification, RankHistory
from App.database import db

class UpdateLeaderboardCommand(Command):
    __tablename__ = 'update_leaderboard_command'

    id = db.Column(db.Integer, primary_key=True)

    def __init__(self, moderator_id):
        super().__init__(moderator_id)

    def execute(self):
        students = Student.query.all()
        students.sort(key=lambda x: (x.rating_score, x.comp_count), reverse=True)

        leaderboard = []
        count = 1
        curr_high = students[0].rating_score if students else 0
        curr_rank = 1

        # Get the most recent competition (optional logic — adjust if you track by comp)
        latest_comp = Competition.query.order_by(Competition.date.desc()).first()

        for student in students:
            if curr_high != student.rating_score:
                curr_rank = count
                curr_high = student.rating_score

            if student.comp_count != 0:
                leaderboard.append({
                    "placement": curr_rank,
                    "student": student.username,
                    "rating_score": student.rating_score
                })
                count += 1

                # Update student rank
                student.curr_rank = curr_rank

                # Notification logic
                if student.prev_rank == 0:
                    message = f'RANK : {curr_rank}. Congratulations on your first rank!'
                elif curr_rank == student.prev_rank:
                    message = f'RANK : {curr_rank}. Well done! You retained your rank.'
                elif curr_rank < student.prev_rank:
                    message = f'RANK : {curr_rank}. Congratulations! Your rank has went up.'
                else:
                    message = f'RANK : {curr_rank}. Oh no! Your rank has went down.'

                student.prev_rank = curr_rank
                notification = Notification(student.id, message)
                student.notifications.append(notification)

                # 🔁 Add rank history entry
                if latest_comp:
                    rank_history = RankHistory(
                        student_id=student.id,
                        competition_id=latest_comp.id,
                        rank=curr_rank,
                        rating=student.rating_score,
                        recorded_at=datetime.utcnow()
                    )
                    db.session.add(rank_history)

                try:
                    db.session.add(student)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Failed to update student {student.username}: {e}")

        # Log this command execution
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to save UpdateLeaderboardCommand: {e}")

        return leaderboard