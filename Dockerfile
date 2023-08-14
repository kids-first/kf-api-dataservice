FROM        python:3-alpine3.7 as builder

WORKDIR     /app

EXPOSE      80
ENV         FLASK_APP "manage.py"
ENV         FLASK_CONFIG "production"

# Setup deps
RUN apk update && apk add py3-psycopg2 musl-dev \
    nginx supervisor git \
    openssl ca-certificates \
    gcc postgresql-dev \
 && pip install --upgrade pip

# Setup nginx
RUN         mkdir -p /run/nginx && \
            mkdir -p /etc/nginx/sites-available && \
            mkdir /etc/nginx/sites-enabled && \
            rm -f /etc/nginx/sites-enabled/default && \
            rm -f /etc/nginx/conf.d/default.conf
COPY        bin/nginx.conf /etc/nginx/nginx.conf

# Setup supervisord
RUN         mkdir -p /var/log/supervisor/conf.d
COPY        bin/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Setup dataservice
COPY        requirements.txt /app/
RUN         pip install "cython<3.0.0" && pip install --no-build-isolation "pyyaml==5.4.0" 
RUN         pip install -r /app/requirements.txt

COPY        manage.py setup.py config.py /app/
COPY        bin bin
COPY        docs docs
COPY        migrations migrations
COPY        dataservice  dataservice
COPY        .git .git
RUN         python /app/setup.py install

# Start processes
CMD ["/app/bin/run.sh"]

FROM        builder as test
COPY        dev-requirements.txt /app/
RUN         pip install -r /app/dev-requirements.txt
