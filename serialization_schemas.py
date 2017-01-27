from flask_marshmallow import Marshmallow
import user_model
import club_model
import practice_model

ma = Marshmallow()


class UserSchema(ma.ModelSchema):
    class Meta:
        model = user_model.User


class ClubSchema(ma.ModelSchema):
    class Meta:
        model = club_model.Club


class PracticeSchema(ma.ModelSchema):
    invited = ma.Nested(UserSchema, many=True)
    confirmed = ma.Nested(UserSchema, many=True)
    declined = ma.Nested(UserSchema, many=True)

    class Meta:
        model = practice_model.Practice
