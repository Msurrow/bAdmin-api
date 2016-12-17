from flask import jsonify
from flask_restful import Resource, reqparse, abort

USERS = [{"id":0, "name": "foobar", "email": "", "phone": 00000000, "clubs": [999,888], "practices": [0,1]}]

"""
User DB schema
User datatype:
{
    id: <int>, not null
    name: <string>, not null
    email: <string>, valid email
    phone: <int:8>, 8-digits valid DK phonenumber
    clubs: <list:int>, int must be id of existing club
    practices: <list:int>, int must be id of existing practice
}
"""

# Resource for handling non-user-pecific actions on User resource
# since Flask-RESTful doesn't know what RESTful is.
class Users(Resource):

    def get(self):
        # Get on user resource lists all users
        return jsonify(USERS)

    def post(self):
        # No ID required when creating user. Backedn will create ID.
        self.args_parser = reqparse.RequestParser()
        self.args_parser.add_argument('name', type=str, required=True, nullable=False, help="Attribute is required. Username must be of type string and not null, and cannot be empty.")
        self.args_parser.add_argument('email', type=str, required=True, nullable=False, help="Attribute is required. User email must be of type string and not null, and must be a valid email address.")
        self.args_parser.add_argument('phone', type=int, required=False, nullable=False, help="Attribute is not required, but if provided user phone must be of type int and not null, and must be a valid DK phonenumber.")
        self.args_parser.add_argument('clubs', type=list, required=False, nullable=False, help="Attribute is not required, but if provided user clubs list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('practices', type=list, required=False, nullable=False, help="Attribute is not required, but if provided user practices' list must be of type list and not null, but can be empty.")

        args = self.args_parser.parse_args(strict=True)

        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) <= 0:
                abort(400, message="User name cannot be an empty string.")

        # TODO: Validate user email is actually a valid email address
        # TODO: Validate user phone is actually a valid DK phone

        USERS.append({"id": len(USERS)+1, "name": args['name'], "clubs": args['clubs'], "email": args['email'], "phone": args['phone']})
        return jsonify(args)

# Resource for handling user-pecific actions on User resource
# since Flask-RESTful doesn't know what RESTful is.
class User(Resource):

    def get(self, userID):
        # userID type (must be int) is enforced by Flask-RESTful
        return jsonify([user for user in USERS if user['id'] == userID][0])

    def put(self, userID):
        # Set JSON args requirements in reqparser for this method.
        # UserID is part of URL not args. Dont validate with args_parser.
        # userID type is enforced by Flask-RESTful
        self.args_parser = reqparse.RequestParser()
        self.args_parser.add_argument('name', type=str, required=False, nullable=False, help="Attribute is not required, but if provided username must be of type string and not null, and cannot be empty.")
        self.args_parser.add_argument('email', type=str, required=False, nullable=False, help="Attribute is not required, but if provided user email must be of type string and not null, and must be a valid email address.")
        self.args_parser.add_argument('phone', type=int, required=False, nullable=False, help="Attribute is not required, but if provided user phone must be of type int and not null, and must be a valid DK phonenumber.")
        self.args_parser.add_argument('clubs', type=list, required=False, nullable=False, help="Attribute is not required, but if provided user clubs list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('practices', type=list, required=False, nullable=False, help="Attribute is not required, but if provided user practices' list must be of type list and not null, but can be empty.")

        # Validate args and get if valid. reqparser will throw nice HTTP 400's
        # at the caller if arguments are not validated.
        args = self.args_parser.parse_args(strict=True)

        # Get user object from DB
        user = [user for user in USERS if user['id'] == userID][0]

        # Do relative update: if the user attribute is part of the arguments
        # then update it, otherwise leave as is.

        # Update name attribute if in args.
        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) > 0:
                user['name'] = args['name']
            else:
                abort(400, message="User name cannot be an empty string.")

        # Update email attribute if in args
        # TODO: Validate sematically correct email
        if args['email'] is not None:
            user['email'] = args['email']

        # Update phone attribute if in args
        # TODO: Validate sematically correct DK phone
        if args['phone'] is not None:
            user['phone'] = args['phone']

        # Update user clubs list
        # Extra input validation: ClubIDs in user club list must match existing
        # clubIDs in database
        if args['clubs'] is not None:
            for clubID in args['clubs']:
                # TODO: Match against clubs in DB. Put does_club_exist(clubID)
                # method in DB layer
                if False:
                    abort(400, message="All clubIDs in user's clubs list must be IDs of existing clubs.")
                    break
            user['clubs'] = args['clubs']

        # Update user practices' list
        # Extra input validation: PracticeIDs in user practices' list must
        # match existing practiceIDs in database
        if args['practices'] is not None:
            for practiceID in args['practices']:
                # TODO: Match against clubs in DB. Put does_practice_exist(practiceID)
                # method in DB layer
                if False:
                    abort(400, message="All practiceIDs in user's practice list must be IDs of existing clubs.")
                    break
            user['practices'] = args['practices']

        return jsonify(args)

"""
API USER RESOURCE HELPERS
"""
# Returns the user's clubs as a list of Club objects
class UserClubs(Resource):
    def get(self, userID):
        abort(404, message="Not implemented yet")
# Returns the user's practices as a list of Practice objects
class UserPractices(Resource):
    def get(self, userID):
        abort(404, message="Not implemented yet")
