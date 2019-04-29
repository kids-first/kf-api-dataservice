FROM        python:3-alpine3.7

ADD         requirements.txt /app/
WORKDIR     /app

RUN apk update && apk add \
    py3-psycopg2 \
    musl-dev \
    supervisor \
    git \
    gcc \
    postgresql-dev \
    && rm -rf /var/cache/apk/*

RUN         pip install -r /app/requirements.txt
ADD         . /app
RUN         python /app/setup.py install

EXPOSE      80
ENV         FLASK_APP "manage.py"
ENV         FLASK_CONFIG "production"

# Setup supervisord
RUN         mkdir -p /var/log/supervisor/conf.d
COPY        bin/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
#COPY        bin/gunicorn.conf /etc/supervisor/conf.d/gunicorn.conf

# Start processes
CMD ["/app/bin/run.sh"]
