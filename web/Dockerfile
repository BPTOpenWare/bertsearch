FROM python:3.8.6-slim-buster
COPY . /app
WORKDIR /app
RUN apt-get update
RUN apt-get -y install python-pycurl python-dev libcurl4-gnutls-dev librtmp-dev gcc
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN apt-get -y remove gcc
ENTRYPOINT ["gunicorn"]
CMD ["-w 2", "-b 0.0.0.0:5000", "app:app"]
