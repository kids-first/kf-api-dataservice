FROM        ubuntu:16.04
FROM        python:3.5
ADD         requirements.txt /app/
WORKDIR     /app
RUN         apt-get update & apt-get install gcc -y
RUN         pip install -r /app/requirements.txt
RUN         pip install -e .
ADD         . /app
EXPOSE      80
ENV         FLASK_APP "manage.py"
ENV         FLASK_CONFIG "production"
ENV         PG_HOST
ENV         PG_NAME
#RUN         ["flask", "db", "init"]
RUN         ["flask", "db", "upgrade"]
RUN         ["flask", "db", "migrate"]
CMD         ["gunicorn", "-b", ":80", "--access-logfile", "-",  "manage:app", "--threads", "4"]
