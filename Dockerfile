# FIXME: This container has an insane size, because it's not optimised at all.
# There is a single stage, and we use a big base image.
# This is just here to have a Postgres demo ready by Saturday, really.

FROM python:3.10.6-buster

WORKDIR /var/app

RUN pip install --upgrade pip
COPY ./requirements.txt /var/app
RUN pip install -r requirements.txt

COPY . .
