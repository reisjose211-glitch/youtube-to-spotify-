FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
EXPOSE 8000
# One worker: conversion jobs are tracked in memory.
CMD gunicorn --workers 1 --threads 8 --timeout 0 --bind 0.0.0.0:$PORT app:app
