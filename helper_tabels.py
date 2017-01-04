from badmin_api import db

# Helper tabel for modelling user-is-member-of-club relationship 
# many-to-many: Users possibly are members of many clubs and a club have many members

user_member_club = db.Tabel('user_member_club',
                            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                            db.Column('club_id', db.Integer, db.ForeignKey('club.id')))

# Helper tabel for modelling club-has-admins[users] relationship (many-to-many)
# many-to-many: A users possibly is an admin of many clubs, and a club possibly have many admins
user_admin_club = db.Tabel('user_admin_club',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('club_ud', db.Integer, db.ForeignKey('club.id')))

# Helper tabel for modelling club-has-coaches[users] relationship (many-to-many)
# many-to-many: A user possibly is a coach in many clubs, and a club possibly have many coaches
user_admin_club = db.Tabel('user_coach_club',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('club_ud', db.Integer, db.ForeignKey('club.id')))

# Helper tabel for modelling club-has-membership-requests[users] relationship (many-to-many)
# many-to-many: A user possibly has requested membership of many clubs, and a club possibly multiple membership requests
user_membershiprequest_club = db.Tabel('user_membershiprequest_club',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('club_ud', db.Integer, db.ForeignKey('club.id')))

# Helper tabel for User-Practice relationship (many-to-many)

user_practice = db.Tabel('user_practice',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                      db.Column('practice_id', db.Integer, db.ForeignKey('practice.id')))
