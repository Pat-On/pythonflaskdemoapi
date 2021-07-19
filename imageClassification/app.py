"""
IMAGE CLASSIFICATION API (Chart)

application what is represented on pictures
used: tensorflow and inceptionV3

Resources |  URL        |  Method  | Params     | returns codes

Register  | /register   | Post      | Username  | 200 ok
                                    password    | 301 invalid username exist

Classify  | /classify   | Post      | username  | 200 ok
                                    pw          | 301 invalid username
                                    url         | 302 invalid password
                                                | 303 out of tokens

Refill    | /refill     | Post      | Username  | 200 ok
                                    admin pw    | 301 invalid password
                                    amount      | 304 wrong admin password
"""

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import requests
import subprocess
import json

app = Flask(__name__)

api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.ImageRecognition
users = db["Users"]


# helper function
def user_exist(username):
    if users.find({"Username": username}).count() == 0:
        return False
    else:
        return True


def verify_pw(username, password):
    if not user_exist(username):
        return False
    hashed_pw = users.find({
        "Username": username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode("utf8"), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def verify_credentials(username, password):
    if not user_exist(username):
        return generated_return_dictionary(301, "Invalid Username"), True  # two things to return

    correct_pw = verify_pw(username, password)
    if not correct_pw:
        return generated_return_dictionary(302, "Invalid Password"), True

    return None, False


def generated_return_dictionary(status, msg):
    ret = {
        "status": status,
        "msg": msg
    }
    return ret


class Register(Resource):
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]

        if user_exist(username):
            ret_json = {
                "status": 301,
                "msg": "invalid username"
            }
            return jsonify(ret_json)
        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Tokens": 6
        })

        ret_json = {
            "status": 200,
            "msg": "You successfully signed up for this API"
        }

        return jsonify(ret_json)


class Classify(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        url = posted_data["url"]

        # TODO:
        ret_json, error = verify_credentials(username, password)

        if error:
            return jsonify(ret_json)

        tokens = users.find({
            "Username": username
        })[0]["Tokens"]

        # TODO
        if tokens <= 0:
            return jsonify(generated_return_dictionary(303, "Not enough tokens"))

        r = requests.get(url)
        ret_json = {}

        with open("temp.jpg", "wb") as f:
            f.write(r.content)
            # proc = subprocess.Popen('python classify_image.py --model_dir=. --image_file=./temp.jpg')
            proc = subprocess.Popen('python classify_image.py --model_dir=. --image_file=temp.jpg',  shell=True)
            proc.communicate()[0]
            proc.wait()
            with open("text.txt") as g:
                ret_json = json.load(g)

        users.update({
            "Username": username
        }, {
            "$set": {
                "Tokens": tokens - 1
            }
        })
        return ret_json


class Refill(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["admin_pw"]
        amount = posted_data["amount"]

        if not user_exist(username):
            return jsonify(generated_return_dictionary(301, "Invalid username"))

        # hard coded for simplification
        correct_pw = "password"

        if not password == correct_pw:
            return jsonify(generated_return_dictionary(304, "Invalid administrator password"))

        users.update({
            "Username": username
        }, {
            "$set": {
                "Tokens": amount
            }
        })

        return jsonify(generated_return_dictionary(200, "You refilled the tokens amount"))


api.add_resource(Register, "/register")
api.add_resource(Classify, "/classify")
api.add_resource(Refill, "/refill")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020)
