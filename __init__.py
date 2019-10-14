import json

from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'password':
            error = 'Invalid username or password.'
        else:
            return render_template('home.html', username=request.form['username'])
    return render_template('login.html', error=error)

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        return render_template('home.html', username=request.form['username'])

    return render_template('home.html')

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
        response = requests.get("http://127.0.0.1:5001/exercises?energy=3")
        print("Status Code: " + str(response))
        content = json.loads(response.content)
        print(content)
        return render_template('summary.html', username=request.form['username'])

    return render_template('summary.html')

if __name__ == "__main__":
    app.run(debug=True)