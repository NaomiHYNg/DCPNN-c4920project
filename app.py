import json
from pymongo import MongoClient
from bson.json_util import dumps
# import requests
from flask import Flask
from flask import request, jsonify
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse

import re
import random
from database import DB

# Helper Functions
app = Flask(__name__)
api = Api(app)
DB.init()

# Fitness levels in integer form
BEGINNER = 1
INTEMEDIATE = 2
ADVANCED = 3


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
parser.add_argument('level', required=True)


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
        collection = DB.find_all("exercises")

        # Abort if collection not found
        if not collection:
            api.abort(404, "There are no collections in the database")

        print("GENERATING EXERCISES BASED ON:")
        print("- ENERGY LEVEL: {}".format(energy))
        print("- FITNESS LEVEL: {}".format(usr_fitness_level))
        print("- MUSCLE LIST: {}".format(usr_muscle_list))
        print("- EQUIPMENT LIST: {}".format(equip_usr_list))

        output_list = []
        output_id_list = []  # List of exercise ids only

        # If the user has muscle groups selected
        if usr_muscle_list:

            single_id_dict = {}  # Each muscle is a key of the dictionary
            compound_id_list = []  # List of dictionaries {id: len(intersection)}
            muscle_checklist = dict.fromkeys(usr_muscle_list, False)  # Create muscle checklist

            # For each exercise, find the intersection between the user's muscle input list and the muscle list in the exercise
            for record in collection:
                muscle_list = record['muscle']
                # print(record['exercise name'])
                exercise_id = record['id']
                level = convertFitnessLevel(record['level'])

                # Check that the exercise is
                if (level > usr_fitness_level):
                    continue

                inter_list = intersection(usr_muscle_list, muscle_list)

                if len(inter_list) > 0:  # If there are entries in the intersection list

                    # If the exercise's associated muscle/s only matches one of the user's muscle preferences
                    if len(inter_list) == 1:
                        if inter_list[0] in single_id_dict:
                            single_id_dict[inter_list[0]].append(exercise_id)
                        else:
                            single_id_dict[inter_list[0]] = []
                            single_id_dict[inter_list[0]].append(exercise_id)

                    # If the exercise has more than one matching muscle
                    if len(inter_list) > 1:
                        temp_dict = {"id": exercise_id, "intersection_len": len(inter_list), "inter_list": inter_list,
                                     "level": level}
                        compound_id_list.append(temp_dict)

            # Prioritise exercises that have more intersections and have the same fitness level as user's selected level
            compound_id_list = sorted(compound_id_list, key=lambda i: (i['intersection_len'], i['level']), reverse=True)

            # EQUIPMENT SELECTION
            # Remove all items in list that do not match user's equipment selections

            temp_list_a = []

            if equip_usr_list:

                equip_usr_list.append("Bodyweight")
                for cl in compound_id_list:
                    record = DB.find_one("exercises", {"id": cl['id']})
                    equipment = record['equipment']
                    if equipment in equip_usr_list:
                        temp_list_a.append(cl)
                compound_id_list = temp_list_a

                temp_list_a = []

                for key, value in single_id_dict.items():
                    temp_list_a = []
                    for sl in value:
                        record = DB.find_one("exercises", {"id": sl})
                        equipment = record['equipment']
                        if equipment in equip_usr_list:
                            temp_list_a.append(sl)
                    single_id_dict[key] = temp_list_a

            print("GENERATED EXERCISE LISTS ARE:")
            print("COMPOUND LIST")
            print(compound_id_list)
            print("SINGLE LIST")
            print(single_id_dict)

            counter = energy

            # If there are more user required exercises than the compound list
            # Take all exercises from the compound list
            if energy > len(compound_id_list):
                for i in compound_id_list:
                    output_id_list.append(i['id'])
                    counter = counter - 1

                genMuscleListFromComp(output_id_list, compound_id_list, muscle_checklist)

                print("Muscle checklist")
                print(muscle_checklist)

                # Choose remaining exercises from the dictionary of single exercises

                total_single = 0
                total = len(output_id_list)

                # Count the number of exercises in the single list
                for key, value in single_id_dict.items():
                    total_single = total_single + len(value)

                # Count the number of exercises in both single and compound list
                total = total + total_single

                # If there are less exercises available than requested, take all single exercises
                if total <= counter:
                    for key, value in single_id_dict.items():
                        output_id_list.extend(value)
                else:
                    while counter > 0:
                        # If a muscle is missing from the muscle checklist
                        if checkMissingMuscle(muscle_checklist) == False:
                            for key, value in muscle_checklist.items():
                                if value == False:
                                    if key in single_id_dict.keys():
                                        if len(single_id_dict[key]) != 0:
                                            random.shuffle(single_id_dict[key])
                                            output_id_list.append(single_id_dict[key][0])
                                            genMuscleListFromSing(key, muscle_checklist)
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

            # If there are less user required exercises than the compound list
            # Randomly select the required number of exercises
            else:
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
                        # Check out single lists first if muscle is missing
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

            print("OUTPUT ID LIST")
            print(output_id_list)
            for i in output_id_list:
                entry = DB.find_one("exercises", {"id": i})
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

                # Initialise the equipment checklist
                for e in equip_usr_list:
                    equip_checklist[e] = []

                for record in collection:
                    equipment = record['equipment']
                    level = convertFitnessLevel(record['level'])

                    if level > usr_fitness_level:
                        continue
                    if equipment in equip_usr_list:
                        exercise_id = record['id']
                        equip_checklist[equipment].append(exercise_id)

                print("EQUIPMENT CHECKLIST")
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

                print("OUTPUT ID LIST")
                print(output_id_list)

                for i in output_id_list:
                    entry = DB.find_one("exercises", {"id": i})
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

                tricep_id_list = []
                quad_id_list = []
                ham_id_list = []

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

                # Assume energy level will always be divisible by 3
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

                for m_list in default_list:
                    for i in m_list:
                        entry = DB.find_one("exercises", {"id": i})

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

                        output_id_list.append(i)

                print("OUTPUT ID LIST")
                print(output_id_list)

        return output_list, 200


