#!/usr/bin/python3
"""
starts a Flask web application
"""

from flask import Flask, render_template, request, redirect, session as logged_in_session, url_for
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import or_, desc, asc
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from create_tables import Users
from create_tables import User_preferences, User_pics, Likes, Matches, Messages
from sys import argv
import base64
import random
from geopy.distance import geodesic
from email_validator import validate_email
from password_strength import PasswordPolicy
from flask_mail import Mail, Message

#Flask/mail/SQL Achemy configuration
app = Flask(__name__, static_url_path='/static')
app.secret_key = argv[8]

user_name = argv[1]
password = argv[2]
db_name = argv[4]
host = argv[3]
db_url = "mysql+mysqldb://{}:{}@{}/{}".format(user_name, password, host, db_name)

engine = create_engine(db_url, echo=True, pool_pre_ping=True)
Session = sessionmaker(bind=engine)


app.config['MAIL_SERVER'] = argv[7]
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = argv[5]
app.config['MAIL_PASSWORD'] = argv[6]
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail= Mail(app)

# log out fuction. Clears session cookie.
@app.route('/', strict_slashes=False)
def home():
	logged_in_session.clear()
	return render_template('homepage.html')

# On GET: Return the sign up html template.
# On POST: Check if username and password matches, update the user's real age and location, add
# session cookie, push changes to databse, check if email address verified.
# Return: "email not verified" then is forwarded to "/verify_email/" via js.
# Return: "email verified" then is forwarded to "/new_match_passive/" via js.
# Return: "incorrect username or password" then is alerted via js. No changes to database.
@app.route('/signin', strict_slashes=False, methods=['GET', 'POST'])
def signin():
	if request.method == 'GET':
		return render_template('signup.html')

	elif request.method == 'POST':
		form_data = request.json
		with Session() as session:

			user = session.query(Users).filter_by(user_name=form_data["user_name"]).first()

			# Check that user and password match
			if user and check_password_hash(user.user_password, form_data["user_password"]):

				# Update the session cookie with the user's ID.
				# This id will to used in SQL queries throughout the app.
				# On occasion the id will to be passed as arg to a template.
				logged_in_session["user_id"] = user.id

				# Update the users coordinates
				user.latitude = form_data["latitude"]
				user.longitude = form_data["longitude"]

				# Update the users real age
				today = datetime.today()
				age = datetime.strptime(str(user.date_of_birth), "%Y-%m-%d")
				real_age = today.year - age.year - ((today.month, today.day) < (age.month, age.day))
				user.age = real_age

				# Push the changes to the database
				session.commit()

				# Check if the email address has been verified
				if user.email_verified == False:
					return "email not verified"
				else:
					return "email verified"
			else:
				return "incorrect username or password"



# On GET: Return the the create-account html template with the minmum DOB
# as an arg. This is to make sure they are over 18.
# On POST: Create an account if the checks are are passed or send a error message front end.
# Return: "form incomplete" no changes to database then javascript: front end alert.
# Return: "User name already exists" no changes to database then javascript: front end alert.
# Return: "email already in use" no changes to database then javascript: front end alert.
# Return: "email not valid" no changes to database then javascript: front end alert.
# Return: "password not valid" no changes to database then javascript: front end alert.
# Return: "must be over 18" no changes to database then javascript: front end alert.
# Return: "created new user" push changes to databs then javascript: forward to "/signin".
@app.route('/signup', strict_slashes=False, methods=['GET', 'POST'])
def signup():
	if request.method == 'GET':

		# Calculate the minimum DOB accepted
		current_date = datetime.today()
		min_dob = current_date - timedelta(days=18*365) - timedelta(days=5)
		return render_template('create-account.html', min_dob=min_dob)

	elif request.method == 'POST':
		form_data = request.json
		with Session() as session:

			# Check that form is filled in
			for value in form_data.values():
				if value == "":
					return "form incomplete"

			# Check that another user does not have the same user_name
			existing_user = session.query(Users).filter_by(user_name=form_data["user_name"]).first()
			if existing_user:
				return "User name already exists"

			# Check that another user does not have the same email
			existing_user = session.query(Users).filter_by(email=form_data["email"]).first()
			if existing_user:
				if existing_user.email_verified == True:
					return "email already in use"

			# Check that email syntax is valid
			try:
				validate_email(form_data["email"])
			except Exception as e:
				return "email not valid"

			# Check that the password is is strong
			policy = PasswordPolicy.from_names(
				length=8,
				uppercase=1,
				numbers=1,
				special=1
			)
			strength = policy.test(form_data["user_password"])
			if strength:
				return "password not valid"

			# Hash the password
			hashed_password = generate_password_hash(form_data["user_password"])
			form_data["user_password"] = hashed_password

			# Create the new user
			new_user = Users(**form_data)
			session.add(new_user)


			# Check that the new user is over 18
			today = datetime.today()
			age = datetime.strptime(str(new_user.date_of_birth), "%Y-%m-%d")
			real_age = today.year - age.year - ((today.month, today.day) < (age.month, age.day))
			if real_age < 18:
				return "must be over 18"

			# Update real age
			new_user.age = real_age

			# Push changes to database
			session.commit()

			return "created new user"

