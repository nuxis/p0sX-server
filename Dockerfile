FROM python:3.7

ENV NAME=p0sx

ENV DIR=/srv/app

RUN mkdir -p $DIR
WORKDIR $DIR

# Install requirements
RUN mkdir -p $DIR/requirements
COPY ./requirements/base.txt $DIR/requirements/base.txt
COPY ./requirements/production.txt $DIR/requirements/production.txt
RUN pip install -r requirements/base.txt --upgrade
RUN pip install -r requirements/production.txt --upgrade

# Copy project files
COPY . $DIR

RUN mkdir -p static media
ENV DJANGO_SETTINGS_MODULE=$NAME.settings.base
RUN python manage.py collectstatic --noinput --clear
ENV DJANGO_SETTINGS_MODULE=$NAME.settings.prod

EXPOSE 8080 8081

CMD ["sh", "docker-entrypoint.sh"]
