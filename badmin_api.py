import sys
from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
# Import API resources
from user_resource import Users, User, UserClubs, UserPractices
from club_resource import Clubs, Club, ClubMembers, ClubPractices
from practice_resource import Practices

app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(Users, "/user", methods=["GET", "POST"])
api.add_resource(User, "/user/<int:userID>", methods=["GET", "PUT", "DELETE"])
api.add_resource(UserClubs, "/user/<int:userID>/clubs", methods=["GET"])
api.add_resource(UserPractices, "/user/<int:userID>/practices", methods=["GET"])

api.add_resource(Clubs, "/club", methods=["GET", "POST"])
api.add_resource(Club, "/club/<int:clubID>", methods=["GET", "PUT"])
api.add_resource(ClubMembers, "/club/<int:clubID>/members", methods=["GET"])
api.add_resource(ClubPractices, "/club/<int:clubID>/practices", methods=["GET"])

api.add_resource(Practices, "/practice", methods=["GET", "POST"])
#api.add_resource(Practice, "/practice/<int:clubID>", methods=["GET", "PUT"])


@app.route("/")
def index():
    return jsonify({"TODO":"Please write documentation"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))
