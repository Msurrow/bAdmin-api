from flask import jsonify, request
from flask_restful import Resource, abort
import debug_code_generator
import traceback
# Imports for input validation (marsmallow)
from validation_schemas import ClubValidationSchema
# Imports for serialization (marshmallow)
from serialization_schemas import ClubSchema
import user_model
import club_model
# Imports for DB connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from db_helper import db

# Resource for handling non-club-pecific actions on Club resource
class Clubs(Resource):

    def __init__(self):
        self.club_schema = ClubSchema()
        self.clubs_schema = ClubSchema(many=True)
        self.club_validation_schema = ClubValidationSchema()

    def get(self):
        # Get on club resource lists all clubs
        clubs = club_model.Club.query.filter(1==1).all()
        return jsonify(self.clubs_schema.dump(clubs).data)

    def post(self):
        # Input validation using Marshmallow.
        _, errors = self.club_validation_schema.load(request.json)
        if len(errors) > 0:
            abort(400, message="The reqeust input could bot be validated. There were the following validation errors: {}".format(errors))

        # Extra input validation: creatingUserID must be ID of existing user
        creatingUser = user_model.User.query.get(request.json['userID'])
        if creatingUser is None:
            abort(400, message="User with ID {} does not exist.".format(request.json['userID']))

        # Add the creatingUser as a club member and set creatingUser as admin
        # by default. Otherwise a club is created without any coaches or
        # membership requests. Club name input is validated by Marshmallow
        # schema.
        try:
            club = club_model.Club(request.json['name'], [creatingUser])
            club.members = [creatingUser]
        except ValueError as err:
            debug_code = debug_code_generator.gen_debug_code()
            print("ValueError happend in club_model.py (catched in club_resource.py). Debug code: {}. Stacktrace follows: ".format(debug_code))
            print(traceback.format_exc())
            print(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        try:
            db.session.add(club)
            db.session.commit()
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            print("SQL IntegrityError happend in club_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            print(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(club_model.dump(club).data)

# Resource for handling club-pecific actions on Club resource
class Club(Resource):

    def __init__(self):
        self.club_schema = ClubSchema()
        self.clubs_schema = ClubSchema(many=True)
        self.club_validation_schema = ClubValidationSchema()

    def get(self, clubID):
        # clubID type (must be int) is enforced by Flask-RESTful
        club = club_model.Club.query.get(clubID)
        if club is None:
            abort(404, message="Club with ID {} does not exist.".format(clubID))
        return jsonify(self.club_schema.dump(club).data)

    def put(self, clubID):
        # Input validation using Marshmallow. No parameter is actually required
        # in the PUT (update) request, since we do partical/relative update.
        # clubID type is enforced by Flask-RESTful
        _, errors = self.club_validation_schema.load(request.json, partial=('name',))
        if len(errors) > 0:
            abort(400, message="The reqeust input could bot be validated. There were the following validation errors: {}".format(errors))

        # Get club object from DB
        club = club_model.Club.query.get(clubID)
        if club is None:
            abort(404, message="Club with ID {} does not exist.".format(clubID))

        # Do relative update: if the attribute is part of the arguments
        # then update it, otherwise leave as is.
        # All input params are validated in Marshmallow schema.

        if 'name' in request.json:
            club.name = request.json['name']

        # Fecth all admins and add to club
        if 'admins' in request.json:
            user_objects = []
            for userID in request.json['admins']:
                u = user_model.User.query.get(userID)
                if u is not None:
                    user_objects.append(u)
            club.admins = user_objects

        # Fecth all coaches and add to club
        if 'coaches' in request.json:
            user_objects = []
            for userID in request.json['coaches']:
                u = user_model.User.query.get(userID)
                if u is not None:
                    user_objects.append(u)
            club.coaches = user_objects

        # Fecth all membersipRequest users and add to club
        if 'membershipRequests' in request.json:
            user_objects = []
            for userID in request.json['membershipRequests']:
                u = user_model.User.query.get(userID)
                if u is not None:
                    user_objects.append(u)
            club.membershipRequests = user_objects

        # Fecth all members and add to club
        if 'members' in request.json:
            user_objects = []
            for userID in request.json['members']:
                u = user_model.User.query.get(userID)
                if u is not None:
                    user_objects.append(u)
            club.members = user_objects

        try:
            db.session.commit()
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            print("SQL IntegrityError happend in user_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            print(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.club_schema.dump(club).data)

    def delete(self, practiceID):
        abort(501)
