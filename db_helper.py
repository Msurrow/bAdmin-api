from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


# Helper table for modelling user-is-member-of-club relationship 
# many-to-many: Users possibly are members of many clubs and a club have many members

user_member_club = db.Table('user_member_club',
                            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                            db.Column('club_id', db.Integer, db.ForeignKey('club.id')))

# Helper table for modelling club-has-admins[users] relationship (many-to-many)
# many-to-many: A users possibly is an admin of many clubs, and a club possibly have many admins
user_admin_club = db.Table('user_admin_club',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('club_id', db.Integer, db.ForeignKey('club.id')))

# Helper table for modelling club-has-coaches[users] relationship (many-to-many)
# many-to-many: A user possibly is a coach in many clubs, and a club possibly have many coaches
user_coach_club = db.Table('user_coach_club',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('club_id', db.Integer, db.ForeignKey('club.id')))

# Helper table for modelling club-has-membership-requests[users] relationship (many-to-many)
# many-to-many: A user possibly has requested membership of many clubs, and a club possibly multiple membership requests
user_membershiprequest_club = db.Table('user_membershiprequest_club',
                                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                       db.Column('club_id', db.Integer, db.ForeignKey('club.id')))

# Helper table for modelling practices-has-invitees relationship (many-to-many)
# many-to-many: A user can be invited to many practices and a pratice have many invitees
user_invited_practice = db.Table('user_invited_practice',
                                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                 db.Column('practice_id', db.Integer, db.ForeignKey('practice.id')))

# Helper table for modelling practices-has-confirmed-attendants relationship (many-to-many)
# many-to-many: A user can have confirmed many practices and a pratice have many confirmed users
user_confirmed_practice = db.Table('user_confirmed_practice',
                                   db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                   db.Column('practice_id', db.Integer, db.ForeignKey('practice.id')))

# Helper table for modelling practices-has-declined-attendants relationship (many-to-many)
# many-to-many: A user can have declined many practices and a pratice have many declined users
user_declined_practice = db.Table('user_declined_practice',
                                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                  db.Column('practice_id', db.Integer, db.ForeignKey('practice.id')))