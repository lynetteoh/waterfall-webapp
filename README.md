# CS4920-project

[Facebook Group](https://www.facebook.com/groups/246537335979315/?fref=nf)

## Instructions for SETTING UP the development environment.

Update/install virtualenv using pip: pip install virtualenv

1. virtualenv venv -p python3.6

2. source venv/bin/activate

3. pip install -r requirements.txt


## Everytime you add a python dependancy to the project, run:

pip freeze > requirements.txt


## Wiping the DB clean and loading dummy dev data

1. Delete all files BUT __init__.py files in migration folders for each app.
2. Drop the current database, or delete the db.sqlite3 if it is your case.
3. Create the initial migrations and generate the database schema:

python manage.py makemigrations

python manage.py migrate

4. Load dummy data

python manage.py loaddata webapp/fixtures/initial_data.json