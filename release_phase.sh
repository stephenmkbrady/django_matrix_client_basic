#!/bin/bash

echo "Running Release Tasks"
echo "Running Migrations"
python manage.py migrate
