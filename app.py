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
login = LoginManager()  # exported into models.py and
login.init_app(app)
login.login_view = 'login'

# Fitness levels in integer form
BEGINNER = 1
INTEMEDIATE = 2
ADVANCED = 3


def updateEntry(record, collection, query):
    collection.update(query, record)


def intersection(lst1, lst2):
    output_list = []
    for i1 in lst1:
        for i2 in lst2:
            if i1.lower() == i2.lower():
                output_list.append(i1)
    return output_list


def genMuscleListFromComp(output_id_list, compound_id_list, muscle_checklist):
    for i in output_id_list:
        for j in compound_id_list:
            if j['id'] == i:
                for k in j['inter_list']:
                    muscle_checklist[k] = True

    # print(muscle_checklist)
    return muscle_checklist


def genMuscleListFromSing(muscle, muscle_checklist):
    muscle_checklist[muscle] = True
    return muscle_checklist


def checkMissingMuscle(muscle_checklist):
    check = True
    for key, value in muscle_checklist.items():
        # print(key)
        if value == False:
            #   print("is False")
            check = False
    return check


def convertFitnessLevel(str_level):
    int_level = 0
    if str_level.lower() == "beginner":
        int_level = BEGINNER
    if str_level.lower() == "intermediate":
        int_level = INTEMEDIATE
    if str_level.lower() == "advanced":
        int_level = ADVANCED

    return int_level


# Setup parser
parser = reqparse.RequestParser()
parser.add_argument('energy', type=int, required=True)
parser.add_argument('muscle', action='split')
parser.add_argument('equipment', action='split')
parser.add_argument('level')


# GET http://127.0.0.1:5001/exercises?energy=3

