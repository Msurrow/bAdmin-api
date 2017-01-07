from flask import jsonify
from flask_restful import Resource, reqparse, abort
import debug_code_generator
# Imports for serialization (marshmallow)
from serialization_schemas import UserSchema
import user_model
import club_model
import practice_model
# Imports for DB connection
from sqlalchemy.exc import IntegrityError
from db_helper import db

"""
Resources
"""
# Resource for handling non-user-pecific actions on User resource
class Users(Resource):

    def __init__(self):
        self.user_schema = UserSchema()
        self.users_schema = UserSchema(many=True)

    def get(self):
        # Get on user resource lists all users
        users = user_model.User.query.filter(1==1).all()
        return jsonify(self.users_schema.dump(users).data)

    def post(self):
        # No ID required when creating user. Backedn will create ID.
        self.args_parser = reqparse.RequestParser(bundle_errors=True)
        self.args_parser.add_argument('name', type=str, location='json', required=True, nullable=False, help="Attribute is required. Username must be of type string and not null, and cannot be empty.")
        self.args_parser.add_argument('email', type=str, location='json', required=True, nullable=False, help="Attribute is required. User email must be of type string and not null, and must be a valid email address.")
        self.args_parser.add_argument('phone', type=int, location='json', required=False, nullable=False, help="Attribute is not required, but if provided user phone must be of type int and not null, and must be a valid DK phonenumber.")
        self.args_parser.add_argument('clubs', type=_is_list_with_valid_clubs, location='json', required=False, nullable=False, help="Attribute is not required, but if provided user clubs list must be of type list, not null and all IDs must be IDs of existing clubs, but can be empty.")
        self.args_parser.add_argument('practices', type=_is_list_with_valid_practices, location='json', required=False, nullable=False, help="Attribute is not required, but if provided user practices' list must be of type list and not null, but can be empty.")

        args = self.args_parser.parse_args(strict=True)

        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) <= 0:
                abort(400, message="User name cannot be an empty string.")

        # TODO: Validate user email is actually a valid email address
        # TODO: Validate user phone is actually a valid DK phone

        user = user_model.User(args['name'], args['email'], args['phone'])
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            print("SQL IntegrityError happend in user_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            print(err)
            abort(400, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.user_schema.dump(user).data)

# Resource for handling user-pecific actions on User resource
class User(Resource):

    def __init__(self):
        self.user_schema = UserSchema()
        self.users_schema = UserSchema(many=True)

    def get(self, userID):
        # userID type (must be int) is enforced by Flask-RESTful
        user = user_model.User.query.get(userID)
        if user is None:
            abort(404, message="User with ID {} does not exist.".format(userID))
        return jsonify(self.user_schema.dump(user).data)

    def put(self, userID):
        # Set JSON args requirements in reqparser for this method.
        # UserID is part of URL not args. Dont validate with args_parser.
        # userID type is enforced by Flask-RESTful
        self.args_parser = reqparse.RequestParser(bundle_errors=True)
        self.args_parser.add_argument('name', type=str, required=False, nullable=False, help="Attribute is not required, but if provided username must be of type string and not null, and cannot be empty.")
        self.args_parser.add_argument('email', type=str, required=False, nullable=False, help="Attribute is not required, but if provided user email must be of type string and not null, and must be a valid email address.")
        self.args_parser.add_argument('phone', type=int, required=False, nullable=False, help="Attribute is not required, but if provided user phone must be of type int and not null, and must be a valid DK phonenumber.")
        self.args_parser.add_argument('clubs', type=_is_list_with_valid_clubs, location='json', required=False, nullable=False, help="Attribute is not required, but if provided user clubs list must be of type list, not null and all IDs must be IDs of existing clubs, but can be empty.")
        self.args_parser.add_argument('practices', type=_is_list_with_valid_practices, required=False, nullable=False, help="Attribute is not required, but if provided user practices' list must be of type list and not null, but can be empty.")

        # Validate args and get if valid. reqparser will throw nice HTTP 400's
        # at the caller if arguments are not validated.
        args = self.args_parser.parse_args(strict=True)

        # Get user object from DB
        user = user_model.User.query.get(userID)
        if user is None:
            abort(404, message="User with ID {} does not exist.".format(userID))

        # Do relative update: if the attribute is part of the arguments
        # then update it, otherwise leave as is.

        # Update name attribute if in args.
        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) > 0:
                user.name = args['name']
            else:
                abort(400, message="User name cannot be an empty string.")

        # Update email attribute if in args
        # TODO: Validate sematically correct email
        if args['email'] is not None:
            user.email = args['email']

        # Update phone attribute if in args
        # TODO: Validate sematically correct DK phone
        if args['phone'] is not None:
            user.phone = args['phone']

        # Update user clubs list
        if args['clubs'] is not None:
            club_objects = []
            for clubID in args['clubs']:
                c = club_model.Club.query.get(clubID)
                if c is not None:
                    club_objects.append(c)
                # No 'else'-clause since Flask-restful input validation already
                # checked that all clubIDs in input is actually IDs of existing
                # clubs.
            user.clubs = club_objects

        # Update user practices' list
        if args['practices'] is not None:
            practice_objects = []
            for practiceID in args['practice']:
                c = practice_model.Practice.query.get(practiceID)
                if c is not None:
                    practice_objects.append(c)
                # No 'else'-clause since Flask-restful input validation already
                # checked that all practiceIDs in input is actually IDs of
                # existing clubs.
            user.clubs = practice_objects

        try:
            db.session.commit()
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            print("SQL IntegrityError happend in user_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            print(err)
            abort(400, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.user_schema.dump(user).data)

"""
CUSTOM VALIDATORS FOR REQPARSE / VALIDATING INPUT
"""
def _is_list_with_valid_clubs(listClubIDs, name):
    lst = listClubIDs
    try:
        lst = list(listClubIDs)
        if isinstance(lst, str):
            raise ValueError("The parameter '{}' is of type string, and should be of type list. Input was: {}".format(name, lst))

        for clubID in lst:
            c = club_model.Club.query.get(clubID)
            if c is None:
                raise ValueError("The parameter '{}' contains IDs that are not valid clubIDs. Input was: {}".format(name, lst))

    except:
        raise ValueError("The parameter '{}' is not of type list. Input was: {}".format(name, listClubIDs))

    return lst

def _is_list_with_valid_practices(listPracticeIDs, name):
    lst = listPracticeIDs
    try:
        lst = list(listPracticeIDs)
        if isinstance(listPracticeIDs, str):
            # Due to 'help' text in for the argument, the error text
            # doesn't get logged, so we print it
            print("The parameter '{}' is of type string, and should be of type list. Input was: {}".format(name, listPracticeIDs))
            raise ValueError()

        for practiceID in lst:
            p = practice_model.Club.query.get(practiceID)
            if p is None:
                raise ValueError("The parameter '{}' contains IDs that are not valid practiceIDs. Input was: {}".format(name, lst))

    except:
        raise ValueError("The parameter '{}' is not of type list. Input was: {}".format(name, listPracticeIDs))

    return lst