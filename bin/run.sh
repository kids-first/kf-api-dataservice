#!/bin/ash
source venv/bin/activate
flask db upgrade
supervisord -c  /etc/supervisor/conf.d/supervisord.conf
