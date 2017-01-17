from marshmallow import Schema, fields, ValidationError, validate
import user_model
import club_model
import practice_model

"""
Custom validators and helpers
"""


def _is_list_with_valid_userIDs(listUserIDs):
    lst = listUserIDs

    if isinstance(lst, str):
        raise ValidationError("The parameter is of type string, and should be of type list. Input was: {}".format(listUserIDs))

    lst = list(listUserIDs)
    for userID in lst:
        u = user_model.User.query.get(userID)
        if u is None:
            raise ValidationError("The parameter contains a ID that is not a valid userID. Input was: {}".format(listUserIDs))


def _is_list_with_valid_clubIDs(listClubIDs):
    lst = listClubIDs

    if isinstance(lst, str):
        raise ValidationError("The parameter is of type string, and should be of type list. Input was: {}".format(listClubIDs))

    lst = list(listClubIDs)
    for clubID in lst:
        u = club_model.Club.query.get(clubID)
        if u is None:
            raise ValidationError("The parameter contains a ID that is not a valid clubID. Input was: {}".format(listClubIDs))


def _is_list_with_valid_practiceIDs(listPracticeIDs):
    lst = listPracticeIDs

    if isinstance(lst, str):
        raise ValidationError("The parameter is of type string, and should be of type list. Input was: {}".format(listPracticeIDs))

    lst = list(listPracticeIDs)
    for practiceID in lst:
        u = practice_model.Practice.query.get(practiceID)
        if u is None:
            raise ValidationError("The parameter contains a ID that is not a valid practiceID. Input was: {}".format(listPracticeIDs))


def _is_valid_club_ID(clubID):
        club = club_model.Club.query.get(clubID)
        if club is None:
            raise ValidationError("Practice clubID must be ID of exiting club. Input was: {}".format(clubID))

"""
Defintions of Marshmallow shcemas for validating JSON input.
"""


class GlobalSchema(Schema):
    userID = fields.Int(required=True)
    userAccessToken = fields.String(required=True)


class ClubValidationSchema(GlobalSchema):
    name = fields.String(required=True, validate=validate.Length(min=1, error="Club name cannot be an empty string."))
    admins = fields.List(fields.Int(), validate=_is_list_with_valid_userIDs)
    coaches = fields.List(fields.Int(), validate=_is_list_with_valid_userIDs)
    membershipRequests = fields.List(fields.Int(), validate=_is_list_with_valid_userIDs)
    members = fields.List(fields.Int(), validate=_is_list_with_valid_userIDs)


class PracticeValidationSchema(GlobalSchema):
    club = fields.Int(required=True, validate=_is_valid_club_ID)
    name = fields.String(required=True, validate=validate.Length(min=1, error="Practice name cannot be an empty string."))
    startTime = fields.DateTime(required=True)
    durationMinutes = fields.Int(required=True, validate=validate.Range(min=1, max=1440, error="Practice duration must be at least one minute and less than one day (24hours)"))
    invited = fields.List(fields.Int(), validate=_is_list_with_valid_userIDs)


class UserValidationSchema(GlobalSchema):
    name = fields.String(required=True, validate=validate.Length(min=1, error="User name cannot be an empty string."))
    email = fields.Email(required=True)
    phone = fields.Int(validate=validate.Length(min=8, max=8, error="Phone number must be a valid DK phonenumber without area code (8 digits)"))
    clubs = fields.List(fields.Int(), validate=_is_list_with_valid_clubIDs)
    practices = fields.List(fields.Int(), validate=_is_list_with_valid_practiceIDs)
