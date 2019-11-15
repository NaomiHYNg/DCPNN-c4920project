from flask import Flask, render_template, redirect, url_for, request, flash
import requests
from flask_login import current_user, login_user, logout_user, login_required
# flask app
from application import app
# user management
from models import *
from forms import *

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login()
    if form.validate_on_submit():
        user = DB.find_one("users", {"username": form.username.data})
        if user and User.check_password(user['password'], form.password.data):
            user_obj = User(username=user['username'])
            login_user(user_obj)
            return redirect(request.args.get("next") or url_for("home"))
        else:
            flash("Invalid username or password")
    return render_template('login2.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        # hash is generated and stored
        user.set_password(form.password.data)
        #db.session.add(user)
        DB.insert("users", user)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

