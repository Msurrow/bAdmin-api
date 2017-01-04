from db_helper import db
from db_helper import user_member_club, user_admin_club, user_coach_club, user_membershiprequest_club

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
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(500), unique=True, nullable=False)
    members = db.relationship('User', secondary=user_member_club, backref=db.backref('clubs', lazy='dynamic'))
    admins = db.relationship('User', secondary=user_admin_club, backref=db.backref('adminOfClubs', lazy='dynamic'))
    coaches = db.relationship('User', secondary=user_coach_club, backref=db.backref('coachInClubs', lazy='dynamic'))
    membershipRequests = db.relationship('User', secondary=user_membershiprequest_club, backref=db.backref('clubMembershipRequests', lazy='dynamic'))
    # 'practices' attribute/backref is defined in practice_model

    def __init__(self, name, listAdmins):
        self.name = name
        if listAdmins is not None and isinstance(listAdmins, list) and len(listAdmins) > 0:
            self.admins = listAdmins
        else:
            raise ValueError("List of admins must contain atleast one user object. Club.init was passed: {}".format(listAdmins))