#!/bin/ash
flask db upgrade
supervisord -c  /etc/supervisor/conf.d/supervisord.conf
