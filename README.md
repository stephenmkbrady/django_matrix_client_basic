# django_matrix_client_basic
### Django matrix client app with absolutely no javascript. 
#### Description
The current matrix clients available are many and varied. 
The web version looks good but is frontend heavy and not designed for older devices or even newer devices with limited resources.
Some of the lighter native clients are great but are locked to win, mac or linux. 
This client just needs a very basic browser and internet access.

#### Features
- It's simply HTML4/5, and CSS3 in your browser. 
- It's responsive so will fit all screens. 
- Smooth deploy directly to heroku.
- It runs on everything (within reason): feature phone browsers, text based browsers, iexplore, chrome based, firefox based
- Displays text with urls only or thumbnailed images with urls.
- Tested
- Toaster compatible
- Django backend with postgresql db.
- No passwords are stored in the db and heroku is ephem.

### Live demo version
[Matrix Client Running On Heroku](https://peaceful-sea-58238.herokuapp.com/)
(First load might be slow as you wake the heroku hobby dyno up.)

### Development Environment Guide
__Required:__
__Python 3__
__postgresql installed, configured and running as per your OS__
__heroku_cli installed__
[The Arch Linux postgresql setup guide is great](https://wiki.archlinux.org/index.php/PostgreSQL)

#### Installation
1. $ mkdir venv1
Note: call this whatever you want, the idea is to keep your packages and env bins separate from the code
2. $ python -m venv venv1/
3. $ source venv1/bin/activate
Note: Activating your venv differs between environment, [read](https://docs.python.org/3/library/venv.html) 
4. $ cd venv1/
5. $ git clone https://github.com/stephenmkbrady/django_matrix_client_basic.git
6. $ cd django_matrix_client_basic/
7. $ pip install pipenv
8. $ pipenv install
__Everything is installed__

Note: pipenv can be used to create and activate the virtualenv aswell.


##### Database Setup
TL;DR: 
- Create DB called "pymatrix_client"
- Add role "pmatrix_client_user"
- Give role permission to "Create DB" (for use when running tests)
1. Login to your postgres account to admin psql, varies with environment. For arch linux:
$ sudo -u postgres -i
2. The db settings can be found in pymatrix_client/settings.py but you can follow the steps below to setup the db:
3. Create DB called: pymatrix_client'
[postgres]$ createdb myDatabaseName
4. Add the username: pmatrix_client_user
[postgres]$ createuser --interactive
or
[postgres]$ psql
postgres=# CREATE USER pmatrix_client_user WITH PASSWORD 'this_is_a_super_strong_password'
Give pmatrix_client_user the ability to create a db for the test run and give it a strong password. It will be used by DB_PASSWORD
5. In psql, you can list the users by typing \du, you want to have pmatrix_client_user with the ability to Create DB
postgres=# ALTER ROLE pmatrix_client_user WITH CREATEDB;
6. Exit both psql program and postgres account.


##### Environment Variables Setup
For testing localling in linux bash:
export SECRET_KEY="you_secret_unique_key_not_to_be_shared_and_strong"
[Choose a secret key based on the docs](https://docs.djangoproject.com/en/2.0/ref/settings/#std:setting-SECRET_KEY)
export DB_PASSWORD="the_password_you_used_when_creating_pmatrix_client_user"
For runnin on heroku:
[Add the same DB_PASSWORD and SECRET_KEY as config vars](https://devcenter.heroku.com/articles/config-vars)


##### Running Locally
First run (and if/when you change the model):
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py collectstatic


To run the server:
$ python manage.py runserver
or
$ gunicorn pymatrix_client.wsgi --timeout 120 
Note: matrix.org is slow to respond as it's under heavy load as it becomes popular, so extending the timeout seems to be required here.

Open a web browser at:
http://127.0.0.1:8000 

[Note: You can also run it locally using heroku_cli](https://devcenter.heroku.com/articles/getting-started-with-python#run-the-app-locally)

##### Running Tests
1. Add the following to your environment variables:
$ export TEST_USER="your_test_user_name_registered_with_matrix_server"
$ export TEST_PASS="your_test_user_names_pass"
$ export TEST_ROOM='#your_room:the_matrix_server_with_the.room'
$ python manage.py test

##### Deploying to Heroku
It's pretty straight forward from here.
[If you're unfamiliar with heroku, maybe follow this guide in a seperate folder before deploying this or any app. If you've deployed ruby or nodejs apps then you should be ok.](https://devcenter.heroku.com/articles/getting-started-with-python#introduction)
[Extra relevent reading](https://devcenter.heroku.com/articles/deploying-python#deployment-of-python-applications)

Note: The Procfile, Pipfile, Pipfile.lock and requirements.txt do not need to be modified for this.

__1. IMPORTANT: Open pymatrix_client/settings.py and set "DEBUG = False" from "DEBUG = True"__
2. heroku create
3. heroku addons:add heroku-postgresql
4. git push heroku master
5. heroku ps:scale web=1
6. heroku open

### TODO
#### Major Tasks in order of priority
- Another branch will be created with lightweight JS for async, make it behave like irc client.
#### Minor Tasks
- Add a little extra CSS to add better styling for medium to extra large screens.
- Find and add css minfier to heroku release script
