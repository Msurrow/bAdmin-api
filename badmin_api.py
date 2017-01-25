import sys
import os
from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
import logging, logging.config, yaml
# Import API resources
from user_resource import Users
from club_resource import Clubs, ClubPractices
from practice_resource import Practices
# Import DB resources
from db_helper import db
from serialization_schemas import ma

app = Flask(__name__)
CORS(app)

# Setup API resources
api = Api(app)

api.add_resource(Users, "/user", methods=["GET", "POST"], endpoint="users_all")
api.add_resource(Users, "/user/<int:userID>", methods=["GET", "PUT"], endpoint="users_with_id")

api.add_resource(Clubs, "/club", methods=["GET", "POST"], endpoint="clubs_all")
api.add_resource(Clubs, "/club/<int:clubID>", methods=["GET", "PUT", "DELETE"], endpoint="clubs_with_id")
api.add_resource(ClubPractices, "/club/<int:clubID>/practicesbyweek", methods=["GET"], endpoint="club_practies_by_week_all")
api.add_resource(ClubPractices, "/club/<int:clubID>/practicesbyweek/<int:weekNumber>", methods=["GET"], endpoint="club_practies_by_week_with_number")

api.add_resource(Practices, "/practice", methods=["GET", "POST"], endpoint="practices_all")
api.add_resource(Practices, "/practice/<int:practiceID>", methods=["GET", "PUT", "DELETE"], endpoint="practices_with_id")

# Setup database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db.init_app(app)
# Tell sqlalchemy that this app is the current app
app.app_context().push()

# Marshmallow must be initialized after sqlalchemy
ma.init_app(app)

if not app.debug:
    # In production mode, log to both stdout and logfile
    logging.config.dictConfig(yaml.load(open('logging.conf')))

# API Routes that Flask-Restful API doesn't handle
@app.route("/")
def index():
    return jsonify({"TODO":"Please write documentation"})

if __name__ == "__main__":
    # When run with gunicorn this isn't called, and gunicorn will run as debug=false
    app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))