@api.route('/exercises/<int:exercise_id>')
class ExerciseCollection(Resource):
    def get(self, exercise_id):
        collection = DB.find_one("exercises", {"id": exercise_id})

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


@api.route('/users/<string:username>/workouts/<int:workout_id>')
class OneWorkoutPerUser(Resource):
    def get(self, username, workout_id):
        output_list = []
        collection = DB.find_one("workouts", {"workout_id": workout_id, "username": username})

        # Abort if collection not found
        if not collection:
            api.abort(404, "There are no collections in the database")

        output_dict = {
            "workout_id": collection['workout_id'],
            "username": username,
            "workout_name": collection['workout_name'],
            "workout": collection['workout']
        }

        return output_dict, 200

    def put(self, username, workout_id):

        # Consists of a dictionary {"workout_id": int, "username", "workout_name:" "", "workout": []}
        payload = request.json
        payload = json.loads(payload)

        collection = DB.find_one("workouts", {"workout_id": workout_id, "username": username})
        print(collection)

        # Abort if collection not found
        if not collection:
            api.abort(404, "There are no collections in the database")

        new_entry = {"workout_id": workout_id, "username": username, "workout_name": payload['workout_name'],
                     "workout": payload['workout']}

        DB.update("workouts", {"workout_id": workout_id}, new_entry)

        return new_entry, 200

    def delete(self, username, workout_id):

        collection = DB.find_one("workouts", {"workout_id": workout_id, "username": username})

        # Abort if collection not found
        if not collection:
            api.abort(404, "There are no collections in the database")

        DB.delete_one("workouts", {"workout_id": workout_id})

        return {}, 200


@api.route('/users/<string:username>/workouts')
class WorkoutsPerUser(Resource):
    # post.request("http://127.0.0.1:5001/users/<int:workout_id>/workouts")
    # create new entry in db when user is initially created

    def post(self, username):

        # consists of a dictionary {"workout_name:" "", "username": "", "workout": ""}
        payload = request.json
        payload = json.loads(payload)

        collection = DB.find_all("workouts")
        max_id = 0
        exists = 0
        exist_id = 0
        for record in collection:
            entry_id = record['workout_id']
            if entry_id > max_id:
                max_id = entry_id

        max_id = max_id + 1

        new_entry = {"workout_id": max_id, "username": username, "workout_name": payload['workout_name'],
                     "workout": payload['workout']}

        DB.insert("workouts", new_entry)

        return new_entry, 200


if __name__ == '__main__':
    app.run(port=5001, debug=True)