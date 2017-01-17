from flask import jsonify
from flask_restful import Resource, reqparse, abort
import dateutil.parser
import debug_code_generator
# Imports for serialization (marshmallow)
from serialization_schemas import PracticeSchema
import user_model
import club_model
import practice_model
# Imports for DB connection
from sqlalchemy.exc import IntegrityError
from db_helper import db

# Resource for handling non-practice-pecific actions on Practice resource
class Practices(Resource):

    def __init__(self):
        self.practice_schema = PracticeSchema()
        self.practices_schema = PracticeSchema(many=True)

    def get(self):
        # Get on practice resource lists all practices
        practices = club_model.Practice.query.filter(1==1).all()
        return jsonify(self.practice_schema.dump(practices).data)

    def post(self):
        # No ID required when creating club. Backedn will create ID.
        self.args_parser = reqparse.RequestParser(bundle_errors=True)
        self.args_parser.add_argument('club', type=int, required=True, nullable=False, help="Attribute is required. ClubID must be of type int and not null, and must be valid ID of existing club.")
        self.args_parser.add_argument('name', type=str, required=True, nullable=False, help="Attribute is required. Name must be of type string and not null, and not empty.")
        # The validator function will check for valid datatime and return a datetime object if valid
        self.args_parser.add_argument('startTime', type=_is_valid_datetime, required=True, nullable=False, help="Attribute is required. startTime must be of type datetime (ISO-format) and not null.")
        self.args_parser.add_argument('durationMinutes', type=int, required=True, nullable=False, help="Attribute is required. durationMinutes must be of type int, not null and > 0.")
        self.args_parser.add_argument('invited', type=list, required=False, nullable=False, help="Attribute is not required, but if provided invited list must be of type list and not null, but can be empty.")
        # Since this is a creation of a pracice (POST to /practice), no users
        # can be either confirmed of declined yet. Thus these are considered
        # empty
        #self.args_parser.add_argument('confirmed', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided confirmed list must be of type list and not null, but can be empty.")
        #self.args_parser.add_argument('declined', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided declined list must be of type list and not null, but can be empty.")

        args = self.args_parser.parse_args(strict=True)
        if not True:#_is_list_with_valid_userIDs(args['invited']):
            abort(400, message="The parameter '{}' is of type string, and should be of type list. Input was: {}".format('invited', args['invited']))

        # Ekstra input validation: clubID must be valid id of existing club
        club = club_model.Club.query.get(args['club'])
        if club is None:
            abort(400, message="Practice clubID must be ID of exiting club.")

        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) <= 0:
                abort(400, message="Practice name cannot be an empty string.")

        # Ekstra input validation: durationMinutes attribute cannot be less
        # than 1.
        if args['durationMinutes'] is not None:
            if int(args['durationMinutes']) <= 0:
                abort(400, message="durationMinutes cannot be less than 0.")

        # TODO: Validate starttime is not in the past

        practice = practice_model.Practice(args['name'], club, args['startTime'], args['durationMinutes'])

        # Fecth all invited users and add to practice
        if args['invited'] is not None:
            user_objects = []
            for userID in args['invited']:
                u = user_model.User.get(userID)
                if u is not None:
                    user_objects.append(u)
                # No 'else'-clause since Flask-restful input validation already
                # checked that all userIDs in input is actually IDs of existing
                # users.
            practice.invited = user_objects

        try:
            db.session.add(practice)
            db.session.commit()
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            print("SQL IntegrityError happend in practice_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            print(err)
            abort(400, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.practice_schema.dump(practice).data)

# Resource for handling practice-pecific actions on Practice resource
class Practice(Resource):

    def __init__(self):
        self.practice_schema = PracticeSchema()
        self.practices_schema = PracticeSchema(many=True)

    def get(self, practiceID):
        # practiceID type (must be int) is enforced by Flask-RESTful
        practice = practice_model.Practice.query.get(practiceID)
        if practice is None:
            abort(404, message="Practice with ID {} does not exist.".format(practiceID))
        return jsonify(self.practice_schema.dump(practice).data)

    def put(self, practiceID):
        # Set JSON args requirements in reqparser for this method.
        # UserID is part of URL not args. Dont validate with args_parser.
        # userID type is enforced by Flask-RESTful
        self.args_parser = reqparse.RequestParser(bundle_errors=True)
        self.args_parser.add_argument('club', type=int, required=False, nullable=False, help="Attribute is not required, but if provided ClubID must be of type int and not null, and must be valid ID of existing club.")
        self.args_parser.add_argument('name', type=str, required=False, nullable=False, help="Attribute is not required, but if provided Name must be of type string and not null, and not empty.")
        # The validator function will check for valid datatime and return a datetime object if valid
        self.args_parser.add_argument('starttime', type=_is_valid_datetime, required=False, nullable=False, help="Attribute is not required, but if provided startTime must be of type datetime (ISO-format) and not null.")
        self.args_parser.add_argument('durationMinutes', type=int, required=False, nullable=False, help="Attribute is not required, but if provided durationMinutes must be of type int, not null and > 0.")
        self.args_parser.add_argument('invited', type=list, required=False, nullable=False, help="Attribute is not required, but if provided invited list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('confirmed', type=list, required=False, nullable=False, help="Attribute is not required, but if provided confirmed list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('declined', type=list, required=False, nullable=False, help="Attribute is not required, but if provided declined list must be of type list and not null, but can be empty.")

        # Validate args and get if valid. reqparser will throw nice HTTP 400's
        # at the caller if arguments are not validated.
        args = self.args_parser.parse_args(strict=True)
        # if not _is_list_with_valid_userIDs(args['invited']):
        #     abort(400, message="The parameter '{}' is of type string, and should be of type list. Input was: {}".format('invited', args['invited']))
        # if not _is_list_with_valid_userIDs(args['confirmed']):
        #     abort(400, message="The parameter '{}' is of type string, and should be of type list. Input was: {}".format('confirmed', args['confirmed']))
        # if not _is_list_with_valid_userIDs(args['declined']):
        #     abort(400, message="The parameter '{}' is of type string, and should be of type list. Input was: {}".format('declined', args['declined']))

        # Get practice object from DB
        practice = practice_model.Practice.query.get(practiceID)
        if practice is None:
            abort(404, message="Practice with ID {} does not exist.".format(practiceID))

        # Do relative update: if the attribute is part of the arguments
        # then update it, otherwise leave as is.

        # Ekstra input validation: clubID must be valid id of existing club
        if args['club'] is not None:
            club = club_model.Club.query.get(args['club'])
            if club is None:
                abort(400, message="Practice clubID must be ID of exiting club.")
            else:
                practice.club = club

        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) <= 0:
                abort(400, message="Practice name cannot be an empty string.")
            else:
                practice.name = args['name']

        # TODO: Validate starttime is not int the past
        if args['startTime'] is not None:
            practice.startTime = args['startTime']

        # Ekstra input validation: durationMinutes attribute cannot be less
        # than 1.
        if args['durationMinutes'] is not None:
            if int(args['durationMinutes']) <= 0:
                abort(400, message="durationMinutes cannot be less than 0.")
            else:
                practice.durationMinutes = args['durationMinutes']

        # Fecth all invited users and add to practice
        if args['invited'] is not None:
            user_objects = []
            for userID in args['invited']:
                u = user_model.User.get(userID)
                if u is not None:
                    user_objects.append(u)
                # No 'else'-clause since Flask-restful input validation already
                # checked that all userIDs in input is actually IDs of existing
                # users.
            practice.invited = user_objects

        # Fecth all confirmed users and add to practice
        if args['confirmed'] is not None:
            user_objects = []
            for userID in args['confirmed']:
                u = user_model.User.get(userID)
                if u is not None:
                    user_objects.append(u)
                # No 'else'-clause since Flask-restful input validation already
                # checked that all userIDs in input is actually IDs of existing
                # users.
            practice.confirmed = user_objects

        # Fecth all declined users and add to practice
        if args['declined'] is not None:
            user_objects = []
            for userID in args['declined']:
                u = user_model.User.get(userID)
                if u is not None:
                    user_objects.append(u)
                # No 'else'-clause since Flask-restful input validation already
                # checked that all userIDs in input is actually IDs of existing
                # users.
            practice.declined = user_objects

        try:
            db.session.commit()
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            print("SQL IntegrityError happend in practice_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            print(err)
            abort(400, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.practice_schema.dump(practice).data)

    def delete(self, practiceID):
        abort(501)

"""
CUSTOM VALIDATORS FOR REQPARSE / VALIDATING INPUT
"""
def _is_valid_datetime(strDateTime, name):
    newStartTime = strDateTime
    if strDateTime is not None:
        # If the parser fails it raises a ValueError or OverflowError
        # and the flask-restfull validator will fail with the validator
        # error message.
        newStartTime = dateutil.parser.parse(strDateTime)
    return newStartTime
