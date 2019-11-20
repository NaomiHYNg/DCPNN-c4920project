<<<<<<< HEAD
=======
import json
import re

from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        return render_template('login.html')

    return render_template('login.html', error=error)

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':

        if request.form['username']:
            login_status="Logged in as " + request.form['username'] + "."
        else:
            login_status="Not signed in."

        return render_template('home.html', login_status=login_status, username=request.form['username'])

    return render_template('home.html', login_status="Not signed in.")

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    return render_template('signup.html', login_status="Not signed in.")


@app.route('/about/', methods=['GET', 'POST'])
def about():

    if request.method == 'POST':
        return render_template('about.html', username=request.form['username'])

    return render_template('about.html')

@app.route('/history/', methods=['GET', 'POST'])
def history():

    if request.method == 'POST':
        return render_template('history.html', username=request.form['username'])

    return render_template('history.html')

@app.route('/contact/', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':
        return render_template('contact.html', username=request.form['username'])

    return render_template('contact.html')

@app.route('/summary', methods=['GET', 'POST'])
def summary():

    if request.method == 'POST':

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

            if request.form['energy'] == '3':
                energy = "LOW"
            elif request.form['energy'] == '6':
                energy = "MODERATE"
            elif request.form['energy'] == '9':
                energy = "HIGH"

            return render_template('summary.html', energy=energy, exercise_list=content, energy_value=request.form['energy'], username=request.form['username'])

        except Exception as e:
            print(e)
            error = "Error connecting to server!"

    return render_template('home.html', error=error)

@app.route('/generate', methods=['GET', 'POST'])
def generate():

    if request.method == 'POST':

        muscles = []
        equipments = []

        for muscle in request.form.getlist('muscle'):
            muscles.append(muscle)

        for equipment in request.form.getlist('equipment'):
            equipments.append(equipment)

        return render_template('generate.html', level=request.form.getlist('fitnessLevel'), muscles=request.form.getlist('muscle'), equipments=request.form.getlist('equipment'), username=request.form['username'], energy=request.form['energy'])

    return render_template('generate.html')

@app.route('/complete', methods=['GET', 'POST'])
def complete():

    return render_template('complete.html')

@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))

    return dict(mdebug=print_in_console)

if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> Darren
