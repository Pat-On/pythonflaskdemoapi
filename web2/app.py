"""
Similarity of text

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





@app.route('/')
def hello_world():
    return "Hello World from web2 app!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010)
