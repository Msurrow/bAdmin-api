from badmin_api import db

"""
User datatype:
{
    id: <int>, not null
    name: <string>, not null
    email: <string>, valid email, not null, unique
    phone: <int:8>, 8-digits valid DK phonenumber
    clubs: <list:int>, int must be id of existing club
    practices: <list:int>, int must be id of existing practice
}
"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(200), unique=False, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    phone = db.Column(db.Integer, unique=False, nullable=True)
    # 'clubs' attribute is defined in club_model
    # 'adminOfClubs' attribute is defined in club_model
    # 'coachInClubs' attribute is defined in club_model
    # 'clubMembershipRequests' attribute is defined in club_model
