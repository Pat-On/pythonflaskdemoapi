"""
registration of a user 0 token
each user gets 10 tokens
store a sentence on out database for 1 token
retrieve his stored sentence for 1 token

API chart
Resource             |    /address     | Protocol  |   Param                       |  Response + Status
Register user        |    /register    | Post      | username password string      |  200 ok
store sentence       |    /store       | post      | username password sentence    |  200ok
                                                                                      301 no token
                                                                                      302 inv P & Un
retrieve sentence    |    /get         | GET       | user n + p                    |  200 ok
                                                                                      301 no token
                                                                                      302 inv P and UN

"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]


# HELPER FUNCTIONS
def verify_password(username, password):
    hashed_pw = users.find({
        "Username": username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def count_tokens(username):
    tokens = users.find({
        "Username": username
    })[0]["Tokens"]
    return tokens


# RESOURCES
class Register(Resource):
    def post(self):
        # to get users data
        posted_data = request.get_json()

        # Get the data - no validation - study API
        user_name = posted_data["username"]
        password = posted_data["password"]

        # hash(password + salt) = blablablabalbalb in python py-bcrypt
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        # store username and pt into the db - in production what is normal to check if user exist!
        users.insert({
            "Username": user_name,
            "Password": hashed_pw,
            "Sentence": "",  # placeholder
            "Tokens": 10
        })
        #         creating the map
        ret_json = {
            "status": 200,
            "msg": "You successfully signed up for API"
        }
        return jsonify(ret_json)


class Store(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        sentence = posted_data["sentence"]

        #         login user - verification - simplification
        correct_pw = verify_password(username, password)

        if not correct_pw:
            ret_json = {
                "status": 302
            }
            return jsonify(ret_json)

        #         to verify number of tokens
        numbers_of_tokens = count_tokens(username)
        if numbers_of_tokens <= 0:
            ret_json = {
                "status": 301
            }
            return jsonify(ret_json)
        #  if enough tokens store the sentence take one token aay and return 200 OK????
        users.update({
            "Username": username
        }, {
            "$set": {
                "Sentence": sentence,
                "Tokens": numbers_of_tokens - 1
            }
        })

        ret_json = {
            "status": 200,
            "msg": "Sentence saved successfully"
        }
        return jsonify(ret_json)


class Get(Resource):
    def get(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        correct_pw = verify_password(username, password)
        if not correct_pw:
            ret_json = {
                "status": 302
            }
            return jsonify(ret_json)

        numbers_of_tokens = count_tokens(username)
        if numbers_of_tokens <= 0:
            ret_json = {
                "status": 301
            }
            return jsonify(ret_json)
        users.update({
            "Username": username
        }, {
            "$set": {
                "Tokens": numbers_of_tokens - 1
            }
        })

        sentence = users.find({
            "Username": username
        })[0]["Sentence"]

        ret_json = {
            "status": 200,
            "sentence": sentence
        }

        return jsonify(ret_json)


# RESOURCES OF OUR API
api.add_resource(Register, '/register')
api.add_resource(Store, "/store")
api.add_resource(Get, "/get")


# Simple check route
@app.route('/')
def hello_world():
    return "Hello World from web1 app!"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
