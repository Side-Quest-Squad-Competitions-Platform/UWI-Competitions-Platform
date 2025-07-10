from App.database import db

class Result(db.Model):
    __tablename__ = 'result'

    result_id = db.Column(db.Integer, primary_key=True)
    comp_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=False)
    team_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    standing = db.Column(db.Integer, nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)
    student = db.relationship("Student", backref="results", lazy=True)


    def __init__(self, comp_id, full_name, email, team_name, score, standing):
        self.comp_id = comp_id
        self.full_name = full_name
        self.email = email
        self.team_name = team_name
        self.score = score
        self.standing = standing
    
    def get_json(self):
        return {
            'result_id': self.result_id,
            'comp_id': self.comp_id,
            'fName': self.fName,
            'lName': self.lName,
            'email': self.email,
            'team_name': self.team_name,
            'score': self.score,
            'standing': self.standing,
            'student_id': self.student_id
        }
    
    def to_dict(self):
        return {
            'Result ID': self.result_id,
            'Competition ID': self.comp_id,
            'First Name': self.fName,
            'Last Name': self.lName,
            'Email': self.email,
            'Team Name': self.team_name,
            'Score': self.score,
            'Standing': self.standing,
            'Student ID': self.student_id
        }