# On GET: return a dashbaord with the profile pic updated or with a filler icon.
# If the email is not verifed, render the verification html template.
@app.route('/dashboard/', strict_slashes=False)
def dashboard():
	with Session() as session:
		# Get the current user instance
		user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()

		if user.email_verified == True:
			profile_pic = session.query(User_pics).filter_by(user_id=logged_in_session.get("user_id")).order_by(User_pics.id.desc()).first()
			if profile_pic:
				return render_template('dashboard2.html', user=user, profile_pic=profile_pic.path)
			return render_template('dashboard.html', user=user)
		else:
			return render_template('verification.html')

# Check if email verified else  forward to verification
# On GET: return the update preferences template with this user's preferences instance
# On POST: Update existing prefereces or if not exists create new instance
@app.route('/preferences/', strict_slashes=False, methods=['GET', 'POST'])
def preferences():
	with Session() as session:

		# Get this user instance and this user's preferences instance
		preferences = session.query(User_preferences).filter_by(user_id=logged_in_session.get("user_id")).first()
		this_user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()

		# Check if email verified
		if this_user.email_verified == False:
			return render_template('verification.html')

		if request.method == "GET":
			return render_template('update-preferences.html', preferences=preferences)

		elif request.method == 'POST':
			# Update existing preferences
			if preferences:
				form_data = request.json
				preferences.min_age = form_data["min_age"]
				preferences.max_age = form_data["max_age"]
				preferences.distance = form_data["distance"]
				preferences.gender = form_data["gender"]
				preferences.intentions = form_data["intentions"]
				this_user.is_active = True
				session.commit()
				return {"success": "updated exiting preferences"}
			else:
				# Create new preferences
				form_data = request.json
				new_preferences = User_preferences()
				new_preferences.min_age = form_data["min_age"]
				new_preferences.max_age = form_data["max_age"]
				new_preferences.distance = form_data["distance"]
				new_preferences.gender = form_data["gender"]
				new_preferences.intentions = form_data["intentions"]
				new_preferences.user_id = logged_in_session.get("user_id")

				session.add(new_preferences)
				this_user.is_active = True
				session.commit()
				return {"Success": "created new preferences"}

# On GET: return the get_pic html tempalte. Check if email verified
# On POST: get pic from js, parse and save to local storage. Update database with path
@app.route('/camera/', strict_slashes=False, methods=['GET', 'POST'])
def camera():

		if request.method == "GET":
			with Session() as session:
				user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
				if user.email_verified == False:
					return render_template('verification.html')
			return render_template('get_pic.html')

		if request.method == "POST":

			# Encode image data
			data = request.json
			_, encoded = data["ImageData"].split(",", 1)
			image_bytes = base64.b64decode(encoded)

			with Session() as session:
				user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()

				# Set file name and save to local storage
				filename = "{}{}.png".format(user.user_name, random.random());
				with open("static/images/user_pics/" + filename, "wb") as file:
					file.write(image_bytes)

				# Create a new instance of user_pics
				new_user_pics = User_pics()
				new_user_pics.user_id = user.id
				new_user_pics.file_name = filename
				new_user_pics.path = "static/images/user_pics/{}".format(filename)

				# Update user profile pic and push changs to database
				session.add(new_user_pics)
				user.profile_pic_path = new_user_pics.path
				session.commit()

				return {"success": "saved file"}

