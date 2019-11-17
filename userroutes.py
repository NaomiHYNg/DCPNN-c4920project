from flask import Flask, render_template, redirect, url_for, request, flash
import requests
from flask_login import current_user, login_user, logout_user, login_required
# flask app
from application import *
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
            login_user(user_obj, remember=form.remember_me.data)
            return redirect(request.args.get("next") or url_for("home"))
        else:
            flash("Invalid username or password")
            return redirect(url_for('login'))
    return render_template('login2.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        # hash is generated and stored
        user.set_password(form.password.data)
        user.set_email(form.email.data)
        #db.add(user)
        user.add()
        #user can now log in
        return redirect(url_for('login'))
        '''
        # or log user in and go to home
        login_user(user)
        return redirect(request.args.get("next") or url_for("home"))
        '''
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/user/<username>')
@login_required
def user(username):
    # Obtain collection
    collection = DB.find_one("users", {"username" : username})
    # Abort if collection not found
    if not collection:
        api.abort(404, "There are no collections in the database")
    
    user = User(username=collection['username'])

    return render_template('profile.html', user=user)

    

