FROM python:3.7.0

MAINTAINER Kristoffer Dalby

ENV NAME=p0sx

ENV DIR=/srv/app

RUN mkdir -p $DIR
WORKDIR $DIR

# Install requirements
COPY ./requirements $DIR/requirements
RUN pip install -r requirements/production.txt --upgrade

# Copy project files
COPY . $DIR

RUN mkdir -p static media
ENV DJANGO_SETTINGS_MODULE=$NAME.settings.base
RUN python manage.py collectstatic --noinput --clear

EXPOSE 8080 8081

CMD ["sh", "docker-entrypoint.sh"]
