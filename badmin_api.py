import sys
from flask import Flask, jsonify, request, abort
from flask_restful import  Api
# Import API resources
from user_resource import Users, User, UserClubs, UserPractices
from club_resource import Clubs, Club

app = Flask(__name__)
api = Api(app)

api.add_resource(Users, "/user", methods=["GET", "POST"])
api.add_resource(User, "/user/<int:userID>", methods=["GET", "PUT", "DELETE"])
api.add_resource(UserClubs, "/user/<int:userID>/clubs", methods=["GET"])
api.add_resource(UserPractices, "/user/<int:userID>/practices", methods=["GET"])

api.add_resource(Clubs, "/club", methods=["GET", "POST"])
api.add_resource(Club, "/club/<int:clubID>", methods=["GET", "POST"])

@app.route("/")
def index():
    return jsonify({"TODO":"Please write documentation"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))
