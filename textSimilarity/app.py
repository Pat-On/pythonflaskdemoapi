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

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB

# collections
users = db["Users"]


def UserExist(username):
    if users.find({"Username": username}).count() == 0:
        return False
    else:
        return True


def VerifyPw(username, password):
    if not UserExist(username):
        return False

    hashed_pw = users.find({
        "Username": username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode("utf8"), hashed_pw) == hashed_pw:
        return True
    else:
        return False


# maybe we should do it at the same time when we check if user exist
def CountTokens(username):
    tokens = users.find({
        "Usersname": username
    })[0]["Tokens"]
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

        hashed_pw = bcrypt.hashpw(password.encoded("utf8"), bcrypt.gensalt())

        users.instert_one({
            "Username": username,
            "Password": hashed_pw,
            "Tokens": 6
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
            "Username": username,
        }, {
            "$set": {
                "Tokens": current_tokens - 1
            }
        })
        return jsonify(ret_json)


@app.route('/')
def hello_world():
    return "Hello World from textSimilarity app!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010)
