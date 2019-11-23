import json
from pymongo import MongoClient
import requests
from flask import Flask
from flask import request, jsonify
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

workout = [
  {
    "id": 1,
    "exercise": "Stretch Push Up (On Risers)",
    "description": [
      "Assume a quadruped position between risers with your shoulders underneath your hands, toes tucked, and knees under hips.",
      "Place one hand on each riser and then extend one leg at a time. Assume a pushup position with the legs straight, elbows extended, and head in a neutral position looking at the floor.",
      "Slowly descend to the floor by retracting the shoulder blades and unlocking the elbows.",
      "Descend until your chest touches the bench.",
      "Push back to the starting point by extending the elbows and driving your palms into the floor.",
      "Repeat for the desired number of repetitions."
    ],
    "video": "https://www.youtube.com/embed/168QDdvpDag?rel=0",
    "muscle": [
      "Chest",
      "Abs",
      "Shoulders",
      "Triceps"
    ],
    "level": "Intermediate",
    "equipment": "Bodyweight"
  },
  {
    "id": 12,
    "exercise": "Knuckle Push Up",
    "description": [
      "Assume a quadruped position on the floor with your hands in a fist under your shoulders, toes tucked, and knees under hips.",
      "Extend one leg at a time and assume a push up position with the legs straight, elbows extended, and head in a neutral position looking at the floor.",
      "Slowly descend to the floor by retracting the shoulder blades and unlocking the elbows.",
      "Descend until the upper arms are parallel or your chest touches the floor.",
      "Push back to the starting point by extending the elbows and driving your knuckles into the floor.",
      "Repeat for the desired number of repetitions."
    ],
    "video": "https://www.youtube.com/embed/1vDmtRthKJ0?rel=0",
    "muscle": [
      "Chest",
      "Abs",
      "Shoulders",
      "Triceps"
    ],
    "level": "Intermediate",
    "equipment": "Bodyweight"
  },
  {
    "id": 18,
    "exercise": "Fingertip Push Ups",
    "description": [
      "Assume a quadruped position on the floor with your hands under your shoulders, toes tucked, and knees under hips.",
      "Press up on your finger tips and prevent your palms from touching the floor. Extend one leg at a time and assume a pushup position with the legs straight, elbows extended, and head in a neutral position looking at the floor.",
      "Slowly descend to the floor by retracting the shoulder blades and unlocking the elbows.",
      "Descend until the upper arms are parallel or your chest touches the floor.",
      "Push back to the starting point by extending the elbows and driving your palms into the floor.",
      "Repeat for the desired number of repetitions."
    ],
    "video": "https://www.youtube.com/embed/d1EHK4VbZIQ?rel=0",
    "muscle": [
      "Chest",
      "Abs",
      "Shoulders",
      "Triceps"
    ],
    "level": "Intermediate",
    "equipment": "Bodyweight"
  }
]

username = "admin"
payload = {
	"workout_name": "workout 2",
  "username": username, 
	"workout": workout
}
headers = {"Content-Type": "application/json"}

# CREATE A NEW WORKOUT ENTRY

url = "http://127.0.0.1:5001/users/" + username + "/workouts"
headers = {"Content-Type": "application/json"}

success = requests.post(url, json=json.dumps(payload), headers=headers)

url = "http://127.0.0.1:5001/users/" + username + "/workouts/1"
payload = {
	"workout_name": "slow workout",
  "username": username,
	"workout": workout
}

url = "http://127.0.0.1:5001/users/" + username + "/workouts/1"

# UPDATE THE WORKOUT USING THE ASSOCIATED WORKOUT ID

success = requests.put(url, json=json.dumps(payload), headers=headers)
print(success.json())

url = "http://127.0.0.1:5001/users/" + username + "/workouts/1"

# VIEW THE WORKOUT USING THE ASSOCIATED WORKOUT ID

success = requests.get(url)
print(success.json())

url = "http://127.0.0.1:5001/users/" + username + "/workouts/2"

#success = requests.delete(url)