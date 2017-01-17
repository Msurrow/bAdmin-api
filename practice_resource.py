from flask import jsonify
from flask_restful import Resource, abort, request
import debug_code_generator
import dateutil.parser
# Imports for input validation (marsmallow)
from validation_schemas import PracticeValidationSchema
# Imports for serialization (flask-marshmallow)
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
        self.practice_validation_schema = PracticeValidationSchema()

    def get(self):
        # Get on practice resource lists all practices
        practices = club_model.Practice.query.filter(1==1).all()
        return jsonify(self.practice_schema.dump(practices).data)

    def post(self):
        # Input validation using Marshmallow.
        _, errors = self.practice_validation_schema.load(request.json)
        if len(errors) > 0:
            abort(400, message="The reqeust input could bot be validated. There were the following validation errors: {}".format(errors))

        # TODO: Validate starttime is not in the past

        # All request.json input parameters are validated by Marshmallow
        # schema.
        club = club_model.Club.query.get(request.json['club'])
        practice = practice_model.Practice(request.json['name'], club, request.json['startTime'], request.json['durationMinutes'])

        # Fecth all invited users and add to practice
        if 'invited' in request.json:
            user_objects = []
            for userID in request.json['invited']:
                u = user_model.User.get(userID)
                if u is not None:
                    user_objects.append(u)
            practice.invited = user_objects
        else:
            practice.invited = []

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
        self.practice_validation_schema = PracticeValidationSchema()

    def get(self, practiceID):
        # practiceID type (must be int) is enforced by Flask-RESTful
        practice = practice_model.Practice.query.get(practiceID)
        if practice is None:
            abort(404, message="Practice with ID {} does not exist.".format(practiceID))
        return jsonify(self.practice_schema.dump(practice).data)

    def put(self, practiceID):
        # Input validation using Marshmallow. No parameter is actually required
        # in the PUT (update) request, since we do partical/relative update.
        # practiceID type is enforced by Flask-RESTful
        _, errors = self.practice_validation_schema.load(request.json, partial=('club', 'name', 'startTime', 'durationMinutes', 'invited', 'confiremd', 'declined',))
        if len(errors) > 0:
            abort(400, message="The reqeust input could bot be validated. There were the following validation errors: {}".format(errors))

        # Get practice object from DB
        practice = practice_model.Practice.query.get(practiceID)
        if practice is None:
            abort(404, message="Practice with ID {} does not exist.".format(practiceID))

        # Do relative update: if the attribute is part of the arguments
        # then update it, otherwise leave as is.
        # All input params are validated in Marshmallow schema.

        if 'club' in request.json:
            abort(403, message="We don't allow a practice to be moved from one club to another, i.e. changing ClubID.")

        if 'name' in request.json:
                practice.name = request.json['name']

        # TODO: Validate starttime is not int the past
        if 'startTime' in request.json:
            practice.startTime = dateutil.parser.parse(request.json['startTime'])

        if 'durationMinutes' in request.json:
            practice.durationMinutes = request.json['durationMinutes']

        # Fecth all invited users and add to practice
        if 'invited' in request.json:
            user_objects = []
            for userID in request.json['invited']:
                u = user_model.User.get(userID)
                if u is not None:
                    user_objects.append(u)
            practice.invited = user_objects

        # Fecth all confirmed users and add to practice
        if 'confirmed' in request.json:
            user_objects = []
            for userID in request.json['confirmed']:
                u = user_model.User.get(userID)
                if u is not None:
                    user_objects.append(u)
            practice.confirmed = user_objects

        # Fecth all declined users and add to practice
        if request.json['declined'] in request.json:
            user_objects = []
            for userID in request.json['declined']:
                u = user_model.User.get(userID)
                if u is not None:
                    user_objects.append(u)
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
