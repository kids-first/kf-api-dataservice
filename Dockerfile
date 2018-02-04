FROM        ubuntu:16.04
FROM        python:3.5
ADD         requirements.txt /app/
WORKDIR     /app
RUN         apt-get update & apt-get install gcc -y
RUN         pip install -r /app/requirements.txt
ADD         . /app
RUN         python /app/setup.py install
EXPOSE      80
ENV         FLASK_APP "manage.py"
ENV         FLASK_CONFIG "production"
CMD         ["./bin/run.sh"]
