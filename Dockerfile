FROM ubuntu:jammy

MAINTAINER thomasbechtold@jpberlin.de
ARG VERSION=unknown

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APPDIR /app

RUN apt update \
    && apt install --no-install-recommends --yes python3-pip gcc libpython3-dev libpq-dev pkg-config gettext \
    && DEBIAN_FRONTEND=noninteractive apt clean

WORKDIR $APPDIR

COPY . .
RUN cd django-kitamanager && \
    pip install --upgrade pip setuptools \
    && SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION} pip install --no-cache-dir "." gunicorn tzdata

COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 8000
CMD gunicorn kmsite.wsgi:application --bind 0.0.0.0:8000
