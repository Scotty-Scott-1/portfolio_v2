# Fraiseberry

## inntroduction
The purpose is to connect those who are looking for romantic relationships or friendship and to facilitate correspondence between the matched pair. The search algorithm presents the user with a list of candidates according to their preferences; where the user can then like or pass the candidate. If two users like each other a match is initiated. A match can de deleted.

https://medium.com/@6799/fraiseberry-com-match-making-eb6674bc2696

## Installation
Please follow the following steps:
* Set up a SMTP app password on your prefered email account. Recommended email provider: gmail.
* Clone this repo
* Install dependancies
* Run the following command: ./create_tables.py argv1 argv2 argv3 argv4
	* the command line argument relate the MySQL database:
	* user_name = argv[1]
	* password = argv[2]
	* host = argv[3]
	* db_name = argv[4]
* Run the following command: ./fraiseberry.py argv1 argv2 argv3 argv4 argv5 argv6 argv7 argv8
	* Command line arguments 1 - 4 relate the MySQL database
	* user_name = argv[1]
	* password = argv[2]
	* host = argv[3]
	* db_name = argv[4]

	* Command line arguments 5 - 7 relate the Fmask mail config
	* app.config['MAIL_USERNAME'] = argv[5]
	* app.config['MAIL_PASSWORD'] = argv[6]
	* app.config['MAIL_SERVER'] = argv[7]

	* Command line arguments 8 is the app secret key

## Usage

* To create an account click on the sign up, complete the form and submit. If the form passes checks the account is created
* Sign in with username and password
* Verify your email address by checking for a email from the app. This contains the verification code
* Click on the camera icon to take/update profile pic
* Click on the pencil icon to update preferences
* Click on the settings icon to update uer information
* Click on the heart icon a generate a list of candidates
* Click on the message icon to view matches

## Contributing

Fork the repository.
Create a new branch for your feature or bug fix: git checkout -b feature-name.
Make your changes and commit them: git commit -am 'Add new feature'.
Push to the branch: git push origin feature-name.
Submit a pull request with a clear description of your changes.

## Related projects

Coming soon Fraiseberry V3 intended for public release.

## Authors

https://www.linkedin.com/in/solomon-william-b88401a3
