#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

function migrate {
    cd /code/p0sx
    python manage.py migrate
}

function prod {
    echo Starting uwsgi
    exec uwsgi --chdir=/code/p0sx \
        --module=p0sx.wsgi:application \
        --env DJANGO_SETTINGS_MODULE=p0sx.settings.prod \
        --master --pidfile=/tmp/project-master.pid \
        --socket=0.0.0.0:8080 \
        --http=0.0.0.0:8081 \
        --processes=5 \
        --harakiri=20 \
        --max-requests=5000 \
        --offload-threads=4 \
        --static-map=/static=/code/collected_static \
        --static-map=/media=/code/media \
        --vacuum
}

function devserver {
    cd /code/p0sx
    python manage.py runserver_plus 0.0.0.0:8000
}

function compile-pip {
  echo "Compiling pip requirements"
  echo "Base requirements..."
  pip-compile requirements/base.in --output-file requirements/base.txt
  echo "Lint requirements..."
  pip-compile requirements/lint.in --output-file requirements/lint.txt
  echo "Dev requirements..."
  pip-compile requirements/dev.in --output-file requirements/dev.txt
  echo "Prod requirements..."
  pip-compile requirements/prod.in --output-file requirements/prod.txt
}

"$@"
