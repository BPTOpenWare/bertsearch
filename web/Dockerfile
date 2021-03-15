FROM python:3.8.6-slim-buster
COPY . /app
WORKDIR /app
RUN pip install -U pip
RUN pip install -r requirements.txt
ENTRYPOINT ["gunicorn"]
CMD ["-w 4", "-b 0.0.0.0:5000", "app:app"]
