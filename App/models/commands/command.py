from App.database import db
from abc import abstractmethod
from datetime import datetime

class Command(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    moderator_id = db.Column(db.String, db.ForeignKey('moderator.id'))
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, moderator_id):
        self.moderator_id = moderator_id
        self.executed_at = datetime.utcnow()

    @abstractmethod
    def execute(self):
        pass

    def get_json(self):
        return {
            'id': self.id,
            'moderator_id': self.moderator_id,
            'executed_at': self.executed_at.strftime("%Y-%m-%d %H:%M:%S")
        }
