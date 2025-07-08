from App.database import db
from datetime import datetime
from .competition_moderator import *

class Competition(db.Model):
    __tablename__='competition'

    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String, nullable=False, unique=True)
    date = db.Column(db.DateTime, default= datetime.utcnow)
    location = db.Column(db.String(120), nullable=False)
    weight = db.Column(db.Float, default=1)
    max_score = db.Column(db.Integer, default=25)
    confirm = db.Column(db.Boolean, default=False)
    moderators = db.relationship('Moderator', secondary="competition_moderator", overlaps='competitions', lazy=True)
    
    results = db.relationship('Result', overlaps='competitions', lazy=True)

    def __init__(self, name, date, location, weight, max_score):
        self.name = name
        self.date = date
        self.location = location
        self.weight = weight
        self.max_score = max_score
    
    def add_mod(self, mod):
        for m in self.moderators:
            if m.id == mod.id:
                return False, f"{mod.username} already added to {self.name}"

        try:
            comp_mod = CompetitionModerator(comp_id=self.id, mod_id=mod.id)
            self.moderators.append(mod)
            db.session.commit()
            return True, f"{mod.username} successfully added to {self.name}"
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to add moderator: {str(e)}"
        
    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "date": self.date.strftime("%d-%m-%Y"),
            "time": self.date.strftime("%I:%M %p"),
            "location": self.location,
            "weight" : self.weight,
            "max_score" : self.max_score,
            "moderators": [mod.username for mod in self.moderators],
        }

    def toDict(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "Date": self.date,
            "Location": self.location,
            "Weight" : self.weight,
            "Max Score" : self.max_score,
            "Moderators": [mod.username for mod in self.moderators],
        }

    def __repr__(self):
        return f'<Competition {self.id} : {self.name}>'