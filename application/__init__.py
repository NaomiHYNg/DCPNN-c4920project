import json
import os
import re

from flask import Flask, render_template, redirect, url_for, request
import requests
# user management
from flask_login import LoginManager
from flask_login import login_required
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Mail

app = Flask(__name__)

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx',

    MAIL_SERVER = 'smtp.googlemail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'natwai.mailservice@gmail.com',
    MAIL_PASSWORD = 'natwai1994',
    MAIL_DEFAULT_SENDER = 'natwai.mailservice@gmail.com'
)

# login
login = LoginManager(app) # exported into models.py
login.login_view = 'login'
mail = Mail(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():

    workouts = get_workouts()
    programs = get_programs()

    if request.method == 'POST':

        try:
            if request.form['action'] == "delete saved workout":
                for workout in workouts:
                    if str(workout['workout_id']) == str(request.form['delete_id']):
                        workouts.remove(workout)
                query = "http://127.0.0.1:5001/users/" + current_user.username + "/workouts/" + str(request.form['delete_id'])
                requests.delete(query)

                # Also delete any programs that included that saved workout:
                for program in programs:
                    for workout in program['program']:
                        if str(workout['workout_id']) == str(request.form['delete_id']):
                            programs.remove(program)
                            query = "http://127.0.0.1:5001/users/" + current_user.username + "/programs/" + str(
                                program['program_id'])
                            requests.delete(query)

            elif request.form['action'] == "save program":

                program = []
                program.append(str(request.form['Monday Workout']))
                program.append(str(request.form['Tuesday Workout']))
                program.append(str(request.form['Wednesday Workout']))
                program.append(str(request.form['Thursday Workout']))
                program.append(str(request.form['Friday Workout']))
                program.append(str(request.form['Saturday Workout']))
                program.append(str(request.form['Sunday Workout']))

                i = 0
                for day in program:

                    if day == "Rest":

                        program[i] = {"workout_id": -1, "username": current_user.username, "workout_name": "Rest",
                            "workout": "Rest"}

                        i += 1
                        continue

                    # day is the id of the workout if not Rest Day
                    query = "http://127.0.0.1:5001/users/" + current_user.username + "/workouts/" + day
                    workout = json.loads(requests.get(query).content)

                    program[i] = workout

                    i += 1

                program_name = str(request.form['program_name'])

                payload = {
                    "program_name": program_name,
                    "username": current_user.username,
                    "program": program
                }
                headers = {"Content-Type": "application/json"}

                url = "http://127.0.0.1:5001/users/" + current_user.username + "/programs"

                requests.post(url, json=json.dumps(payload), headers=headers)

                # Programs has changed as you added a new one, update programs
                programs = get_programs()
            # Delete a Program
            elif request.form['action'] == "delete program":
                for program in programs:
                    if str(program['program_id']) == str(request.form['delete_id']):
                        programs.remove(program)
                query = "http://127.0.0.1:5001/users/" + current_user.username + "/programs/" + str(request.form['delete_id'])
                requests.delete(query)

        except Exception as e:
            pass

        workouts=get_workouts()
        programs = get_programs()

        return render_template('home.html', programs=programs, workouts=workouts, username=request.form['username'])

    return render_template('home.html', programs=programs, workouts=workouts)

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    workouts = get_workouts()
    programs = get_programs()

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

                # Refresh
                workouts = get_workouts()

                return render_template('summary.html', programs=programs, workouts=workouts, level=request.form['fitnessLevel'], energy=request.form['energy'], exercise_list=exercise_list,
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

                return render_template('summary.html', programs=programs, workouts=workouts, delete_status=delete_status, level=request.form['fitnessLevel'],
                                       energy=request.form['energy'], exercise_list=exercise_list,
                                       energy_value=request.form['energy_value'], username=request.form['username'])
            # Loading a saved workout
            elif request.form['action'] == "begin saved workout":

                for workout in workouts:
                    if str(workout['workout_id']) == str(request.form['workout_id']):
                        saved_workout = workout

                print(saved_workout['workout'])

                return render_template('summary.html', programs=programs, energy_value=6, level=current_user.fitness, energy=saved_workout['workout_name'], workouts=workouts, exercise_list=saved_workout['workout'], username=request.form['username'])
        except Exception as e:
            pass


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

            energy = "Energy Level: " + energy

            return render_template('summary.html', programs=programs, workouts=workouts, level=level, energy=energy, exercise_list=content, raw_exercise_list=response.content, energy_value=request.form['energy'], username=request.form['username'])

        except Exception as e:
            print(e)
            error = "Error connecting to server!"

    return render_template('home.html', programs=programs, workouts=workouts, error=error)

@app.route('/generate', methods=['GET', 'POST'])
def generate():

    workouts = get_workouts()
    programs = get_programs()

    if request.method == 'POST':

        muscles = []
        equipments = []

        for muscle in request.form.getlist('muscle'):
            muscles.append(muscle)

        for equipment in request.form.getlist('equipment'):
            equipments.append(equipment)

        return render_template('generate.html', programs=programs, workouts=workouts, level=request.form.getlist('fitnessLevel'), muscles=request.form.getlist('muscle'), equipments=request.form.getlist('equipment'), username=request.form['username'], energy=request.form['energy'])

    return render_template('generate.html')

@app.route('/complete', methods=['GET', 'POST'])
def complete():

    programs = get_programs()
    workouts = get_workouts()

    if request.method == 'POST':
        return render_template('complete.html', programs=programs, workouts=workouts)
    return render_template('complete.html', programs=programs, workouts=workouts)

@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))

    return dict(mdebug=print_in_console)


def get_workouts():
    query = "http://127.0.0.1:5001/users/" + current_user.username + "/workouts"

    response = requests.get(query)
    print("Status Code for workouts: " + str(response))

    workouts = response.content
    workouts = json.loads(workouts)

    return workouts

def get_programs():
    query = "http://127.0.0.1:5001/users/" + current_user.username + "/programs"

    response = requests.get(query)
    print("Status Code for programs: " + str(response))

    programs = response.content
    programs = json.loads(programs)

    # Define days of the week for programs
    # len(programs) = 7

    for program in programs:
        program['program'][0]['day'] = 'Monday'
        program['program'][1]['day'] = 'Tuesday'
        program['program'][2]['day'] = 'Wednesday'
        program['program'][3]['day'] = 'Thursday'
        program['program'][4]['day'] = 'Friday'
        program['program'][5]['day'] = 'Saturday'
        program['program'][6]['day'] = 'Sunday'

    return programs