@app.route('/swipe/', strict_slashes=False, methods=['GET', 'POST'])
def swipe():

	if request.method == "GET":
		with Session() as session:
			# Get the user's preferences
			prefs = session.query(User_preferences).filter_by(user_id=logged_in_session.get("user_id")).first()
			pref_gender = prefs.gender
			pref_min_age = prefs.min_age
			pref_max_age = prefs.max_age
			pref_distance = prefs.distance
			pref_intention = prefs.intentions

			# Get the user's coordinates
			user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
			this_user_latitude = user.latitude
			this_user_longitude = user.longitude

			# Filter all users according the this user"s age and gender preferences
			candiate_list = session.query(Users).filter_by(gender=pref_gender).filter(Users.age <= pref_max_age).filter(Users.age >= pref_min_age).all()

			# If candidate intentions matches user intentions add canidate to result (list)
			result = []
			for candidate in candiate_list:
				candidate_prefs = session.query(User_preferences).filter_by(user_id=candidate.id).first()
				if candidate_prefs and candidate_prefs.intentions == pref_intention:
					result.append(candidate)

			# If the user has not already likeed the candidate, add candiate to result1 (list)
			result1 = []
			user_exisiting_likes = session.query(Likes).filter_by(user_1_id=logged_in_session.get("user_id")).all()
			for candidate1 in result:
				found = False
				for like in user_exisiting_likes:
					if like.user_2_id == candidate1.id:
						found = True
						break
				if not found:
					result1.append(candidate1)


			# Compare the users coordinates to the canidates and get the distance.
			# If the canidates distance is within the user"s preference add canidate to result2 (list)
			# Create a dictionary of the same users {"username": distance}
			distance_dict = {}
			result2 = []
			for candidate1 in result1:
				candidate_location = "{}, {}".format(candidate1.latitude, candidate1.longitude)
				user_location = "{}, {}".format(this_user_latitude ,this_user_longitude)
				distance = geodesic(candidate_location, user_location).kilometers
				real_distance = int(distance)

				if real_distance <= pref_distance:
					result2.append(candidate1)
					distance_dict[candidate1.user_name] = real_distance

			# Shuffle the result
			shuffled_list = result2.copy()
			random.shuffle(shuffled_list)

			# If this user happens to be in the result list remove them
			for a in shuffled_list[:]:
				if a.user_name == user.user_name:
					shuffled_list.remove(a)

			# Get a slice of the result list (first 20), if the list was over 20
			if len(shuffled_list) > 20:
				shuffled_list = shuffled_list[:20]

			return render_template('swipe.html', result=shuffled_list, distance=distance_dict)

	elif request.method == "POST":
		form_data = request.json

		with Session() as session:

			# Get the user and likee
			user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
			likee = session.query(Users).filter_by(user_name=form_data["canidate_user_name"]).first()
			if likee:
				new_like = Likes()
				new_like.user_1_id = logged_in_session.get("user_id")
				new_like.user_2_id = likee.id

				# Check if likee and has already liked the liker and create a new match
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
					return "New Match"
				else:
					session.add(new_like)
					session.commit()
					return {"success": "created a like"}

		return {"error": "user not found"}


# On GET: return the update user info html template
# On Post: Update info with data from the request
@app.route('/update-user-info/', strict_slashes=False, methods=['GET', 'POST'])
def update_user_info():
	if request.method == "GET":
		with Session() as session:
			user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
			return render_template('update_user_info.html', user=user)

	if request.method == "POST":
		form_data = request.json
		with Session() as session:
			user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
			user.first_name = form_data["first_name"]
			user.last_name = form_data["last_name"]
			user.date_of_birth = form_data["date_of_birth"]
			user.email = form_data["email"]
			user.user_name = form_data["user_name"]
			user.gender = form_data["gender"]
			user.bio = form_data["bio"]
			session.commit()
			return {"success": "updated user info"}

# On GET: inform user and a new match
@app.route('/new_match/', strict_slashes=False, methods=['GET'])
def new_match():

	if request.method == "GET":
		this_user = logged_in_session.get("user_id")

		with Session() as session:
			match = session.query(Matches).filter(or_(Matches.user_1_id == this_user, Matches.user_2_id == this_user)).order_by(desc(Matches.created_at)).first()
			if match is None:
					return redirect(url_for("dashboard"))

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

		return redirect(url_for("dashboard"))

# On GET: inform user and multiple new matches
@app.route('/new_match_passive/', strict_slashes=False, methods=['GET'])
def new_match_passive():
	if request.method == "GET":
		this_user = logged_in_session.get("user_id")
		with Session() as session:
			matches = session.query(Matches).filter(or_(Matches.user_1_id == this_user, Matches.user_2_id == this_user)).order_by(desc(Matches.created_at)).all()
			if matches is None:
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

		return redirect(url_for("dashboard"))

