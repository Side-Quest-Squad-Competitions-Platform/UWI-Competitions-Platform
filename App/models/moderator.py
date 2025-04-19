from App.database import db
from App.models import User

class Moderator(User):
    __tablename__ = 'moderator'

    competitions = db.relationship('Competition', secondary='competition_moderator', overlaps='moderators', lazy=True)

    def __init__(self, username, password):
        super().__init__(username, password)
        self.competitions = []

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username,
            'competitions': [comp.name for comp in self.competitions]
        }

    def toDict(self):
        return{
            'ID': self.id,
            'Username': self.username,
            'Competitions': [comp.name for comp in self.competitions]
        }

    def __repr__(self):
        return f'{self.id}'
