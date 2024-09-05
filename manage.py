#! /usr/bin/env python

import os
from dataservice import create_app

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')

BIND_ALL_INTERFACES = os.environ.get("BIND_ALL_INTERFACES")
host = None
if BIND_ALL_INTERFACES == "enabled":
    host = "0.0.0.0"

if __name__ == '__main__':
    app.run(host=host)
