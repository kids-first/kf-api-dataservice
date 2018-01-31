#!/bin/bash
source venv/bin/activate
flask db upgrade
flask db migrate
exec gunicorn -b :80 --access-logfile - manage:app --threads 4
