FROM python:3.7

ENV DJANGO_SETTINGS_MODULE=p0sx.settings.env
COPY ./requirements/dev.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /code
WORKDIR "/code"
RUN "./bin/collectstatic.sh"

ENTRYPOINT ["./entry.sh"]
CMD ["devserver"]
