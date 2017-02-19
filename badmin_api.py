import sys
import os
from flask import Flask, jsonify, g, request, abort
from flask_restful import Api
from flask_cors import CORS
import logging, logging.config, yaml
# Import API resources
from user_resource import Users, UserPractices
from club_resource import Clubs, ClubPractices
from practice_resource import Practices
import user_model
# Import DB resources
from db_helper import db
from serialization_schemas import ma
# Security
from auth_helper import auth

app = Flask(__name__)
CORS(app)

# Setup API resources
api = Api(app)

api.add_resource(Users, "/user", methods=["GET", "POST"], endpoint="users_all")
api.add_resource(Users, "/user/<int:userID>", methods=["GET", "PUT"], endpoint="user_with_id")
api.add_resource(UserPractices, "/user/<int:userID>/practices", methods=["GET"], endpoint="user_practies_with_id")

api.add_resource(Clubs, "/club", methods=["GET", "POST"], endpoint="clubs_all")
api.add_resource(Clubs, "/club/<int:clubID>", methods=["GET", "PUT", "DELETE"], endpoint="club_with_id")
api.add_resource(ClubPractices, "/club/<int:clubID>/practicesbyweek", methods=["GET"], endpoint="club_practies_by_week_all")
api.add_resource(ClubPractices, "/club/<int:clubID>/practicesbyweek/<int:weekNumber>", methods=["GET"], endpoint="club_practies_by_week_with_number")

api.add_resource(Practices, "/practice", methods=["GET", "POST"], endpoint="practices_all")
api.add_resource(Practices, "/practice/<int:practiceID>", methods=["GET", "PUT", "DELETE"], endpoint="practice_with_id")

# Setup database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# Heroku postgres have 20 conn limit. Running 4 workers parallel limits each worker to 5 conns.
app.config['SQLALCHEMY_POOL_SIZE'] = 5
db.init_app(app)
# Tell sqlalchemy that this app is the current app
app.app_context().push()

# Marshmallow must be initialized after sqlalchemy
ma.init_app(app)

if not app.debug:
    # In production mode, log to both stdout and logfile
    logging.config.dictConfig(yaml.load(open('logging.conf')))

# Setup security and helper methods
@auth.verify_password
def verify_password(useremail_or_token, password):
    if not useremail_or_token:
        return False
    # first try to authenticate by token
    user = user_model.User.verify_auth_token(useremail_or_token)
    if not user:
        # try to authenticate with username/password
        user = user_model.User.query.filter_by(email=useremail_or_token).first()
        if not user or not user.verify_password(password):
            return False
    return True

# API Routes that Flask-Restful API doesn't handle
@app.route("/")
def index():
    return jsonify({"TODO":"Please write documentation"})

@app.route('/token')
@auth.login_required
def get_auth_token():
    if not request or not request.authorization:
        abort(400, "Missing HTTPBasic auth parameters")
    user = user_model.User.query.filter_by(email=request.authorization.username).first()
    token = user.generate_auth_token()
    return jsonify({'userID':user.id,'token': token.decode('ascii')})

if __name__ == "__main__":
    # When run with gunicorn this isn't called, and gunicorn will run as debug=false
    app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))
