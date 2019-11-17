# user management
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import DB
from app import api
from application import login

from hashlib import md5

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
    
    def get_email(self):
        return self.email

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def set_email(self, email):
        self.email = email
    
    def add(self):
        user = {
            "username": self.username, 
            "email": self.email, 
            "password": self.password_hash
            }
        DB.insert("users", user)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

@login.user_loader
def load_user(username):
    collection = DB.find_one("users", {"username":username})

    if not collection:
        api.abort(404, "User {} not found".format(username))
    return User(username=collection['username'])


