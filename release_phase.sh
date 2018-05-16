#!/bin/bash

echo "Running Release Tasks"
echo "collectstatic"
python manage.py collectstatic
echo "Running Tests"
python manage.py test
echo "Running Migrations"
python manage.py migrate
