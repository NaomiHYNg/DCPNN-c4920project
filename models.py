# Api 
from flask_restplus import Resource
# user management
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# other files
from database import DB
from app import api
from application import login
from bson.decimal128 import Decimal128

from hashlib import md5
from datetime import datetime


class User(UserMixin):
    def __init__(self, dictionary):
        # self.username = username
        for key in dictionary:
            setattr(self, key, dictionary[key])

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

    def get_email(self):
        return self.email

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_goal(self, goal):
        self.goal = goal

    # user.log_workout(workout_dict)
    def log_workout(self, workout_dict):
        user = DB.find_one("users", {"username": self.username})
        if not user:
            api.abort(404, "User {} not found".format(self.username))
        # update workout history
        hist = user['history'].append(workout_dict['id'])
        # update entry in DB
        DB.update("users", {"username": self.username}, {"$set": {"history": hist}})
        DB.insert("workouts", workout_dict)
        self.history = hist

    def get_history(self):
        user = DB.find_one("users", {"username": self.username})
        if not user:
            api.abort(404, "User {} not found".format(self.username))
        return user['history']

    def add(self):
        user = {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "username": self.username,
            "email": self.email,
            "password": self.password_hash,
            "fitness": self.fitness,
            "weight": Decimal128(self.weight),
            "goalweight": Decimal128(self.goalweight),
            "goal": self.goal,
            "history": []
        }
        DB.insert("users", user)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


'''
JUST WANT ID
    obj = Workout({"id" : 1}) 
ALL WORKOUT INFO for populating profile page (list of past workout with details)
    collection = DB.find_one("workouts", {"id":1}) <-- this is a dict
    collection.pop('_id', None) <-- remove mongo _id
    obj = Workout(collection) <-- workout object with fields to populate front end
'''


class Workout():
    # create workout object from dict
    def __init__(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])

    def get_id(self):
        return self.id


class Post():
    def __init__(self, user, content):
        self.content = content
        self.user = user


@login.user_loader
def load_user(username):
    collection = DB.find_one("users", {"username": username})
    if not collection:
        return None
    return User(collection)
