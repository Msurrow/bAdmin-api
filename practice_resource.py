from flask import jsonify
from flask_restful import Resource, abort, request
import debug_code_generator
import dateutil.parser
import traceback
import logging
from datetime import timedelta
# Imports for input validation (marsmallow)
from validation_schemas import PracticeValidationSchema
# Imports for serialization (flask-marshmallow)
from serialization_schemas import PracticeSchema
import user_model
import club_model
import practice_model
# Imports for DB connection
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from db_helper import db
from auth_helper import auth


"""
Resource for handling non-practice-pecific actions on Practice resource
"""
class Practices(Resource):

    def __init__(self):
        self.practice_schema = PracticeSchema()
        self.practices_schema = PracticeSchema(many=True)
        self.practice_validation_schema = PracticeValidationSchema()
        self.logger = logging.getLogger('root')

    @auth.login_required
    def get(self, practiceID=None):
        if practiceID:
            # practiceID type (must be int) is enforced by Flask-RESTful
            practice = practice_model.Practice.query.get(practiceID)
            if practice is None:
                abort(404, message="Practice with ID {} does not exist.".format(practiceID))
            return jsonify(self.practice_schema.dump(practice).data)
        else:
            # Get on practice resource lists all practices
            practices = practice_model.Practice.query.filter(1==1).order_by(practice_model.Practice.startTime.asc()).all()
            return jsonify(self.practices_schema.dump(practices).data)

    @auth.login_required
    def post(self):
        # Input validation using Marshmallow.
        _, errors = self.practice_validation_schema.load(request.json)

        if len(errors) > 0:
            abort(400, message="The reqeust input could bot be validated. There were the following validation errors: {}".format(errors))

        # TODO: Validate starttime is not in the past

        # All request.json input parameters are validated by Marshmallow
        # schema.
        club = club_model.Club.query.get(request.json['club'])

        try:
            st = dateutil.parser.parse(request.json['startTime'])
            # Assume input timestring is in UTC and drop all timezone info
            st = st.replace(tzinfo=None)

            invited = []

            # Fecth all invited users and add to practice
            if 'invited' in request.json:
                user_objects = []
                for userID in request.json['invited']:
                    u = user_model.User.query.get(userID)
                    if u is not None:
                        user_objects.append(u)
                invited = user_objects

            repeats = 1

            if 'repeats' in request.json and request.json['repeats'] is not None:
                repeats = int(request.json['repeats'])

            for x in range(0, repeats):
                practice = practice_model.Practice(request.json['name'], club, st, request.json['durationMinutes'])
                practice.invited = invited

                # Add a practice
                db.session.add(practice)

                # Add one week to the starttime (for next practice)
                st = st + timedelta(weeks=1)

            db.session.commit()

        except ValueError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("ValueError happend in practice_model.py (catched in practice_resource.py). Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(traceback.format_exc())
            self.logger.error(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("SQL IntegrityError happend in practice_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(traceback.format_exc())
            self.logger.error(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.practice_schema.dump(practice).data)

    @auth.login_required
    def put(self, practiceID):
        # Input validation using Marshmallow. No parameter is actually required
        # in the PUT (update) request, since we do partical/relative update.
        # practiceID type is enforced by Flask-RESTful
        _, errors = self.practice_validation_schema.load(request.json, partial=('club', 'name', 'startTime', 'durationMinutes', 'invited', 'confiremd', 'declined',))
        self.logger.debug("errors: {}".format(errors))
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
            st = dateutil.parser.parse(request.json['startTime'])
            # Assume input timestring is in UTC and drop all timezone info
            practice.startTime = st.replace(tzinfo=None)

        if 'durationMinutes' in request.json:
            practice.durationMinutes = request.json['durationMinutes']

        # Fecth all invited users and add to practice
        if 'invited' in request.json:
            user_objects = []
            for userID in request.json['invited']:
                u = user_model.User.query.get(userID)
                if u is not None:
                    user_objects.append(u)
            practice.invited = user_objects

        # Fecth all confirmed users and add to practice
        if 'confirmed' in request.json:
            user_objects = []
            for userID in request.json['confirmed']:
                u = user_model.User.query.get(userID)
                if u is not None:
                    user_objects.append(u)
            practice.confirmed = user_objects

        # Fecth all declined users and add to practice
        if 'declined' in request.json:
            user_objects = []
            for userID in request.json['declined']:
                u = user_model.User.query.get(userID)
                if u is not None:
                    user_objects.append(u)
            practice.declined = user_objects

        try:
            db.session.commit()
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("SQL IntegrityError happend in practice_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.practice_schema.dump(practice).data)

    @auth.login_required
    def delete(self, practiceID):
        # Get practice object from DB
        practice = practice_model.Practice.query.get(practiceID)
        if practice is None:
            # Problem solved?
            abort(404, message="Cannot delete practice. Practice with ID {} does not exist. .. problem solved?".format(practiceID))
        try:
            db.session.delete(practice)
            db.session.commit()
        except SQLAlchemyError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("SQL Error happend in practice_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(err)
            abort(500, message="The database blew up. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))
