#!/bin/bash
source venv/bin/activate
rm webapp/migrations/__pycache__/*
rm webapp/migrations/0001_initial.py
rm db.sqlite3
echo "*** Emptied migrations folder and dbsqlite3 ***"
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata webapp/fixtures/initial_data.json
