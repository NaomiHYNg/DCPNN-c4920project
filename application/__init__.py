import json
import os
import re

from flask import Flask, render_template, redirect, url_for, request
import requests
# user management
from flask_login import LoginManager
from flask_login import login_required
from flask_login import current_user, login_user, logout_user, login_required

app = Flask(__name__)

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

# login
login = LoginManager(app) # exported into models.py
login.login_view = 'login'


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():

    workouts = get_workouts()

    if request.method == 'POST':

        try:
            if request.form['action'] == "delete saved workout":
                for workout in workouts:
                    if str(workout['workout_id']) == str(request.form['delete_id']):
                        workouts.remove(workout)
                query = "http://127.0.0.1:5001/users/" + current_user.username + "/workouts/" + str(request.form['delete_id'])
                requests.delete(query)

        except Exception as e:
            print("Normal Generation")

        return render_template('home.html', workouts=workouts, username=request.form['username'])

    return render_template('home.html', workouts=workouts)

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    workouts = get_workouts()

    if request.method == 'POST':


        try:
            # Saving a workout
            if request.form['action'] == "save workout":
                #User sent a save workout request

                username = request.form['username']
                workout_name = request.form['workout_name']

                exercise_list=request.form['workout']
                exercise_list=re.sub(",]", "]", exercise_list)
                exercise_list=eval(exercise_list)
                workout = exercise_list

                # PUT Request

                payload = {
                    "workout_name": workout_name,
                    "username": username,
                    "workout": workout
                }
                headers = {"Content-Type": "application/json"}

                url = "http://127.0.0.1:5001/users/" + username + "/workouts"

                success = requests.post(url, json=json.dumps(payload), headers=headers)



                return render_template('summary.html', workouts=workouts, level=request.form['fitnessLevel'], energy=request.form['energy'], exercise_list=exercise_list,
                                       energy_value=request.form['energy_value'], username=request.form['username'], save_disabled="disabled", save_status="Workout Saved!")
            # Deleting an exercise from the workout
            elif request.form['action'] == "delete workout":
                exercise_list = request.form['workout']
                exercise_list = re.sub(",]", "]", exercise_list)
                exercise_list = eval(exercise_list)
                delete_id = request.form['delete_id']

                for exercise in exercise_list:
                    if str(exercise['id']) == str(delete_id):
                        exercise_list.remove(exercise)

                # Deleting is not an option if there is only one exercise in the list
                if len(exercise_list) == 1:
                    delete_status = "display:none;"
                else:
                    delete_status = ""

                return render_template('summary.html', workouts=workouts, delete_status=delete_status, level=request.form['fitnessLevel'],
                                       energy=request.form['energy'], exercise_list=exercise_list,
                                       energy_value=request.form['energy_value'], username=request.form['username'])

        except Exception as e:
            print("Normal Generation")

        try:
            muscles = re.sub("\'", "\"", request.form['muscles'])
            muscles = json.loads(muscles)
            muscles = ",".join(muscles)

            query = "http://127.0.0.1:5001/exercises?energy=" + request.form['energy']

            if muscles:
                query = query + "&muscle=" + muscles

            equipment = re.sub("\'", "\"", request.form['equipments'])
            equipment = json.loads(equipment)
            equipment = ",".join(equipment)

            if equipment:
                query = query + "&equipment=" + equipment

            level = json.loads(re.sub("\'", "\"", request.form['fitnessLevel']))[0]

            if level:
                query = query + "&level=" + level

            print(query)

            response = requests.get(query)
            print("Status Code: " + str(response))

            content = json.loads(response.content)
            print(content)

            if request.form['energy'] == '3':
                energy = "LOW"
            elif request.form['energy'] == '6':
                energy = "MODERATE"
            elif request.form['energy'] == '9':
                energy = "HIGH"

            return render_template('summary.html', workouts=workouts, level=level, energy=energy, exercise_list=content, raw_exercise_list=response.content, energy_value=request.form['energy'], username=request.form['username'])

        except Exception as e:
            print(e)
            error = "Error connecting to server!"

    return render_template('home.html', workouts=workouts, error=error)

@app.route('/generate', methods=['GET', 'POST'])
def generate():

    workouts = get_workouts()

    if request.method == 'POST':

        muscles = []
        equipments = []

        for muscle in request.form.getlist('muscle'):
            muscles.append(muscle)

        for equipment in request.form.getlist('equipment'):
            equipments.append(equipment)

        return render_template('generate.html', workouts=workouts, level=request.form.getlist('fitnessLevel'), muscles=request.form.getlist('muscle'), equipments=request.form.getlist('equipment'), username=request.form['username'], energy=request.form['energy'])

    return render_template('generate.html')

@app.route('/complete', methods=['GET', 'POST'])
def complete():

    return render_template('complete.html')

@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))

    return dict(mdebug=print_in_console)

def get_workouts():
    query = "http://127.0.0.1:5001/users/" + current_user.username + "/workouts"

    response = requests.get(query)
    print("Status Code: " + str(response))

    workouts = response.content
    workouts = json.loads(workouts)

    return workouts



