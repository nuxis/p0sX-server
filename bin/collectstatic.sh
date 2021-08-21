#!/bin/bash
# Building static files requires us to have a running/configured environment.
# Because the Dockerfile is oblivious to the config used for runtime, we just
# run the static file collection using some boilerplate runtime config here

# This is the directory where the script lies, not where it is run from
PROJECT_ROOT="${BASH_SOURCE%/*}/.."

source "$PROJECT_ROOT/config/env/base.env"
export $(cut -d= -f1 "$PROJECT_ROOT/config/env/base.env" | grep -v '^#')
# "secrets"

export SECRET_KEY=dontLeakMe
export POSTGRES_PASSWORD=asdf


cd "$PROJECT_ROOT"/p0sx && python manage.py collectstatic --noinput