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
def UserExist(username):
    if users.find({"Username": username}).count() == 0:
        return False
    else:
        return True


class Register(Resource):
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]

        if UserExist(username):
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
