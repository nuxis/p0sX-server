FROM python:3.7

ENV DJANGO_SETTINGS_MODULE=p0sx.settings.env
RUN mkdir /requirements
COPY ./requirements/base.txt /requirements/
COPY ./requirements/production.txt /requirements/
RUN pip install -r /requirements/base.txt
RUN pip install -r /requirements/production.txt

COPY . /code

EXPOSE 8080 8081

ENTRYPOINT ["/code/entry.sh"]
CMD ["devserver"]
