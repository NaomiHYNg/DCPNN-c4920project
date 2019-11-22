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
        user.pop('_id', None) # dont need this when creating User object
        if user and User.check_password(user['password'], form.password.data):
            user_obj = User(user)#User(username=user['username'])
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
        # create dictionary to pass to User constructor
        info = {
            "firstname": form.firstname.data, 
            "lastname": form.lastname.data, 
            "username": form.username.data, 
            "email": form.email.data, 
            "fitness" : form.fitness.data,
            "weight" : form.weight.data,
            "goalweight" : form.goalweight.data
            }
        user = User(info)
        # hash is generated and stored
        user.set_password(form.password.data)
        user.set_goal(form.goal.data)
        # add user to db
        user.add()
        # user can now log in
        #return redirect(url_for('login'))
        # or log user in and go to home
        login_user(user)
        return redirect(request.args.get("next") or url_for("home"))
        
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user() #loginManager function
    return redirect(url_for('login'))

@app.route('/user/<username>')
@login_required
def user(username):
    # Obtain collection
    collection = DB.find_one("users", {"username" : username})
    # Abort if collection not found
    if not collection:
        api.abort(404, "There are no collections in the database")
    collection.pop('_id', None)
    user = User(collection)#User(username=collection['username'])

    #return user.__dict__
    return render_template('profile.html', user=user)

    

