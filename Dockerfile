ARG PYTHON_VERSION=3.12.3-slim-bookworm

FROM python:${PYTHON_VERSION} AS base

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./discussia discussia/