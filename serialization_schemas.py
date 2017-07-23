from flask_marshmallow import Marshmallow
import user_model
import club_model
import practice_model
import decline_notice_model
import confirm_notice_model

ma = Marshmallow()


class DeclineNoticeSchema(ma.ModelSchema):
    class Meta:
        model = decline_notice_model.DeclineNotice

class ConfirmNoticeSchema(ma.ModelSchema):
    class Meta:
        model = confirm_notice_model.ConfirmNotice

class UserSchema(ma.ModelSchema):
    class Meta:
        model = user_model.User


class ClubSchema(ma.ModelSchema):
    class Meta:
        model = club_model.Club


class PracticeSchema(ma.ModelSchema):
    invited = ma.Nested(UserSchema, many=True)

    class Meta:
        model = practice_model.Practice
