from flask import jsonify
from flask_restful import Resource, reqparse, abort
import debug_code_generator
# Imports for serialization (marshmallow)
from serialization_schemas import ClubSchema
import user_model
import club_model
# Imports for DB connection
from sqlalchemy.exc import IntegrityError
from db_helper import db

# Resource for handling non-club-pecific actions on Club resource
class Clubs(Resource):

    def __init__(self):
        self.club_schema = ClubSchema()
        self.clubs_schema = ClubSchema(many=True)

    def get(self):
        # Get on club resource lists all clubs
        clubs = club_model.Club.query.filter(1==1).all()
        return jsonify(self.clubs_schema.dump(clubs).data)

    def post(self):
        self.args_parser = reqparse.RequestParser(bundle_errors=True)
        self.args_parser.add_argument('name', type=str, required=True, nullable=False, help="Attribute is required. Club name must be of type string and not null, and cannot be empty.")
        #self.args_parser.add_argument('admins', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club admin list must be of type list and not null, but can be empty.")
        #self.args_parser.add_argument('coaches', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club coaches list must be of type list and not null, but can be empty.")
        #self.args_parser.add_argument('membershipRequests', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club membershipRequests list must be of type list and not null, and all IDs must be IDs of existing users, but can be empty.")
        #self.args_parser.add_argument('members', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club members list must be of type list, and not null and all IDs must be IDs of existing users, but can be empty.")
        self.args_parser.add_argument('creatingUserID', type=int, required=True, nullable=False, help="Attribute is required. Creating user ID must be ID of existing user.")

        args = self.args_parser.parse_args(strict=True)

        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) <= 0:
                abort(400, message="Club name cannot be an empty string.")

        # Extra input validation: creatingUserID must be ID of existing user
        creatingUser = user_model.User.query.get(args['creatingUserID'])
        if creatingUser is None:
            abort(400, message="User with ID {} does not exist.".format(args['creatingUserID']))

        # Add the creatingUser as a club member and set creatingUser as admin
        # by default. Otherwise a club is created without any coaches or
        # membership requests.
        club = club_model.Club(args['name'], [creatingUser])
        club.members = [creatingUser]
        try:
            db.session.add(club)
            db.session.commit()
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            print("SQL IntegrityError happend in club_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            print(err)
            abort(400, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him in general!".format(debug_code))

        return jsonify(club_model.Club.dump(club).data)

# Resource for handling club-pecific actions on Club resource
class Club(Resource):

    def __init__(self):
        self.club_schema = ClubSchema()
        self.clubs_schema = ClubSchema(many=True)

    def get(self, clubID):
        # clubID type (must be int) is enforced by Flask-RESTful
        club = club_model.Club.query.get(clubID)
        if club is None:
            abort(404, message="Club with ID {} does not exist.".format(clubID))
        return jsonify(self.club_schema.dump(club).data)

    def put(self, clubID):
        # Set JSON args requirements in reqparser for this method.
        # ClubID is part of URL not args. Dont validate with args_parser.
        # clubID type is enforced by Flask-RESTful
        self.args_parser = reqparse.RequestParser(bundle_errors=True)
        self.args_parser.add_argument('name', type=str, required=False, nullable=False, help="Attribute is not required, but if provided club name must be of type string and not null, and cannot be empty.")
        self.args_parser.add_argument('admins', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club admin list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('coaches', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club coaches list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('membershipRequests', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club membershipRequests list must be of type list and not null, and all IDs must be IDs of existing users, but can be empty.")
        self.args_parser.add_argument('members', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club members list must be of type list, and not null and all IDs must be IDs of existing users, but can be empty.")

        # Validate args and get if valid. reqparser will throw nice HTTP 400's
        # at the caller if arguments are not validated.
        args = self.args_parser.parse_args(strict=True)

        # Get club object from DB
        club = club_model.Club.query.get(clubID)
        if club is None:
            abort(404, message="Club with ID {} does not exist.".format(clubID))

        # Do relative update: if the user attribute is part of the arguments
        # then update it, otherwise leave as is.

        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) > 0:
                club.name = args['name']
            else:
                abort(400, message="Club name cannot be an empty string.")

        if args['admins'] is not None:
            user_objects = []
            for userID in args['admins']:
                u = user_model.User.query.get(userID)
                if u is not None:
                    user_objects.append(u)
                # No 'else'-clause since Flask-restful input validation already
                # checked that all userIDs in input is actually IDs of existing
                # users.
            club.admins = user_objects

        if args['coaches'] is not None:
            user_objects = []
            for userID in args['coaches']:
                u = user_model.User.query.get(userID)
                if u is not None:
                    user_objects.append(u)
                # No 'else'-clause since Flask-restful input validation already
                # checked that all userIDs in input is actually IDs of existing
                # users.
            club.coaches = user_objects

        if args['membershipRequests'] is not None:
            user_objects = []
            for userID in args['membershipRequests']:
                u = user_model.User.query.get(userID)
                if u is not None:
                    user_objects.append(u)
                # No 'else'-clause since Flask-restful input validation already
                # checked that all userIDs in input is actually IDs of existing
                # users.
            club.membershipRequests = user_objects

        if args['members'] is not None:
            user_objects = []
            for userID in args['members']:
                u = user_model.User.query.get(userID)
                if u is not None:
                    user_objects.append(u)
                # No 'else'-clause since Flask-restful input validation already
                # checked that all userIDs in input is actually IDs of existing
                # users.
            club.members = user_objects

        try:
            db.session.commit()
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            print("SQL IntegrityError happend in user_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            print(err)
            abort(400, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.club_schema.Club.dump(club).data)

"""
CUSTOM VALIDATORS FOR REQPARSE / VALIDATING INPUT
"""
def _is_list_with_valid_userIDs(listUserIDs, name):
    lst = listUserIDs
    try:
        lst = list(listUserIDs)
        if isinstance(lst, str):
            raise ValueError("The parameter '{}' is of type string, and should be of type list. Input was: {}".format(name, lst))

        for userID in lst:
            u = user_model.User.query.get(userID)
            if u is None:
                raise ValueError("The parameter '{}' contains IDs that are not valid userIDs. Input was: {}".format(name, lst))

    except:
        raise ValueError("The parameter '{}' is not of type list. Input was: {}".format(name, listUserIDs))

    return lst
