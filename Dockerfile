FROM python:3.5.2

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
ENV DJANGO_SETTINGS_MODULE=$NAME.settings.prod

EXPOSE 8080
EXPOSE 8081

CMD ["sh", "docker-entrypoint.sh"]
