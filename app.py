import json
from pymongo import MongoClient
# import requests
from flask import Flask
from flask import request, jsonify
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash


import re
import random
from database import DB



# Helper Functions
app = Flask(__name__)
api = Api(app)
DB.init()
login = LoginManager() # exported into models.py and
login.init_app(app) 
login.login_view = 'login'

def updateEntry(record, collection, query):
    collection.update(query, record)

def intersection(lst1, lst2):
    output_list = []
    for i1 in lst1:
        for i2 in lst2:
            #print(i1)
            #print(i2)
            if i1.lower() == i2.lower():
                output_list.append(i1)
    #print(output_list)            
    return output_list            

# Setup parser
parser = reqparse.RequestParser()
parser.add_argument('energy', type=int, required=True)
parser.add_argument('muscle', action='split')
 
# GET http://127.0.0.1:5000/exercises?energy=3

@api.route('/exercises')
class AllCollections(Resource):
    @api.expect(parser)
    def get(self):

        # Obtain energy entry
        args = parser.parse_args()
        energy = args['energy'] # returns an integer
        usr_muscle_list = args['muscle'] # returns a list of muscles
        #print(usr_muscle_list)        
        #usr_muscle_list = ["Triceps"]
        # Obtain collection
        #collection = db.exercises.find()
        collection = DB.find_all("exercises")

        # Abort if collection not found
        if not collection:
            api.abort(404, "There are no collections in the database")

        output_list = []
        output_id_list = [] # list of exercise ids only        

        # If the user has muscle preferences
        if usr_muscle_list: 
            single_id_dict = {} # each muscle is a key of the dictionary
            compound_id_list = [] # list of dictionaries {id: len(intersection)}
            # For each exercise, find the intersection between the user's muscle input list and the muscle list in the exercise
            for record in collection:
                muscle_list = record['muscle']
                #print(record['exercise'])
                exercise_id = record['id']
                #print(muscle_list)
                inter_list = intersection(usr_muscle_list , muscle_list)
                if len(inter_list) > 0: # if there are entries in the list
                    #print(record['id'])
                    #print(inter_list)

                    # if the exercise's associated muscle/s only matches one of the user's muscle preferences
                    if len(inter_list) == 1:
                        #print(record['exercise'])
                        if inter_list[0] in single_id_dict: 
                            single_id_dict[inter_list[0]].append(exercise_id)
                        else:
                            single_id_dict[inter_list[0]] = []
                            single_id_dict[inter_list[0]].append(exercise_id)

                    # if the exercise has more than one matching muscle   
                    if len(inter_list) > 1:
                        #print("not completed")
                        temp_dict = {"id": exercise_id, "intersection_len": len(inter_list)}
                        compound_id_list.append(temp_dict)
                        #print(record['exercise'])

            compound_id_list = sorted(compound_id_list, key = lambda i: i['intersection_len'], reverse=True)
            print("Compound List")
            print(compound_id_list)
            print("Single List")
            print(single_id_dict)

            counter = energy

            # if there are more user required exercises than the compound list
            # take all exercises from the compound list
            if energy > len(compound_id_list):
                for i in compound_id_list:
                    output_id_list.append(i['id'])
                    counter = counter - 1

                # choose remaining exercises from the dictionary of single exercises 

                total_single = 0
                total = len(output_id_list)

                # count the number of exercises in the single list
                for key, value in single_id_dict.items():
                    #print(value)
                    total_single = total_single + len(value)

                # count the number of exercises in both single and compound list
                total = total + total_single
                #print(total)
                #print(counter)
                
                # if there are less exercises available than requested, take all single exercises
                if total <= counter:
                    for key, value in single_id_dict.items():
                        output_id_list.extend(value)
                else:
                    while counter > 0:
                        #print(counter)
                        for key, value in single_id_dict.items():
                            #print(key)
                            #print(value)
                            random.shuffle(value)
                            temp_id = single_id_dict[key][0]
                            if temp_id in output_id_list:
                                continue
                            else:
                                output_id_list.append(temp_id)
                                counter = counter - 1
                                if counter == 0:
                                    break   

            # if there are less user required exercises than the compound list
            # randomly select the required number of exercises
            else:
                random.shuffle(compound_id_list)
                temp_list = compound_id_list[:energy]
                for i in temp_list:
                    output_id_list.append(i['id'])

            print("Output Id List")
            print(output_id_list)
            for i in output_id_list:
                entry = DB.find_one("exercises", {"id":i})
                #print(entry)
                exercise_name = entry['exercise']
                description = entry['description']
                muscle = entry['muscle']
                photo = entry['photo']
                equipment = entry["equipment"]

                output_dict = {
                    "id": i,
                    "exercise": exercise_name,
                    "description": description,
                    "photo": photo,
                    "muscle": muscle,
                    "equipment": equipment
                }
                output_list.append(output_dict)            


        # if there are no user muscle preferences, set default value
        #else:
        #   print("no muscles")
        
        # Muscle groups are not in consistent format
        # Temporary solution - randomly select any requested number of exercises if no muscle groups selected

        if not output_id_list:
            # For exercisesing, print out all records
            tricep_id_list = []
            quad_id_list = []
            ham_id_list = []

            for record in collection:
                exercise_id = record['id']
                muscle = record['muscle']

                if "Triceps" in muscle:
                    tricep_id_list.append(exercise_id)
                elif "Quadriceps" in muscle:
                    quad_id_list.append(exercise_id)
                elif "Hamstrings" in muscle:
                    ham_id_list.append(exercise_id)

            # assume energy level will always be divisible by 3
            num_per_muscle = int(energy/3)

            random.shuffle(tricep_id_list)
            random.shuffle(quad_id_list)
            random.shuffle(ham_id_list)
            tricep_id_list = tricep_id_list[:num_per_muscle]
            quad_id_list = quad_id_list[:num_per_muscle]
            ham_id_list = ham_id_list[:num_per_muscle]

            default_list = []
            default_list.append(tricep_id_list)
            default_list.append(quad_id_list)
            default_list.append(ham_id_list)
            #print(default_list) #working fine
            for m_list in default_list:
                for i in m_list:
                    entry = DB.find_one("exercises", {"id":i})
                    #print(entry)
                    exercise_name = entry['exercise']
                    description = entry['description']
                    muscle = entry['muscle']
                    photo = entry['photo']
                    equipment = entry["equipment"]

                    output_dict = {
                        "id": i,
                        "exercise": exercise_name,
                        "description": description,
                        "photo": photo,
                        "muscle": muscle,
                        "equipment": equipment
                    }
                    output_list.append(output_dict)            
        #print(output_list)
        return output_list, 200

