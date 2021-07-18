"""
Similarity of text (plagiarism test)

Resources           | URL        | method | Param         | Status code
Register new user   | /register  |  POST  | username      |  200 ok
                                            password      |  301 invalid
Detect Similarity   | /detect    |  POST  | username      |  200 ok
                                            password      |  301 invalid username
                                            text1         |  302 invalid pw
                                            text2         |  303 out of tokens
Refill tokens       | /refill    |  POST  | username      |  200 ok
                                            admin pw      |  301 invalid username
                                            refill amount |  304 incorrect admin pw
"""

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

import spacy
spacy.load('en_core_web_sm')

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB

# collections
users = db["Users"]


def UserExist(username):
    if users.find({"username": username}).count() == 0:
        return False
    else:
        return True


def VerifyPw(username, password):
    if not UserExist(username):
        return False

    hashed_pw = users.find({
        "username": username
    })[0]["password"]

    if bcrypt.hashpw(password.encode("utf8"), hashed_pw) == hashed_pw:
        return True
    else:
        return False


# maybe we should do it at the same time when we check if user exist
def CountTokens(username):
    tokens = users.find({
        "username": username
    })[0]["tokens"]
    return tokens


class Register(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data['password']

        if UserExist(username):
            ret_json = {
                "status": 300,
                "msg": "Invalid Username"
            }
            return jsonify(ret_json)

        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        users.insert({
            "username": username,
            "password": hashed_pw,
            "tokens": 6
        })

        ret_json = {
            "status": 200,
            "msg": "YOu have successful signed up to the API"
        }
        return jsonify(ret_json)


class Detect(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        text1 = posted_data["text1"]
        text2 = posted_data["text2"]

        if not UserExist(username):
            ret_json = {
                "status": 300,
                "msg": "Invalid Username"
            }
            return jsonify(ret_json)

        correct_pw = VerifyPw(username, password)
        if not correct_pw:
            ret_json = {
                "status": 302,
                "msg": "Invalid Password"
            }
            return ret_json

        num_tokens = CountTokens(username)
        if num_tokens <= 0:
            ret_json = {
                "status": 303,
                "msg": "You are out of tokens, please refill!"
            }
            return jsonify(ret_json)

        # natural language processor
        nlp = spacy.load('en_core_web_sm')

        text1 = nlp(text1)
        text2 = nlp(text2)

        # ratio is a number between 0 and 1 the closer 1 the more similar text and text 2 are
        ratio = text1.similarity(text2)

        ret_json = {
            "status": 200,
            "similarity": ratio,
            "msg": "Similarity score calculated successfully"
        }

        current_tokens = CountTokens(username)
        users.update({
            "username": username,
        }, {
            "$set": {
                "tokens": current_tokens - 1
            }
        })
        return jsonify(ret_json)


class Refill(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["admin_pw"]
        refill_amount = posted_data["refill"]

        if not UserExist(username):
            ret_json = {
                "status": 301,
                "msg": "Invalid Username"
            }
            return jsonify(ret_json)

        # hard coded solution to simplify - fun
        correct_pw = "password"
        if not password == correct_pw:
            ret_json = {
                "status": 304,
                "msg": "Invalid Admin Password"
            }
            return jsonify(ret_json)

        current_tokens = CountTokens(username)
        users.update({
            "username": username
        }, {
            "$set": {
                "tokens": refill_amount + current_tokens
            }
        })

        ret_json = {
            "status": 200,
            "msg": "Refilled successfully"
        }
        return jsonify(ret_json)


# adding resources to API
api.add_resource(Register, '/register')
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')

# Check
@app.route('/')
def hello_world():
    return "Hello World from textSimilarity app!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010)
