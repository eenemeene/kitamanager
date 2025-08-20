FROM ubuntu:noble

MAINTAINER thomasbechtold@jpberlin.de
ARG VERSION=unknown

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update \
    && apt install --no-install-recommends --yes python3-pip gcc libpython3-dev libpq-dev pkg-config gettext \
    && DEBIAN_FRONTEND=noninteractive apt clean

WORKDIR /app/

COPY . /app/
RUN pip install --upgrade pip setuptools
RUN cd django-kitamanager && SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION} pip install --no-cache-dir "." gunicorn tzdata
RUN python3 ./manage.py compilemessages
RUN python3 ./manage.py collectstatic --noinput
# install again to have compiled messages there
RUN cd django-kitamanager && SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION} pip install --no-dependencies --no-cache-dir "."

COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 8000
CMD gunicorn kmsite.wsgi:application --bind 0.0.0.0:8000
