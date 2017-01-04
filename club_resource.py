from flask import jsonify
from flask_restful import Resource, reqparse, abort

CLUBS = [{"id": 0, "name": "Andeby Badmintonklub", "admins": [], "coaches": [], "membershipRequests": [], "members": [0]}]

# Resource for handling non-club-pecific actions on Club resource
class Clubs(Resource):

    def get(self):
        # Get on club resource lists all users
        return jsonify(CLUBS)

    def post(self):
        # No ID required when creating club. Backedn will create ID.
        self.args_parser = reqparse.RequestParser(bundle_errors=True)
        self.args_parser.add_argument('name', type=str, required=True, nullable=False, help="Attribute is required. Club name must be of type string and not null, and cannot be empty.")
        self.args_parser.add_argument('admins', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club admin list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('coaches', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club coaches list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('membershipRequests', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club membershipRequests list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('members', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club members list must be of type list and not null, but can be empty.")

        args = self.args_parser.parse_args(strict=True)

        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) <= 0:
                abort(400, message="Club name cannot be an empty string.")

        CLUBS.append({"id": len(CLUBS)+1, "name": args['name'], "admin": args['admins'], "coaches": args['coaches'], "members": args['members'], "membershipRequests": args['membershipRequests']})
        return jsonify(args)

# Resource for handling club-pecific actions on Club resource
class Club(Resource):

    def get(self, clubID):
        # userID type (must be int) is enforced by Flask-RESTful
        return jsonify([club for club in CLUBS if club['id'] == clubID][0])

    def put(self, clubID):
        # Set JSON args requirements in reqparser for this method.
        # ClubID is part of URL not args. Dont validate with args_parser.
        # clubID type is enforced by Flask-RESTful
        self.args_parser = reqparse.RequestParser(bundle_errors=True)
        self.args_parser.add_argument('name', type=str, required=False, nullable=False, help="Attribute is not required, but if provided club name must be of type string and not null, and cannot be empty.")
        self.args_parser.add_argument('admins', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club admin list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('coaches', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club coaches list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('membershipRequests', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club membershipRequests list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('members', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided club members list must be of type list and not null, but can be empty.")

        # Validate args and get if valid. reqparser will throw nice HTTP 400's
        # at the caller if arguments are not validated.
        args = self.args_parser.parse_args(strict=True)

        # Get user object from DB
        club = [club for club in CLUBS if club['id'] == clubID][0]

        # Do relative update: if the user attribute is part of the arguments
        # then update it, otherwise leave as is.

        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) > 0:
                club['name'] = args['name']
            else:
                abort(400, message="Club name cannot be an empty string.")

        if args['admins'] is not None:
            club['admins'] = args['admins']

        if args['coaches'] is not None:
            club['coaches'] = args['coaches']

        if args['membershipRequests'] is not None:
            club['membershipRequests'] = args['membershipRequests']

        if args['members'] is not None:
            club['members'] = args['members']

        return jsonify(args)

"""
API USER RESOURCE HELPERS
"""
# Returns the club's members as a list of User objects
class ClubMembers(Resource):
    def get(self, clubID):
        abort(404, message="Not implemented yet")
# Returns the club's practices as a list of Practice objects
class ClubPractices(Resource):
    def get(self, clubID):
        abort(404, message="Not implemented yet")

"""
CUSTOM VALIDATORS FOR REQPARSE / VALIDATING INPUT
"""
def _is_list_with_valid_userIDs(listUserIDs, name):
    lst = listUserIDs
    try:
        lst = list(listUserIDs)
        if isinstance(listUserIDs, str):
            # Due to 'help' text in for the argument, the error text
            # doesn't get logged, so we print it
            print("The parameter '{}' is of type string, and should be of type list. Input was: {}".format(name, listUserIDs))
            raise ValueError()
        # TODO
        # if does_all_clubs_exist(lst):
            # raise ValueError("The parameter '{}' contains IDs that are not valid userIDs. Input was: {}".format(name, listUserIDs))
        pass
    except:
        raise ValueError("The parameter '{}' is not of type list. Input was: {}".format(name, listUserIDs))

    return lst