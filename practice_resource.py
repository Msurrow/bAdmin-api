from flask import jsonify
from flask_restful import Resource, reqparse, abort
from datetime import datetime
from club_resource import _is_list_with_valid_userIDs

PRACTICES = [{"id": 0, "name": "A-træning", "club": 0, "startTime": "2016-12-24T12:00:00+13:00", "durationMinutes": 120, "invited": [], "accepted": [], "rejected": []}]

"""
Practices datatype:
{
    id: <int>, not null
    name: <string>, not null not empty
    club: <int>, not null club must be id of existing club
    startTime: <datetime>, not null
    durationMinutes: <int>, int must be >0
    invited: <list:int>, ints must be id of existing user
    accepted: <list:int>, ints must be id of existing user
    rejected: <list:ing>, ints must be id of existing user
}
"""

# Resource for handling non-practice-pecific actions on Practice resource
class Practices(Resource):

    def get(self):
        # Get on club resource lists all users
        return jsonify(PRACTICES)

    def post(self):
        # No ID required when creating club. Backedn will create ID.
        self.args_parser = reqparse.RequestParser(bundle_errors=True)
        self.args_parser.add_argument('club', type=int, required=True, nullable=False, help="Attribute is required. ClubID must be of type int and not null, and must be valid ID of existing club.")
        self.args_parser.add_argument('name', type=str, required=True, nullable=False, help="Attribute is required. Name must be of type string and not null, and not empty.")
        self.args_parser.add_argument('startTime', type=str, required=True, nullable=False, help="Attribute is required. startTime must be of type datetime (ISO-format) and not null.")
        self.args_parser.add_argument('durationMinutes', type=int, required=True, nullable=False, help="Attribute is required. durationMinutes must be of type int, not null and > 0.")
        self.args_parser.add_argument('invited', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided invited list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('accepted', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided accepted list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('rejected', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided rejected list must be of type list and not null, but can be empty.")

        args = self.args_parser.parse_args(strict=True)

        # Ekstra input validation: clubID must be valid id of existing club
        try:
            # Reuse already existing validator
            # (parse argument as list)
            _is_list_with_valid_userIDs([args['club']], "club")

        except ValueError:
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

        # TODO: Validate tarttime is not int the past

        PRACTICES.append({"id": len(PRACTICES)+1, "name": args['name'], "club": args['club'], "startTime": args['startTime'], "durationMinutes": args['durationMinutes'], "invited": (args['invited'] if args['invited'] is not None else []), "accepted": (args['accepted'] if args['accepted'] is not None else []), "rejected": (args['rejected'] if args['rejected'] is not None else [])})
        return jsonify(args)

# Resource for handling practice-pecific actions on Practice resource
class Practice(Resource):

    def get(self, practiceID):
        # userID type (must be int) is enforced by Flask-RESTful
        return jsonify([practice for practice in PRACTICES if practice['id'] == practiceID][0])

    def put(self, practiceID):
        # Set JSON args requirements in reqparser for this method.
        # UserID is part of URL not args. Dont validate with args_parser.
        # userID type is enforced by Flask-RESTful
        self.args_parser = reqparse.RequestParser(bundle_errors=True)
        self.args_parser.add_argument('club', type=int, required=False, nullable=False, help="Attribute is not required, but if provided ClubID must be of type int and not null, and must be valid ID of existing club.")
        self.args_parser.add_argument('name', type=str, required=False, nullable=False, help="Attribute is not required, but if provided Name must be of type string and not null, and not empty.")
        self.args_parser.add_argument('starttime', type=datetime, required=False, nullable=False, help="Attribute is not required, but if provided startTime must be of type datetime (ISO-format) and not null.")
        self.args_parser.add_argument('durationMinutes', type=int, required=False, nullable=False, help="Attribute is not required, but if provided durationMinutes must be of type int, not null and > 0.")
        self.args_parser.add_argument('invited', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided invited list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('accepted', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided accepted list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('rejected', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided rejected list must be of type list and not null, but can be empty.")

        # Validate args and get if valid. reqparser will throw nice HTTP 400's
        # at the caller if arguments are not validated.
        args = self.args_parser.parse_args(strict=True)

        # Get user object from DB
        practice = [practice for practice in PRACTICES if practice['id'] == practiceID][0]

        # Do relative update: if the user attribute is part of the arguments
        # then update it, otherwise leave as is.

        # Ekstra input validation: clubID must be valid id of existing club
        if args['club'] is not None:
            try:
                # Reuse already existing validator
                # (parse argument as list)
                _is_list_with_valid_userIDs([args['club']])

                practice['club'] = args['club']
            except ValueError:
                abort(400, message="Practice clubID must be ID of exiting club.")

        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) <= 0:
                abort(400, message="Practice name cannot be an empty string.")
            else:
                practice['name'] = args['name']

        # Ekstra input validation: durationMinutes attribute cannot be less
        # than 1.
        if args['durationMinutes'] is not None:
            if int(args['durationMinutes']) <= 0:
                abort(400, message="durationMinutes cannot be less than 0.")
            else:
                practice['durationMinutes'] = args['durationMinutes']

        # TODO: Validate starttime is not int the past

        if args['invited'] is not None:
            practice['invited'] = args['invited']

        if args['accepted'] is not None:
            practice['accepted'] = args['accepted']

        if args['rejected'] is not None:
            practice['rejected'] = args['rejected']

        return jsonify(args)

    def delete(self, practiceID):
        abort(501)