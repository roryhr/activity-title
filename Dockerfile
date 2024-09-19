ARG PYTHON_VERSION=3.11-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG SECRET_KEY
ARG STRAVA_CLIENT_ID
ARG STRAVA_CLIENT_SECRET

ENV SECRET_KEY=${SECRET_KEY} \
    STRAVA_CLIENT_ID=${STRAVA_CLIENT_ID} \
    STRAVA_CLIENT_SECRET=${STRAVA_CLIENT_SECRET}

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "strava_deck.wsgi"]