@api.route('/exercises')
class AllCollections(Resource):
    @api.expect(parser)
    def get(self):

        # Obtain energy entry
        args = parser.parse_args()
        energy = args['energy']  # returns an integer
        usr_muscle_list = args['muscle']  # returns a list of muscles
        equip_usr_list = args['equipment']
        usr_fitness_level = convertFitnessLevel(args['level'])
        collection = DB.find_all("test1")

        # Abort if collection not found
        if not collection:
            api.abort(404, "There are no collections in the database")

        output_list = []
        output_id_list = []  # list of exercise ids only

        # If the user has muscle preferences
        if usr_muscle_list:

            single_id_dict = {}  # each muscle is a key of the dictionary
            compound_id_list = []  # list of dictionaries {id: len(intersection)}
            muscle_checklist = dict.fromkeys(usr_muscle_list, False)  # Create muscle checklist

            # For each exercise, find the intersection between the user's muscle input list and the muscle list in the exercise
            for record in collection:
                muscle_list = record['muscle']
                # print(record['exercise name'])
                exercise_id = record['id']
                level = convertFitnessLevel(record['level'])

                if (level > usr_fitness_level):
                    continue

                # print(muscle_list)
                inter_list = intersection(usr_muscle_list, muscle_list)

                if len(inter_list) > 0:  # if there are entries in the list

                    # if the exercise's associated muscle/s only matches one of the user's muscle preferences
                    if len(inter_list) == 1:
                        # print(record['exercise name'])
                        if inter_list[0] in single_id_dict:
                            single_id_dict[inter_list[0]].append(exercise_id)
                        else:
                            single_id_dict[inter_list[0]] = []
                            single_id_dict[inter_list[0]].append(exercise_id)

                    # if the exercise has more than one matching muscle
                    if len(inter_list) > 1:
                        # print("not completed")
                        temp_dict = {"id": exercise_id, "intersection_len": len(inter_list), "inter_list": inter_list,
                                     "level": level}
                        compound_id_list.append(temp_dict)
                        # print(record['exercise name'])

            compound_id_list = sorted(compound_id_list, key=lambda i: (i['intersection_len'], i['level']), reverse=True)

            # EQUIPMENT SELECTION
            # remove all items in list that do not match user's equipment selections

            temp_list_a = []

            if equip_usr_list:
                equip_usr_list.append("Bodyweight")
                for cl in compound_id_list:
                    record = DB.find_one("test1", {"id": cl['id']})
                    # print(cl['id'])
                    equipment = record['equipment']
                    if equipment in equip_usr_list:
                        temp_list_a.append(cl)
                        # print("here")
                compound_id_list = temp_list_a

                temp_list_a = []

                for key, value in single_id_dict.items():
                    temp_list_a = []
                    for sl in value:
                        record = DB.find_one("test1", {"id": sl})
                        # print(sl)
                        equipment = record['equipment']
                        if equipment in equip_usr_list:
                            temp_list_a.append(sl)
                    single_id_dict[key] = temp_list_a

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

                genMuscleListFromComp(output_id_list, compound_id_list, muscle_checklist)

                print("Muscle checklist")
                print(muscle_checklist)

                # choose remaining exercises from the dictionary of single exercises

                total_single = 0
                total = len(output_id_list)

                # count the number of exercises in the single list
                for key, value in single_id_dict.items():
                    # print(value)
                    total_single = total_single + len(value)
                    # count the number of exercises in both single and compound list
                total = total + total_single
                # print(total)
                # print(counter)

                # if there are less exercises available than requested, take all single exercises
                if total <= counter:
                    for key, value in single_id_dict.items():
                        output_id_list.extend(value)
                else:
                    while counter > 0:
                        # if a muscle is missing from the muscle checklist
                        if checkMissingMuscle(muscle_checklist) == False:
                            for key, value in muscle_checklist.items():
                                if value == False:
                                    if key in single_id_dict.keys():
                                        if len(single_id_dict[key]) != 0:
                                            random.shuffle(single_id_dict[key])
                                            output_id_list.append(single_id_dict[key][0])
                                            genMuscleListFromSing(key, muscle_checklist)
                                            print(muscle_checklist)
                                            counter = counter - 1
                                            if counter == 0:
                                                break
                        if counter == 0:
                            break
                        for key, value in single_id_dict.items():
                            if len(single_id_dict[key]) != 0:
                                random.shuffle(value)
                                temp_id = single_id_dict[key][0]
                                if temp_id not in output_id_list:
                                    output_id_list.append(temp_id)
                                    counter = counter - 1
                                    if counter == 0:
                                        break

            # if there are less user required exercises than the compound list
            # randomly select the required number of exercises
            # fitness level filtered out correctly
            else:
                # random.shuffle(compound_id_list)
                counter = 0

                for key, value in muscle_checklist.items():
                    if counter < energy:
                        if value == False:
                            for cl in compound_id_list:
                                if key in cl['inter_list']:
                                    output_id_list.append(cl['id'])
                                    genMuscleListFromComp(output_id_list, compound_id_list, muscle_checklist)
                                    counter = counter + 1
                                    break

                if counter < energy:
                    if checkMissingMuscle(muscle_checklist) == False:
                        # check out single lists first if muscle is missing
                        for key, value in muscle_checklist.items():
                            if value == False:
                                if key in single_id_dict.keys():
                                    random.shuffle(single_id_dict[key])
                                    output_id_list.append(single_id_dict[key][0])
                                    genMuscleListFromSing(key, muscle_checklist)
                                    counter = counter + 1
                                    if counter == energy:
                                        break
                    while counter < energy:
                        for cl in compound_id_list:
                            if cl['id'] not in output_id_list:
                                output_id_list.append(cl['id'])
                                counter = counter + 1
                                if counter == energy:
                                    break

            print("Output Id List")
            print(output_id_list)
            for i in output_id_list:
                entry = DB.find_one("test1", {"id": i})
                # print(entry)
                exercise_name = entry['exercise name']
                description = entry['description']
                muscle = entry['muscle']
                video = entry['video']
                equipment = entry["equipment"]
                level = entry["level"]

                output_dict = {
                    "id": i,
                    "exercise": exercise_name,
                    "description": description,
                    "video": video,
                    "muscle": muscle,
                    "level": level,
                    "equipment": equipment
                }
                output_list.append(output_dict)

        if not output_id_list:

            if equip_usr_list:
                equip_usr_list.append("Bodyweight")
                equip_checklist = {}
                # initialise the equipment checklist
                for e in equip_usr_list:
                    equip_checklist[e] = []

                # need to input fitness level checks here

                for record in collection:
                    equipment = record['equipment']
                    level = convertFitnessLevel(record['level'])

                    if level > usr_fitness_level:
                        continue
                    if equipment in equip_usr_list:
                        # print(equipment)
                        exercise_id = record['id']
                        # print(exercise_id)
                        # print(equip_checklist[equipment])
                        equip_checklist[equipment].append(exercise_id)

                print("Equipment checklist")
                print(equip_checklist)

                counter = energy

                while counter > 0:
                    for key, value in equip_checklist.items():
                        random.shuffle(value)
                        if value[0] not in output_id_list:
                            output_id_list.append(value[0])
                            counter = counter - 1
                            if counter == 0:
                                break

                print("Output Id List")
                print(output_id_list)

                for i in output_id_list:
                    entry = DB.find_one("test1", {"id": i})
                    exercise_name = entry['exercise name']
                    description = entry['description']
                    muscle = entry['muscle']
                    video = entry['video']
                    equipment = entry["equipment"]
                    level = entry['level']

                    output_dict = {
                        "id": i,
                        "exercise": exercise_name,
                        "description": description,
                        "video": video,
                        "muscle": muscle,
                        "level": level,
                        "equipment": equipment
                    }
                    output_list.append(output_dict)

            else:
                # For exercises, print out all records
                tricep_id_list = []
                quad_id_list = []
                ham_id_list = []

                # need to input fitness level here
                for record in collection:
                    exercise_id = record['id']
                    muscle = record['muscle']
                    exer_level = convertFitnessLevel(record['level'])

                    if "Triceps" in muscle:
                        if exer_level == usr_fitness_level:
                            tricep_id_list.append(exercise_id)
                    elif "Quads" in muscle:
                        if exer_level == usr_fitness_level:
                            quad_id_list.append(exercise_id)
                    elif "Hamstrings" in muscle:
                        if exer_level == usr_fitness_level:
                            ham_id_list.append(exercise_id)

                # assume energy level will always be divisible by 3
                num_per_muscle = int(energy / 3)

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
                # print(default_list) #working fine
                for m_list in default_list:
                    for i in m_list:
                        entry = DB.find_one("test1", {"id": i})
                        # print(entry)
                        exercise_name = entry['exercise name']
                        description = entry['description']
                        muscle = entry['muscle']
                        video = entry['video']
                        equipment = entry["equipment"]
                        level = entry['level']

                        output_dict = {
                            "id": i,
                            "exercise": exercise_name,
                            "description": description,
                            "video": video,
                            "muscle": muscle,
                            "level": level,
                            "equipment": equipment
                        }
                        output_list.append(output_dict)
                        # print(output_list)

        return output_list, 200


