#!/bin/sh
source .venv/bin/activate
export DEBUG=True
python mysite/manage.py runserver $PORT
