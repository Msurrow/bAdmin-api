from flask import jsonify
from flask_restful import Resource, abort, request
import debug_code_generator
import dateutil.parser
import traceback
import logging
# Imports for input validation (marsmallow)
from validation_schemas import DeclineNoticeValidationSchema
# Imports for serialization (flask-marshmallow)
from serialization_schemas import DeclineNoticeSchema
import user_model
import practice_model
import decline_notice_model
import confirm_notice_model
# Imports for DB connection
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from db_helper import db
# Imports for security
from auth_helper import auth


"""

"""
class DeclineNotice(Resource):

    def __init__(self):
        self.decline_notice_schmea = DeclineNoticeSchema()
        self.decline_notices_schema = DeclineNoticeSchema(many=True)
        self.decline_notice_validation_schema = DeclineNoticeValidationSchema()
        self.logger = logging.getLogger('root')

    @auth.login_required
    def get(self, declineNoticeID=None):
        if declineNoticeID:
            # declineNoticeID type (must be int) is enforced by Flask-RESTful
            decline_notice = decline_notice_model.DeclineNotice.query.get(declineNoticeID)
            if decline_notice is None:
                abort(404, message="Decline Notice with ID {} does not exist.".format(declineNoticeID))
            return jsonify(self.decline_notice_schmea.dump(decline_notice).data)
        else:
            # Get on practice resource lists all practices
            decline_notices = decline_notice_model.DeclineNotice.query.filter(1==1).all()
            return jsonify(self.decline_notice_schmea.dump(decline_notices).data)

    @auth.login_required
    def post(self):
        # Input validation using Marshmallow.
        _, errors = self.decline_notice_validation_schema.load(request.json)

        if len(errors) > 0:
            abort(400, message="The reqeust input could bot be validated. There were the following validation errors: {}".format(errors))

        # All request.json input parameters are validated by Marshmallow
        # schema.

        # Get the User and Practice objects that this DeclineNotice combines
        user = user_model.User.query.get(request.json['userId'])
        practice = practice_model.Practice.query.get(request.json['practiceId'])

        # Get timestamp of when the practice was declined
        try:
            # Start by checking a notice for this user-practice pair doesn't
            # exist already.
            existing_notice = decline_notice_model.DeclineNotice.query.filter(decline_notice_model.DeclineNotice.user_id == user.id,
                                                                                decline_notice_model.DeclineNotice.practice_id == practice.id).all()
            if len(existing_notice) > 0:
                abort(500, message="Cannot create DeclineNotice - the practice for this user is already declined.")

            # Check that a ConfirmNotice for this user-practice pair doesn't
            # exist.
            existing_notice = confirm_notice_model.ConfirmNotice.query.filter(confirm_notice_model.ConfirmNotice.user_id == user.id,
                                                                                confirm_notice_model.ConfirmNotice.practice_id == practice.id).all()
            if len(existing_notice) > 0:
                abort(500, message="Cannot create DeclineNotice - the practice have an existing confirm notice. Delete that first.")

            dt = dateutil.parser.parse(request.json['timestamp'])
            # Assume input timestring is in UTC and drop all timezone info
            dt = dt.replace(tzinfo=None)

            decline_notice = decline_notice_model.DeclineNotice(dt)
            user.declinedPractices.append(decline_notice)
            practice.declined.append(decline_notice)

            # Add a declineNotice to DB
            db.session.add(decline_notice)
            db.session.commit()

        except ValueError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("ValueError happend in decline_notice_model.py (catched in decline_notice_resource.py). Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(traceback.format_exc())
            self.logger.error(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("SQL IntegrityError happend in decline_notice_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(traceback.format_exc())
            self.logger.error(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.decline_notice_schmea.dump(decline_notice).data)

    """
    There is no PUT method. Once the decline notice is created it cannot be
    changed. It can be delete if the user changes her answer, but then DELETE
    is used.
    """

    @auth.login_required
    def delete(self, declineNoticeID):
        # Get practice object from DB
        decline_notice = decline_notice_model.DeclineNotice.query.get(declineNoticeID)
        if decline_notice is None:
            # Problem solved?
            abort(404, message="Cannot delete practice. DeclineNotices with ID {} does not exist. .. problem solved?".format(declineNoticeID))
        try:
            db.session.delete(decline_notice)
            db.session.commit()
        except SQLAlchemyError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("SQL Error happend in decline_notice_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(err)
            abort(500, message="The database blew up. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))
