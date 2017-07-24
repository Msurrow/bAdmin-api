from db_helper import db


class DeclineNotice(db.Model):

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)

    timestamp = db.Column(db.TIMESTAMP(timezone=False), unique=False, nullable=False)

    # Define one-to-many relationship with User: One user can have many
    # DeclineNotices, but a DeclineNotice only has one User.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Define one-to-many relationship with Practice: One Practice can have many
    # DeclineNotices, but a DeclineNotice only belongs to one Practice.
    practice_id = db.Column(db.Integer, db.ForeignKey('practice.id'))

    def __init__(self, timestamp):
        self.timestamp = timestamp
