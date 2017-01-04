from badmin_api import db
from helper_tabels import user_member_club, user_admin_club, user_coach_club, user_membershiprequest_club

"""
Club datatype:
{
    id: <int>, not null
    name: <string>, not null, unique
    members: <list:int>, int must be id of existing User
    admins: <list:int>, not empty, int must be id of existing User
    coaches: <list:int>, int must be id of existing User
    membershipRequests: <list:int, int must be id of existing User
}
"""

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullalbe=False)
    name = db.Column(db.String(500), unique=True, nullalbe=False)
    members = db.relationship('User', secondary=user_member_club, backref=db.backref('clubs', lazy='dynamic'))
    admins = db.relationship('User', secondary=user_admin_club, backref=db.backref('adminOfClubs', lazy='dynamic'))
    clubs = db.relationship('User', secondary=user_coach_club, backref=db.backref('coachInClubs', lazy='dynamic'))
    membershipRequests = db.relationship('User', secondary=user_membershiprequest_club, backref=db.backref('clubMembershipRequests', lazy='dynamic'))