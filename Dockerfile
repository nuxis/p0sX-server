FROM alpine:latest

MAINTAINER Kristoffer Dalby

ENV NAME=p0sx

ENV DIR=/srv/app

RUN mkdir -p $DIR
WORKDIR $DIR

RUN apk add --update --no-cache \
    uwsgi-python3 \
    uwsgi-http \
    uwsgi-corerouter \
    py3-psycopg2 \
    py3-pillow \
    git

# Install requirements
COPY ./requirements $DIR/requirements
RUN pip3 install -r requirements/production.txt --upgrade

RUN apk del --no-cache git

# Copy project files
COPY . $DIR

RUN mkdir -p static media
ENV DJANGO_SETTINGS_MODULE=$NAME.settings.base
RUN python3 manage.py collectstatic --noinput --clear
ENV DJANGO_SETTINGS_MODULE=$NAME.settings.prod

EXPOSE 8080
EXPOSE 8081

CMD ["sh", "docker-entrypoint.sh"]
