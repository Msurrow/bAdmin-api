from datetime import datetime
from db_helper import db
from db_helper import user_invited_practice, user_confirmed_practice, user_declined_practice
from club_model import Club

class Practice(db.Model):
    __tabelname__ = "practice"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(500), unique=False, nullable=False)

    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    club = db.relationship('Club', backref=db.backref('practices'))

    startTime = db.Column(db.TIMESTAMP(timezone=False), unique=False, nullable=False)
    durationMinutes = db.Column(db.Integer, unique=False, nullable=False)
    invited = db.relationship('User', secondary=user_invited_practice, backref=db.backref('invitedPractices', lazy='joined'))
    confirmed = db.relationship('User', secondary=user_confirmed_practice, backref=db.backref('confirmedPractices', lazy='joined'))
    declined = db.relationship('User', secondary=user_declined_practice, backref=db.backref('declinedPractices', lazy='joined'))

    def __init__(self, name, club, startTime, durationMinutes):
        self.name = name

        if club is not None and isinstance(club, Club):
            self.club = club
        else:
            raise ValueError("Club argument must be of type Club and not null. Practice.init was passed {}".format(club))

        if startTime is not None and isinstance(startTime, datetime):
            self.startTime = startTime
        else:
            raise ValueError("StartTime argument must be of type DateTime and not null. Practice.init was passed {}".format(startTime))

        if durationMinutes is not None and isinstance(durationMinutes, int) and durationMinutes > 0:
            self.durationMinutes = durationMinutes
        else:
            raise ValueError("DurationMinutes argument must be of type int, not null and greater than 0. Practice.init was passed {}".format(startTime))