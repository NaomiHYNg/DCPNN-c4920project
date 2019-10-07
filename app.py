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

@api.route('/exercises')
class AllCollections(Resource):
	def get(self):

		# Connect to mongodb mlab
		mongo_port = 27107
		db_name = 'comp4920'
		collection_name = 'exercises'
		mongo_host = "mongodb://admin:admin123@ds331558.mlab.com:31558/comp4920"
		client = MongoClient(host=mongo_host, port=mongo_port)
		db = client[db_name]
		exercises = db[collection_name]

		# Obtain collection
		collection = db.exercises.find()

		output_list = []

		# Abort if collection not found
		if not collection:
			api.abort(404, "There are no collections in the database")

		# For testing, print out all records
		for record in collection:
			output_list.append(record)
			print(record)

		return output_list

if __name__ == '__main__':    

    app.run(debug=True)