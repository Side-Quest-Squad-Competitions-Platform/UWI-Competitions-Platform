from App.database import db
from datetime import datetime
from .competition_moderator import *

class Competition(db.Model):
    __tablename__='competition'

    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String, nullable=False, unique=True)
    date = db.Column(db.DateTime, default= datetime.utcnow)
    location = db.Column(db.String(120), nullable=False)
    level = db.Column(db.Float, default=1)
    max_score = db.Column(db.Integer, default=25)
    confirm = db.Column(db.Boolean, default=False)
    moderators = db.relationship('Moderator', secondary="competition_moderator", overlaps='competitions', lazy=True)
    
    results = db.relationship('Result', overlaps='competitions', lazy=True)

    def __init__(self, name, date, location, level, max_score):
        self.name = name
        self.date = date
        self.location = location
        self.level = level
        self.max_score = max_score
    
    def add_mod(self, mod):
        for m in self.moderators:
            if m.id == mod.id:
                return {
                "status": "error",
                "message": f"{mod.username} already added to {self.name}."
            }

        
        
        try:
            comp_mod = CompetitionModerator(comp_id=self.id, mod_id=mod.id)
            self.moderators.append(mod)
            db.session.commit()
            return {
            "status": "success",
            "message": f"{mod.username} was added to {self.name}.",
            "moderator": mod.username
        }
           
        except Exception as e:
            db.session.rollback()
            return {
            "status": "error",
            "message": f"Failed to add moderator: {str(e)}"
        }
            
    def add_team(self, team):
        for t in self.teams:
            if t.id == team.id:
                return {
                "status": "error",
                "message": f"{team.name} already registered for {self.name}."
            }
               
        try:
            comp_team = CompetitionTeam(comp_id=self.id, team_id=team.id)
            self.teams.append(team)
            team.competitions.append(self)
            db.session.commit()
            return {
            "status": "success",
            "message": f"{team.name} was added to {self.name}.",
            "team": team.name
            }
        
        except Exception as e:
            db.session.rollback()
            return {
            "status": "error",
            "message": f"Failed to add team: {str(e)}"
        }
        

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "date": self.date.strftime("%d-%m-%Y"),
            "time": self.date.strftime("%I:%M %p"),
            "location": self.location,
            "level" : self.level,
            "max_score" : self.max_score,
            "moderators": [mod.username for mod in self.moderators],
        }

    def toDict(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "Date": self.date,
            "Location": self.location,
            "Level" : self.level,
            "Max Score" : self.max_score,
            "Moderators": [mod.username for mod in self.moderators],
        }

    def __repr__(self):
        return f'<Competition {self.id} : {self.name}>'