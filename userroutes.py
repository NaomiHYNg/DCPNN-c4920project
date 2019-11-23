from flask import Flask, render_template, redirect, url_for, request, flash
import requests
from flask_login import current_user, login_user, logout_user, login_required
# flask app
from application import *
# user management
from models import *
from forms import *
#from flask_mail import Message
#from application import app, mail
from confirmationEmail import *
from itsdangerous import URLSafeTimedSerializer
import datetime

def send_confirmation_email(user_email):
    confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
 
    confirm_url = url_for(
        'confirm_email',
        token=confirm_serializer.dumps(user_email, salt='email-confirmation-salt'),
        _external=True)
 
    html = render_template(
        'email_confirmation.html',
        confirm_url=confirm_url)
 
    send_email('Confirm Your Email Address', [user_email],'Confirm Your Email Address', html)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login()
    if form.validate_on_submit():
        user = DB.find_one("users", {"username": form.username.data})
        user.pop('_id', None) # dont need this when creating User object
        if user and not user['email_confirmed']:
            flash("Please confirm your email")
            return redirect(url_for('login'))
        elif user and User.check_password(user['password'], form.password.data):
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
        user.email_confirmation()
        # add user to db
        user.add()
        send_confirmation_email(user.email)
        flash('Please check your email to confirm your email address.')
        # user can now log in
        return redirect(url_for('login'))
        # or log user in and go to home
        #login_user(user)
        #return redirect(request.args.get("next") or url_for("home"))
        
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user() #loginManager function
    return redirect(url_for('login'))

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('login'))
 
    #user = User.query.filter_by(email=email).first()
    usr = DB.find_one("users", { "email" : email })
    usr.pop("_id")
    user = User(usr)
    if user.email_confirmed:
        flash('Account already confirmed. Please login.', 'info')
        return redirect(url_for('login'))
    else:
        #user.email_confirmed = True
        #user.email_confirmed_on = datetime.datetime.now()
        nowtime = datetime.datetime.now()
        user.confirm_email(datetime.datetime.now())

        flash('Thank you for confirming your email address!')
        return redirect(url_for('login'))

 
    return redirect(url_for('home'))

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

@app.route('/editweight', methods=['GET', 'POST'])
@login_required
def editweight():
    print(current_user.__dict__)
    form = EditWeight()
    if form.validate_on_submit():
        current_user.update_weight(form.weight.data)
        flash('Your changes have been saved.')
        return redirect(request.args.get("next") or url_for('user', username=current_user.username))

    return render_template('editweight.html', form=form)

@app.route('/editpassword', methods=['GET', 'POST'])
@login_required
def editpassword():
    form = EditPassword()
    if form.validate_on_submit():
        if User.check_password(current_user.password, form.old_password.data):
            current_user.change_password(form.password.data)
            flash('Your changes have been saved.')
            return redirect(request.args.get("next") or url_for('user', username=current_user.username))
        else:
            flash("Invalid password")
    #return user.__dict__
    return render_template('editpassword.html', form=form)
    