# http://127.0.0.1:5000/exercises/1
@api.route('/exercises/<int:exercise_id>')
class ExerciseCollection(Resource):
    def get(self, exercise_id):
        # Connect to mongodb mlab
        collection = DB.find_one("test1", {"id": exercise_id})

        if not collection:
            api.abort(404, "Collection id {} not found".format(exercise_id))

        exercise = collection['exercise name']
        muscle = collection['muscle']
        equipment = collection['equipment']
        video = collection['video']
        description = collection['description']

        output = {"id": exercise_id, "exercise": exercise, "muscle": muscle, "equipment": equipment, "video": video,
                  "description": description}

        return output, 200

    def put(self, exercise_id):
        payload = request.form

        # Connect to mongodb mlab
        collection = DB.find_one("test1", {"id": exercise_id})

        exercise = payload['exercise name']
        muscle = payload['muscle']
        equipment = payload['equipment']
        video = payload['video']
        description = payload['description']

        new_entry = {"id": exercise_id, "exercise": exercise, "muscle": muscle, "equipment": equipment, "video": video,
                     "description": description}

        updateEntry(new_entry, "exercises", {"id": exercise_id})

        return new_entry, 200, None


# returns list of all users
@api.route('/users')
class AllUsers(Resource):
    # @api.expect(parser)
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
    # @api.expect(parser)
    def get(self, username):
        # Obtain collection
        collection = DB.find_one("users", {"username": username})

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


# get.request("http://127.0.0.1:5001/users/<user_id>/workouts")

@api.route('/users/<string:username>/workouts')
class WorkoutsPerUser(Resource):
    def get(self, username):
        output_list = []
        collection = DB.find_one("workouts", {"username": username})

        # Abort if collection not found
        if not collection:
            api.abort(404, "There are no collections in the database")

        for record in collection:
            output_dict = {
                "id": record['id'],
                "workout_name": record['workout_name'],
                "workout_list": record['workout_list']
            }
            output_list.append(output_dict)

        return output_list, 200

    # put.request("http://127.0.0.1:5001/users/<user_id>/workouts/<workout_id>")
    # if a user does not exist, create a new entry for that user

    # post.request("http://127.0.0.1:5001/users/<username>/workouts")
    # create new entry in db when user is initially created

    def post(self, username):

        collection = DB.find_all("workouts")
        max_id = 0
        exists = 0
        exist_id = 0
        for record in collection:
            entry_id = record['id']
            check_user = record['username']
            if entry_id > max_id:
                max_id = entry_id
            if check_user == username:
                return {}, 200

        max_id = max_id + 1
        workout_list = []
        new_entry = {"id": max_id, "workout_name": "untitled", "workout_list": workout_list}

        DB.insert("workouts", new_entry)

        return new_entry, 200

    def put(self, username):

        payload = request.json
        payload = json.loads(payload)

        collection = DB.find_one("workouts", {"username": username})

        # Abort if collection not found
        if not collection:
            api.abort(404, "There are no collections in the database")

        new_entry = {"id": collection["id"], "username": username, "workout_list": payload['workout_list']}

        DB.update("workouts", {"username": username}, new_entry)

        return new_entry, 200

    # Method used by developers only. Exercises will not be generated by the user


# def post(self)

if __name__ == '__main__':
    app.run(port=5001, debug=True)