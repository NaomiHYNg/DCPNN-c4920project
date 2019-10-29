from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from pymongo import MongoClient
from flask_restplus import Resource
from app import login # from __init__
from app import api

class User(UserMixin):
    def __init__(self, username):
        self.username = username

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

@login.user_loader
def load_user(username):
    #u = mongo.db.Users.find_one({"Name": username})
    # Connect to mongodb mlab
    mongo_port = 27107
    db_name = 'comp4920'
    collection_name = 'users'
    mongo_host = "mongodb://admin:admin123@ds331558.mlab.com:31558/comp4920"
    client = MongoClient(host=mongo_host, port=mongo_port)
    db = client[db_name]
    users = db[collection_name]

    collection = db.users.find_one({"username": username})

    if not collection:
        api.abort(404, "User {} not found".format(username))
    return User(username=collection['username'])
