from App.database import db
from App.models.commands import Command
from App.controllers import create_competition

class CreateCompetitionCommand(Command):
    __tablename__ = 'create_competition_command'

    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'))

    def __init__(self, moderator_id):
        super().__init__(moderator_id)

    def execute(self, mod_names, comp_name, date, location, level, max_score):
        competition = create_competition(mod_names, comp_name, date, location, level, max_score)
        if competition:
            self.competition_id = competition.id
            db.session.add(self)
            db.session.commit()
            return competition
        return None

    def get_json(self):
        json = super().get_json()
        json.update({'competition_id': self.competition_id})
        return json
