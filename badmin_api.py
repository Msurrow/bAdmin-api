import sys
from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
from flask_marshmallow import Marshmallow
# Import API resources
from user_resource import Users, User, UserClubs, UserPractices
from club_resource import Clubs, Club, ClubMembers, ClubPractices
from practice_resource import Practices, Practice
# Import DB resources
from db_helper import db
from serialization_schemas import ma

app = Flask(__name__)
CORS(app)

# Setup API resources
api = Api(app)

api.add_resource(Users, "/user", methods=["GET", "POST"])
api.add_resource(User, "/user/<int:userID>", methods=["GET", "PUT"])

api.add_resource(Clubs, "/club", methods=["GET", "POST"])
api.add_resource(Club, "/club/<int:clubID>", methods=["GET", "PUT"])
api.add_resource(ClubMembers, "/club/<int:clubID>/members", methods=["GET"])
api.add_resource(ClubPractices, "/club/<int:clubID>/practices", methods=["GET"])

api.add_resource(Practices, "/practice", methods=["GET", "POST"])
api.add_resource(Practice, "/practice/<int:practiceID>", methods=["GET", "PUT", "DELETE"])

# Setup database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db.init_app(app)
# Tell sqlalchemy hat this app is the current app
app.app_context().push()

# Marshmallow must be initialized after sqlalchemy
ma.init_app(app)

# API Routes that Flask-Restful API doesn't handle
@app.route("/")
def index():
    return jsonify({"TODO":"Please write documentation"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))
