from flask import jsonify
from flask_restful import Resource, abort, request
import debug_code_generator
import dateutil.parser
import traceback
import logging
# Imports for input validation (marsmallow)
from validation_schemas import ConfirmNoticeValidationSchema
# Imports for serialization (flask-marshmallow)
from serialization_schemas import ConfirmNoticeSchema
import user_model
import practice_model
import confirm_notice_model
import decline_notice_model
# Imports for DB connection
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from db_helper import db
# Imports for security
from auth_helper import auth


"""

"""
class ConfirmNotice(Resource):

    def __init__(self):
        self.confirm_notice_schmea = ConfirmNoticeSchema()
        self.confirm_notices_schema = ConfirmNoticeSchema(many=True)
        self.confirm_notice_validation_schema = ConfirmNoticeValidationSchema()
        self.logger = logging.getLogger('root')

    @auth.login_required
    def get(self, confirmNoticeID=None):
        if confirmNoticeID:
            # confirmNoticeID type (must be int) is enforced by Flask-RESTful
            confirm_notice = confirm_notice_model.ConfirmNotice.query.get(confirmNoticeID)
            if confirm_notice is None:
                abort(404, message="Confirm Notice with ID {} does not exist.".format(confirmNoticeID))
            return jsonify(self.confirm_notice_schmea.dump(confirm_notice).data)
        else:
            # Get on practice resource lists all practices
            confirm_notices = confirm_notice_model.ConfirmNotice.query.filter(1==1).all()
            return jsonify(self.confirm_notice_schmea.dump(confirm_notices).data)

    @auth.login_required
    def post(self):
        # Input validation using Marshmallow.
        _, errors = self.confirm_notice_validation_schema.load(request.json)

        if len(errors) > 0:
            abort(400, message="The reqeust input could bot be validated. There were the following validation errors: {}".format(errors))

        # All request.json input parameters are validated by Marshmallow
        # schema.

        # Get the User and Practice objects that this ConfirmNotice combines
        user = user_model.User.query.get(request.json['userId'])
        practice = practice_model.Practice.query.get(request.json['practiceId'])

        # Get timestamp of when the practice was confirmd
        try:
            # Start by checking a notice for this user-practice pair doesn't
            # exist already.
            existing_notice = confirm_notice_model.ConfirmNotice.query.filter(confirm_notice_model.ConfirmNotice.user_id == user.id,
                                                                                confirm_notice_model.ConfirmNotice.practice_id == practice.id).all()
            if len(existing_notice) > 0:
                abort(500, message="Cannot create ConfirmNotice - the practice for this user is already confirmed.")

            # Check that a DeclineNotice for this user-practice pair doesn't
            # exist.
            existing_notice = decline_notice_model.DeclineNotice.query.filter(decline_notice_model.DeclineNotice.user_id == user.id,
                                                                                decline_notice_model.DeclineNotice.practice_id == practice.id).all()
            if len(existing_notice) > 0:
                abort(500, message="Cannot create ConfirmNotice - the practice have an existing deline notice. Delete that first.")


            dt = dateutil.parser.parse(request.json['timestamp'])
            # Assume input timestring is in UTC and drop all timezone info
            dt = dt.replace(tzinfo=None)

            confirm_notice = confirm_notice_model.ConfirmNotice(dt)
            user.confirmedPractices.append(confirm_notice)
            practice.confirmed.append(confirm_notice)

            # Add a confirmNotice to DB
            db.session.add(confirm_notice)
            db.session.commit()

        except ValueError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("ValueError happend in confirm_notice_model.py (catched in confirm_notice_resource.py). Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(traceback.format_exc())
            self.logger.error(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))
        except IntegrityError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("SQL IntegrityError happend in confirm_notice_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(traceback.format_exc())
            self.logger.error(err)
            abort(500, message="Somehow the validations passed but the input still did not match the SQL schema. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))

        return jsonify(self.confirm_notice_schmea.dump(confirm_notice).data)

    """
    There is no PUT methon. Once the confirm notice is created it cannot be
    changed. It can be delete if the user changes her answer, but then DELETE
    is used.
    """

    @auth.login_required
    def delete(self, confirmNoticeID):
        # Get practice object from DB
        confirm_notice = confirm_notice_model.ConfirmNotice.query.get(confirmNoticeID)
        if confirm_notice is None:
            # Problem solved?
            abort(404, message="Cannot delete practice. ConfirmNotices with ID {} does not exist. .. problem solved?".format(confirmNoticeID))
        try:
            db.session.delete(confirm_notice)
            db.session.commit()
        except SQLAlchemyError as err:
            debug_code = debug_code_generator.gen_debug_code()
            self.logger.error("SQL Error happend in confirm_notice_resource.py. Debug code: {}. Stacktrace follows: ".format(debug_code))
            self.logger.error(err)
            abort(500, message="The database blew up. For security reasons no further details on the error will be provided other than a debug-code: {}. Please email the API developer with the debug-code and yell at him!".format(debug_code))
