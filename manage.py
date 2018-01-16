#! /usr/bin/env python

import os
from dataservice import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    app.run()
