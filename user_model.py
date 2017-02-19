from db_helper import db
import os
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(500), unique=False, nullable=False)
    email = db.Column(db.String(500), unique=True, nullable=False)
    phone = db.Column(db.Integer, unique=False, nullable=True)
    hashed_password = db.Column(db.String(500), unique=False, nullable=True)
    # 'clubs' attribute/backref is defined in club_model
    # 'adminOfClubs' attribute/backref is defined in club_model
    # 'coachInClubs' attribute/backref is defined in club_model
    # 'clubMembershipRequests' attribute/backref is defined in club_model
    # 'invitedPractices'  attribute/backref is defined in practice_model
    # 'confirmedPractices'  attribute/backref is defined in practice_model
    # 'declinedPractices'  attribute/backref is defined in practice_model

    def __init__(self, name, email, phone, password):
        self.name = name
        self.email = email
        self.phone = phone
        self.hashed_password = self.hash_password(password)

    def hash_password(self, password):
        return pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.hashed_password)

    def generate_auth_token(self, expiration=86400):
        s = Serializer(os.environ['TOKEN_GEN_SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(os.environ['TOKEN_GEN_SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user
