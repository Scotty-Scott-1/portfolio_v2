#!/usr/bin/python3
"""
starts a Flask web application
"""

from flask import Flask, render_template, request, redirect, session as logged_in_session, send_file, url_for
from datetime import datetime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, Sequence, Date, DateTime, Boolean, Enum, Text, ForeignKey
from sqlalchemy import MetaData, Sequence, or_, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from create_tables import Users
from create_tables import User_preferences, User_pics, Likes, Matches
from sys import argv
import base64
import random
from geopy.distance import geodesic

import os
import cv2




app = Flask(__name__, static_url_path='/static')
app.secret_key = "FRAISE"

user_name = argv[1]
password = argv[2]
db_name = argv[4]
host = argv[3]
db_url = "mysql+mysqldb://{}:{}@{}/{}".format(user_name, password, host, db_name)

engine = create_engine(db_url, echo=True, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

@app.route('/', strict_slashes=False)
def home():
    logged_in_session.clear()
    return render_template('homepage.html')

@app.route('/signin', strict_slashes=False, methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        form_data = request.json
        session = Session()

        user = session.query(Users).filter_by(user_name=form_data["user_name"]).first()

        if user and check_password_hash(user.user_password, form_data["user_password"]):
            logged_in_session["user_id"] = user.id
            user.latitude = form_data["latitude"]
            user.longitude = form_data["longitude"]

            today = datetime.today()
            age = datetime.strptime(str(user.date_of_birth), "%Y-%m-%d")
            real_age = today.year - age.year - ((today.month, today.day) < (age.month, age.day))
            user.age = real_age

            session.commit()

            result_user_name = user.user_name
            result_user_id = user.id
            session.close()


            return {"Success": "logged in: {}. User id: {}".format(result_user_name, result_user_id)}
        else:
            session.close()
            return {"Failed": "Username or password incorrect"}




@app.route('/signup', strict_slashes=False, methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('create-account.html')
    elif request.method == 'POST':
        form_data = request.json
        session = Session()

        existing_user = session.query(Users).filter_by(user_name=form_data["user_name"]).first()
        if existing_user:
            session.close()
            return {"Failed": "User name already exists"}


        hashed_password = generate_password_hash(form_data["user_password"])
        form_data["user_password"] = hashed_password

        new_user = Users(**form_data)
        with Session() as session:
            session.add(new_user)

            today = datetime.today()
            age = datetime.strptime(str(new_user.date_of_birth), "%Y-%m-%d")
            real_age = today.year - age.year - ((today.month, today.day) < (age.month, age.day))
            new_user.age = real_age

            session.commit()
            return {"Success": "created new user"}

@app.route('/dashboard/', strict_slashes=False)
def dashboard():
    session = Session()
    user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
    profile_pic = session.query(User_pics).filter_by(user_id=logged_in_session.get("user_id")).order_by(User_pics.id.desc()).first()
    session.close()
    if profile_pic:
        return render_template('dashboard2.html', user=user, profile_pic=profile_pic.path)
    return render_template('dashboard.html', user=user)

@app.route('/preferences/', strict_slashes=False, methods=['GET', 'POST'])
def preferences():
    session = Session()
    preferences = session.query(User_preferences).filter_by(user_id=logged_in_session.get("user_id")).first()
    if request.method == "GET":
        return render_template('update-preferences.html', preferences=preferences)
    elif request.method == 'POST':
        if preferences:
            form_data = request.json
            preferences.min_age = form_data["min_age"]
            preferences.max_age = form_data["max_age"]
            preferences.distance = form_data["distance"]
            preferences.gender = form_data["gender"]
            preferences.intentions = form_data["intentions"]
            session.commit()
            session.close()

            session = Session()
            user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
            user.is_active = True
            session.commit()
            session.close()

            return {"success": "updated exiting preferences"}
        else:
            form_data = request.json
            new_preferences = User_preferences()
            new_preferences.min_age = form_data["min_age"]
            new_preferences.max_age = form_data["max_age"]
            new_preferences.distance = form_data["distance"]
            new_preferences.gender = form_data["gender"]
            new_preferences.intentions = form_data["intentions"]
            new_preferences.user_id = logged_in_session.get("user_id")

            session.add(new_preferences)
            session.commit()
            session.close()

            session = Session()
            user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
            user.is_active = True
            session.commit()
            session.close()

            return {"Success": "created new preferences"}

@app.route('/camera/', strict_slashes=False, methods=['GET', 'POST'])
def camera():
        if request.method == "GET":
            return render_template('get_pic.html')
        if request.method == "POST":
            data = request.json

            _, encoded = data["ImageData"].split(",", 1)
            image_bytes = base64.b64decode(encoded)

            session = Session()
            user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()

            filename = "{}{}.png".format(user.user_name, random.random());

            with open("static/images/user_pics/" + filename, "wb") as file:
                file.write(image_bytes)

            new_user_pics = User_pics()
            new_user_pics.user_id = user.id
            new_user_pics.file_name = filename
            new_user_pics.path = "static/images/user_pics/{}".format(filename)
            print(new_user_pics.path)

            session.add(new_user_pics)
            user.profile_pic_path = new_user_pics.path
            session.commit()

            session.close()

            return {"success": "saved file"}

@app.route('/swipe/', strict_slashes=False, methods=['GET', 'POST'])
def swipe():

    if request.method == "GET":
        session = Session()
        prefs = session.query(User_preferences).filter_by(user_id=logged_in_session.get("user_id")).first()
        pref_gender = prefs.gender
        pref_min_age = prefs.min_age
        pref_max_age = prefs.max_age
        pref_distance = prefs.distance
        pref_intention = prefs.intentions
        session.close()

        session = Session()
        user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
        this_user_age = user.age
        this_user_user_name = user.user_name
        this_user_latitude = user.latitude
        this_user_longitude = user.longitude
        session.close()

        print("\n\n\n\n")
        print("The preferred gender is {}. Aged between {} and {}. Living {}km from the user. The user is interested in {}. The user is {} years old. Their username is {}."
            .format(pref_gender, pref_min_age, pref_max_age, pref_distance, pref_intention, this_user_age, this_user_user_name))

        print("\n\n\n\n")

        session = Session()
        candiate_list = session.query(Users).filter_by(gender=pref_gender).filter(Users.age <= pref_max_age).filter(Users.age >= pref_min_age).all()
        result = []
        for candidate in candiate_list:
            user_prefs = session.query(User_preferences).filter_by(user_id=candidate.id).first()
            if user_prefs and user_prefs.intentions == pref_intention:
                result.append(candidate)

        result1 = []


        session = Session()
        user_exisiting_likes = session.query(Likes).filter_by(user_1_id=logged_in_session.get("user_id")).all()
        for candidate1 in result:
            found = False
            for like in user_exisiting_likes:
                if like.user_2_id == candidate1.id:
                    found = True
                    break
            if not found:
                result1.append(candidate1)


        distance_dict = {}
        result2 = []
        print("\n\n")
        print("the user's location is {}, {}. Their username is {}. The max distance this user wants is {}.".format(this_user_latitude, this_user_longitude, this_user_user_name, pref_distance))
        for candidate1 in result1:
            print("the candiates location is {} {}. Their username is {}.".format(candidate1.latitude, candidate1.longitude, candidate1.user_name))
            candidate_location = "{}, {}".format(candidate1.latitude, candidate1.longitude)
            user_location = "{}, {}".format(this_user_latitude ,this_user_longitude)
            distance = geodesic(candidate_location, user_location).kilometers
            real_distance = int(distance)
            print("distnace = {}".format(real_distance))
            if real_distance <= pref_distance:
                result2.append(candidate1)
                distance_dict[candidate1.user_name] = real_distance


        print("result = ")
        for a in result:
            print(a.user_name)

        print("result 1 = ")
        for a in result1:
            print(a.user_name)


        print("result 2 = ")
        for a in result2:
            print(a.user_name)

        shuffled_list = result2.copy()
        random.shuffle(shuffled_list)

        print("\n\n")
        print("shuffled list")

        for a in shuffled_list:
            print(a.user_name)


        print("\n\n")
        session.close()
        return render_template('swipe.html', result=shuffled_list, distance=distance_dict)

    elif request.method == "POST":
        form_data = request.json

        with Session() as session:

            user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
            likee = session.query(Users).filter_by(user_name=form_data["canidate_user_name"]).first()
            if likee:
                new_like = Likes()
                new_like.user_1_id = logged_in_session.get("user_id")
                new_like.user_2_id = likee.id

                """check if likee and has already liked the liker."""
                likee_liked_user = session.query(Likes).filter_by(user_1_id=likee.id, user_2_id=logged_in_session.get("user_id")).first()

                if likee_liked_user:
                    new_like.is_matched = True
                    likee_liked_user.is_matched = True

                    new_match = Matches()
                    new_match.user_1_id = logged_in_session.get("user_id")
                    new_match.user_2_id = likee.id

                    session.add(new_like)
                    session.add(new_match)
                    session.commit()

                    print("\n\n\n")
                    print("CONGRATULATIONS: You have matched with {}".format(likee.first_name))
                    print("\n\n\n")
                    return "New Match"

                else:
                    session.add(new_like)
                    session.commit()
                    print("\n\n\n")

                    return {"success": "created a like"}

        return {"error": "user not found"}



@app.route('/update-user-info/', strict_slashes=False, methods=['GET', 'POST'])
def update_user_info():
    if request.method == "GET":
        session = Session()
        user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
        session.close()
        return render_template('update_user_info.html', user=user)
    if request.method == "POST":
        form_data = request.json
        session = Session()
        user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()

        user.first_name = form_data["first_name"]
        user.last_name = form_data["last_name"]
        user.date_of_birth = form_data["date_of_birth"]
        user.email = form_data["email"]
        user.user_name = form_data["user_name"]
        user.gender = form_data["gender"]
        user.bio = form_data["bio"]

        session.commit()
        session.close()

        return {"success": "updated user info"}


@app.route('/new_match/', strict_slashes=False, methods=['GET'])
def new_match():
    if request.method == "GET":
        this_user = logged_in_session.get("user_id")
        with Session() as session:
            match = session.query(Matches).filter(or_(Matches.user_1_id == this_user, Matches.user_2_id == this_user)).order_by(desc(Matches.created_at)).first()
            if match is None:
                    print("\n\n\n")
                    print("redirected as there are no matches")
                    print("\n\n\n")
                    return redirect(url_for("dashboard"))
            print("user 1: {}".format(match.user_1_id))
            print("user 2: {}".format(match.user_2_id))
            if match.user_1_id == this_user and not match.user_1_notified:
                likee = session.query(Users).filter_by(id=match.user_2_id).first()
                match.user_1_notified = True
                name = likee.first_name
                profile_pic = likee.profile_pic_path
                session.commit()
                return render_template('new_match.html', name=name, profile_pic=profile_pic)
            if match.user_2_id == this_user and not match.user_2_notified:
                likee = session.query(Users).filter_by(id=match.user_1_id).first()
                match.user_2_notified = True
                name = likee.first_name
                profile_pic = likee.profile_pic_path
                session.commit()
                return render_template('new_match.html', name=name, profile_pic=profile_pic)
        print("\n\n\n")
        print("redirected as the user has been notified about the lastest passive match")
        print("\n\n\n")
        return redirect(url_for("dashboard"))

@app.route('/new_match_passive/', strict_slashes=False, methods=['GET'])
def new_match_passive():
    if request.method == "GET":
        this_user = logged_in_session.get("user_id")
        with Session() as session:
            matches = session.query(Matches).filter(or_(Matches.user_1_id == this_user, Matches.user_2_id == this_user)).order_by(desc(Matches.created_at)).all()
            if matches is None:
                    print("\n\n\n")
                    print("redirected as there are no matches")
                    print("\n\n\n")
                    return redirect(url_for("dashboard"))

            names = []
            profile_pics = []
            my_dict = {}

            for match in matches:

                if match.user_1_id == this_user and not match.user_1_notified:
                    likee = session.query(Users).filter_by(id=match.user_2_id).first()
                    match.user_1_notified = True
                    name = likee.first_name
                    profile_pic = likee.profile_pic_path
                    session.commit()
                    names.append(name)
                    profile_pics.append(profile_pic)
                if match.user_2_id == this_user and not match.user_2_notified:
                    likee = session.query(Users).filter_by(id=match.user_1_id).first()
                    match.user_2_notified = True
                    name = likee.first_name
                    profile_pic = likee.profile_pic_path
                    session.commit()
                    names.append(name)
                    profile_pics.append(profile_pic)

            if names:
                if profile_pics:
                    zipped = zip(names, profile_pics)
                    return render_template('new_match_passive.html', zipped=zipped)


        print("\n\n\n")
        print("redirected as the user has been notified about the lastest passive matches")
        print("\n\n\n")
        return redirect(url_for("dashboard"))

@app.route('/view_matches/', strict_slashes=False, methods=['GET'])
def view_matches():
    with Session() as session:
        this_user = logged_in_session.get("user_id")
        user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
        matches = session.query(Matches).filter(or_(Matches.user_1_id == this_user, Matches.user_2_id == this_user)).order_by(desc(Matches.created_at)).all()
        if matches is None:
                print("\n\n\n")
                print("redirected as there are no matches")
                print("\n\n\n")
                return redirect(url_for("dashboard"))
        my_list = []


        for match in matches:
            if match.user_1_id == this_user:
                likee = session.query(Users).filter_by(id=match.user_2_id).first()
                my_list.append(likee)
            if match.user_2_id == this_user:
                likee = session.query(Users).filter_by(id=match.user_1_id).first()
                my_list.append(likee)
        distance_dict = {}
        for candidate1 in my_list:
            candidate_location = "{}, {}".format(candidate1.latitude, candidate1.longitude)
            user_location = "{}, {}".format(user.latitude , user.longitude)
            distance = geodesic(candidate_location, user_location).kilometers
            real_distance = int(distance)
            distance_dict[candidate1.user_name] = real_distance

        return render_template('view_matches.html', result=my_list, user=user, distance=distance_dict)






if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