#http://127.0.0.1:5000/exercises/1
@api.route('/exercises/<int:exercise_id>')
class ExerciseCollection(Resource):
    def get(self, exercise_id):

        # Connect to mongodb mlab
        collection = DB.find_one("exercises", {"id": exercise_id})
        
        if not collection:
            api.abort(404, "Collection id {} not found".format(exercise_id))

        exercise = collection['exercise']
        muscle = collection['muscle']
        equipment = collection['equipment']
        photo = collection['photo']
        description = collection['description']

        output = {"id": exercise_id, "exercise": exercise, "muscle": muscle, "equipment": equipment, "photo": photo, "description": description}

        return output, 200

    def put(self, exercise_id):
        payload = request.form

        # Connect to mongodb mlab
        collection = DB.find_one("exercises", {"id": exercise_id})

        exercise = payload['exercise']
        muscle = payload['muscle']
        equipment = payload['equipment']
        photo = payload['photo']
        description = payload['description']

        new_entry = {"id": exercise_id, "exercise": exercise, "muscle": muscle, "equipment": equipment, "photo": photo, "description": description}

        updateEntry(new_entry, "exercises", {"id": exercise_id})

        return new_entry, 200, None

# returns list of all users
@api.route('/users')
class AllUsers(Resource):
    #@api.expect(parser)
    def get(self):

        collection = DB.find_all("users")
        # Abort if collection not found
        if not collection:
            api.abort(404, "There are no collections in the database")

        output_list = []
        for record in collection: 
            output_dict = {
                "username": record['username'],
                "password": record['password']
            }
            output_list.append(output_dict)   
        return output_list, 200

    def put(self):
        payload = request.form
        user = {
            "username": payload['username'],
            "password": generate_password_hash(payload['password'])
        }
        user_id = DB.insert("users", user)
        return user_id


@api.route('/users/<username>')
class Users(Resource):
    #@api.expect(parser)
    def get(self, username):
        # Obtain collection
        collection = DB.find_one("users", {"username":username})
        
        # Abort if collection not found
        if not collection:
            api.abort(404, "There are no collections in the database")

        output_list = []
        output_dict = {
            "username": collection['username'],
            "password": collection['password']
        }
        output_list.append(output_dict)   
        return output_list, 200 

    # update user password
    # pass in username and new password
@api.route('/update', methods=['PUT'])
class UpdateUser(Resource):
    def put(self, username):
        payload = request.form
        if request.method == 'PUT':
            user = {
                "username": payload['username'],
                "password": generate_password_hash(payload['password'])
            }
        user_id = DB.update("users", {"username": username}, user)
        resp = jsonify('User updated successfully!')
        resp.status_code = 200
        return resp
    


# Method used by developers only. Exercises will not be generated by the user
# def post(self)

if __name__ == '__main__':
    app.run(port=5001, debug=True)