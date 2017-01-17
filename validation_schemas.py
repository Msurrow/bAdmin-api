from marshmallow import Schema, fields, ValidationError, validate
import user_model

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

"""
Defintions of Marshmallow shcemas for validating JSON input.
"""


class GlobalSchema(Schema):
    userID = fields.Int(required=True)
    userAccessToken = fields.String(required=True)


class ClubValidationSchema(GlobalSchema):
    name = fields.String(required=True, validate=validate.Length(min=1, error="Club name cannot be an empty string."))
    admins = fields.List(fields.Int(), validate=_is_list_with_valid_userIDs)
    coaches = fields.List(fields.Int())
    membershipRequests = fields.List(fields.Int())
    members = fields.List(fields.Int())
