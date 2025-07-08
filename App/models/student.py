from App.database import db
from App.models import User

class Student(User):
    __tablename__ = 'student'

    email = db.Column(db.String(120), unique=False, nullable=False)
    fName = db.Column(db.String(120), unique=False, nullable=False)
    lName = db.Column(db.String(120), unique=False, nullable=False)
    rating_score = db.Column(db.Float, nullable=False, default=0)
    comp_count = db.Column(db.Integer, nullable=False, default=0)
    curr_rank = db.Column(db.Integer, nullable=False, default=0)
    prev_rank = db.Column(db.Integer, nullable=False, default=0)
    notifications = db.relationship('Notification', backref='student', lazy=True)

    def __init__(self, username, password, email, fName, lName):
        super().__init__(username, password)
        self.email = email
        self.fName = fName
        self.lName = lName
        self.rating_score = 0
        self.comp_count = 0
        self.curr_rank = 0
        self.prev_rank = 0
        self.notifications = []

    def add_notification(self, notification):
        if notification:
          try:
            self.notifications.append(notification)
            db.session.commit()
            return notification
          except Exception as e:
            db.session.rollback()
            return None
        return None

    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "rating_score": self.rating_score,
            "comp_count" : self.comp_count,
            "curr_rank" : self.curr_rank
        }

    def to_Dict(self):
        return {
            "ID": self.id,
            "Username": self.username,
            "Email": self.email,
            "Rating Score": self.rating_score,
            "Number of Competitions" : self.comp_count,
            "Rank" : self.curr_rank
        }

    def __repr__(self):
        return f'<Student {self.id} : {self.username}>'