# On GET: Show all matches
@app.route('/view_matches/', strict_slashes=False, methods=['GET', 'DELETE'])
def view_matches():
	if request.method == "GET":
		with Session() as session:

			# Get user and user's matches
			this_user = logged_in_session.get("user_id")
			user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
			matches = session.query(Matches).filter(or_(Matches.user_1_id == this_user, Matches.user_2_id == this_user)).order_by(desc(Matches.created_at)).all()

			if matches is None:
					return redirect(url_for("dashboard"))

			# Get the a list of the other users from this users matches
			my_list = []
			for match in matches:
				if match.user_1_id == this_user:
					likee = session.query(Users).filter_by(id=match.user_2_id).first()
					my_list.append(likee)
				if match.user_2_id == this_user:
					likee = session.query(Users).filter_by(id=match.user_1_id).first()
					my_list.append(likee)

			# Get a dictinary of users: distance
			distance_dict = {}
			for candidate1 in my_list:
				candidate_location = "{}, {}".format(candidate1.latitude, candidate1.longitude)
				user_location = "{}, {}".format(user.latitude , user.longitude)
				distance = geodesic(candidate_location, user_location).kilometers
				real_distance = int(distance)
				distance_dict[candidate1.user_name] = real_distance

			return render_template('view_matches.html', result=my_list, user=user, distance=distance_dict)

	elif request.method == "DELETE":
		form_data = request.json
		other_user = int(form_data["id"])
		with Session() as session:
			# Get the user instance and a list of their matches
			user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
			matches = session.query(Matches).filter(or_(Matches.user_1_id == user.id, Matches.user_2_id == user.id)).all()

			# Delete the match instance
			for a in matches:
				if a.user_1_id == user.id and a.user_2_id == other_user:
					session.delete(a)
				if a.user_2_id == user.id and a.user_1_id == other_user:
					session.delete(a)

			# Get and delete the the two respective likes from the match
			like_to_delete = session.query(Likes).filter(Likes.user_1_id == user.id, Likes.user_2_id == other_user).first()
			like_to_delete_2 = session.query(Likes).filter(Likes.user_1_id == other_user, Likes.user_2_id == user.id).first()
			session.delete(like_to_delete)
			session.delete(like_to_delete_2)

			session.commit()
			return({"success": "deleted this match"})


# On GET: Load the latest 200 messages from both users
# On Post: Add a ,ew message instance
@app.route('/message/', strict_slashes=False, methods=['GET', 'POST'])
def messsage ():
	this_user = logged_in_session.get("user_id")
	if request.method == "GET":
		match_id = int(request.args.get('match_id'))
		with Session() as session:

			# Get the match username
			match_user = session.query(Users).filter_by(id=match_id).first()
			match_user_name = match_user.user_name

			# Combine the messages from both users
			dms_from_user = session.query(Messages).filter(Messages.sender_id == this_user ,Messages.receiver_id == match_id)
			dms_from_match = session.query(Messages).filter(Messages.sender_id == match_id ,Messages.receiver_id == this_user)
			combined = dms_from_user.union(dms_from_match).order_by(asc(Messages.sent_at)).limit(200).all()

		return render_template('messages.html', match_user_name=match_user_name, match_id=match_id, this_user_id=this_user, combined=combined)
	if request.method == "POST":

		match_id = int(request.args.get('match_id'))
		form_data = request.json

		with Session() as session:
			new_message = Messages()
			new_message.sender_id = this_user
			new_message.receiver_id = match_id
			new_message.content = form_data["text"]
			session.add(new_message)
			session.commit()

		return({"success": "printed the form data"})

# On GET: Check if email has been verified
# On POST: Enter the verification code
@app.route('/verify_email/', strict_slashes=False, methods=['GET', 'POST'])
def verify_email ():

	if request.method == "GET":
		with Session() as session:
			this_user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
			if this_user:
				if this_user.email_verified == True:
					return "email has been verified"
				elif this_user.email_verified == False:

					# Get a random code
					code = random.randint(1000, 9999)

					# Send an email with the code
					msg = Message('Hello from fraiseberry', sender = 'fraiseberryfr@gmail.com', recipients = [this_user.email])
					msg.body = "Thanks for signing up for a fraise account.\n\nPlease see the code to verify your email address: {}\n\nIf you didn't signup for a fraise account please ignore and delete this email\n\nStart your journey to find love now".format(code)
					mail.send(msg)

					# Update the database with the code
					this_user.verification_code = code
					session.commit()

					return render_template("verification.html")

	if request.method == "POST":
		with Session() as session:
			this_user = session.query(Users).filter_by(id=logged_in_session.get("user_id")).first()
			form_data = request.json

			# Parse the code
			parsed_code = form_data["no1"] + form_data["no2"] + form_data["no3"] + form_data["no4"]
			if parsed_code.isdigit():
				parsed_code_int = int(parsed_code)
			else:
				return "incorrect code"

			# If the parsed code match the database verify the email
			if parsed_code_int == this_user.verification_code:
				this_user.email_verified = True
				session.commit()
				return "email has been verified"
			else:
				return "incorrect code"






if __name__ == '__main__':
	app.run(host='0.0.0.0', port='5000')
