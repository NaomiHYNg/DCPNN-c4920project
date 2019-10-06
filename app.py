import json
from pymongo import MongoClient
import requests
from flask import Flask
from flask import request
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
import re

# Helper Functions
app = Flask(__name__)
api = Api(app)