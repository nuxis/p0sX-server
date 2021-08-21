#!/usr/bin/env sh
python manage.py migrate

rm /tmp/project-master.pid

touch /srv/app/aspargesgaarden.log
tail -n 0 -f /srv/app/*.log &

echo Starting uwsgi.
exec uwsgi --chdir=/srv/app \
    --module=p0sx.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=p0sx.settings.prod \
    --master --pidfile=/tmp/project-master.pid \
    --socket=0.0.0.0:8080 \
    --http=0.0.0.0:8081 \
    --processes=5 \
    --harakiri=20 \
    --max-requests=5000 \
    --offload-threads=4 \
    --static-map=/static=/srv/app/collected_static \
    --static-map=/media=/srv/app/media \
    --vacuum
