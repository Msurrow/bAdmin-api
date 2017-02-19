from flask import jsonify
from flask_restful import Resource, abort, request
import debug_code_generator
import traceback
import logging
# Imports for input validation (marsmallow)
from validation_schemas import UserValidationSchema
# Imports for serialization (marshmallow)
from serialization_schemas import UserSchema, PracticeSchema
import user_model
import club_model
import practice_model
# Imports for DB connection
from sqlalchemy.exc import IntegrityError
from db_helper import db
from auth_helper import auth


"""
Resource for handling non user-specific actions on User resource
"""
class Users(Resource):
    def __init__(self):
        self.user_schema = UserSchema()
        self.users_schema = UserSchema(many=True)
        self.user_validation_schema = UserValidationSchema()
        self.logger = logging.getLogger('root')

    @auth.login_required
    def get(self, userID=None):
        if userID:
            # userID type (must be int) is enforced by Flask-RESTful
            user = user_model.User.query.get(userID)
            if user is None:
                abort(404, message="User with ID {} does not exist.".format(userID))
            return jsonify(self.user_schema.dump(user).data)
        else:
            # Get on user resource without ID lists all users
            users = user_model.User.query.filter(1 == 1).all()
            return jsonify(self.users_schema.dump(users).data)

    def post(self):
        # Input validation using Marshmallow.
        _, errors = self.user_validation_schema.load(request.json, partial=('userAccessToken','clubs','practices'))
        if len(errors) > 0:
            abort(400, message="The reqeust input could bot be validated. There were the following validation errors: {}".format(errors))

        try:
            # Password is hashed in User.init
            user = user_model.User(request.json['name'], request.json['email'], request.json['phone'], request.json['password'])
        except ValueError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("ValueError happend in user_model.py (catched in user_resource.py). Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(traceback.format_exc())
            self.logger.error(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("SQL IntegrityError happend in user_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.user_schema.dump(user).data)

    def put(self, userID):
        # Input validation using Marshmallow. No parameter is actually required
        # in the PUT (update) request, since we do partical/relative update.
        # userID type is enforced by Flask-RESTful

        _, errors = self.user_validation_schema.load(request.json, partial=('name','email','phone','password','clubs','practices',))
        if len(errors) > 0:
            abort(400, message="The reqeust input could bot be validated. There were the following validation errors: {}".format(errors))

        # Get user object from DB
        user = user_model.User.query.get(userID)
        if user is None:
            abort(404, message="User with ID {} does not exist.".format(userID))

        # Do relative update: if the attribute is part of the arguments
        # then update it, otherwise leave as is.
        # All input params are validated in Marshmallow schema.

        if 'name' in request.json:
            user.name = request.json['name']

        if 'email' in request.json:
            user.email = request.json['email']

        if 'phone' in request.json:
            user.phone = request.json['phone']

        if 'password' in request.json:
            hashedPassword = request.json['password']
            user.password = hashedPassword

        # Fecth all users' clubs and add to user
        if 'clubs' in request.json:
            club_objects = []
            for clubID in request.json['clubs']:
                c = club_model.Club.query.get(clubID)
                if c is not None:
                    club_objects.append(c)
            user.clubs = club_objects

        # Fecth all users' practices and add to user
        if 'practices' in request.json:
            practice_objects = []
            for practiceID in request.json['practice']:
                c = practice_model.Practice.query.get(practiceID)
                if c is not None:
                    practice_objects.append(c)
            user.clubs = practice_objects

        try:
            db.session.commit()
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("SQL IntegrityError happend in user_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.user_schema.dump(user).data)

    def delete(self, practiceID):
        abort(501)

"""
Resource for handling club-pecific temporally related requests on Club resource
"""
class UserPractices(Resource):

    def __init__(self):
        self.practices_schema = PracticeSchema(many=True)
        self.logger = logging.getLogger('root')

    def get(self, userID):
        #now = datetime.datetime.now() ,practice_model.Practice.startTime >= now)
        practices = practice_model.Practice.query.\
            filter((practice_model.Practice.invited.any(user_model.User.id == userID)) |
                   (practice_model.Practice.confirmed.any(user_model.User.id == userID)) |
                   (practice_model.Practice.declined.any(user_model.User.id == userID)))\
            .order_by(practice_model.Practice.startTime.asc())\
            .all()
        return jsonify(self.practices_schema.dump(practices).data)