from App.database import db
from datetime import datetime

class RankHistory(db.Model):
    __tablename__ = 'rank_history'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', backref='rank_history')
    competition = db.relationship('Competition')

    def __init__(self, student_id, competition_id, rank, rating, recorded_at):
        self.student_id = student_id
        self.competition_id = competition_id
        self.rank = rank
        self.rating = rating
        self.recorded_at = recorded_at