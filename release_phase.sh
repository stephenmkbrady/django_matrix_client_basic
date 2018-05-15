#!/bin/bash

echo "Running Release Tasks"
echo "Running Tests"
python manage.py test
echo "Running Migrations"
python manage.py migrate
