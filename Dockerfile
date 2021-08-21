FROM python:3.7

ENV DJANGO_SETTINGS_MODULE=p0sx.settings.env
RUN mkdir /requirements
COPY ./requirements/dev.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /code

EXPOSE 8080 8081

WORKDIR "/code"
ENTRYPOINT ["./entry.sh"]
CMD ["devserver"]
