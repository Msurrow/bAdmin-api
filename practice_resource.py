from flask import jsonify
from flask_restful import Resource, reqparse, abort
from datetime import datetime
from club_resource import _is_list_with_valid_userIDs

PRACTICES = [{"id": 0, "name": "A-træning", "club": 0, "startTime": "2016-12-24T12:00:00+13:00", "durationMinutes": 120, "invited": [], "confirmed": [], "rejected": []}]

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

# Resource for handling non-club-pecific actions on Club resource
class Practices(Resource):

    def get(self):
        # Get on club resource lists all users
        return jsonify(PRACTICES)

    def post(self):
        # No ID required when creating club. Backedn will create ID.
        self.args_parser = reqparse.RequestParser()
        self.args_parser.add_argument('club', type=int, required=True, nullable=False, help="Attribute is required. ClubID must be of type int and not null, and must be valid ID of existing club.")
        self.args_parser.add_argument('name', type=str, required=True, nullable=False, help="Attribute is required. Name must be of type string and not null, and not empty.")
        self.args_parser.add_argument('starttime', type=datetime, required=True, nullable=False, help="Attribute is required. startTime must be of type datetime (ISO-format) and not null.")
        self.args_parser.add_argument('durationMinutes', type=int, required=True, nullable=False, help="Attribute is required. durationMinutes must be of type int, not null and > 0.")
        self.args_parser.add_argument('invited', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided invited list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('accepted', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided accepted list must be of type list and not null, but can be empty.")
        self.args_parser.add_argument('rejected', type=_is_list_with_valid_userIDs, required=False, nullable=False, help="Attribute is not required, but if provided rejected list must be of type list and not null, but can be empty.")

        args = self.args_parser.parse_args(strict=True)

        # Ekstra input validation: Name attribute cannot be empty.
        if args['name'] is not None:
            if len(args['name']) <= 0:
                abort(400, message="User name cannot be an empty string.")

        # Ekstra input validation: durationMinutes attribute cannot be less than 1.
        if args['durationMinutes'] is not None:
            if int(args['durationMinutes']) <= 0:
                abort(400, message="durationMinutes cannot be less than 0.")

        PRACTICES.append({"id": len(PRACTICES)+1, "name": args['name'], "club": args['club'], "startTime": args['startTime'], "durationMinutes": args['durationMinutes'], "invited": args['invited'], "confirmed": args['confirmed'], "rejected": args['rejected']})
        return jsonify(args)