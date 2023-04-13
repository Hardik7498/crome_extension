#! /bin/bash

export FLASK_APP=src.app:create_app
flask run --host=0.0.0.0 --port=5000 --reload --debugger
