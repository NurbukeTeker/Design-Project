FROM python:3.7-slim
FROM ubuntu:latest
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && apt-get update \
    && apt-get -y install python3-pip\
        curl \
        git \
        gcc \
        python-dev 
WORKDIR /tesseract-flask-image-labeling-master

COPY . /tesseract-flask-image-labeling-master
RUN pip3 install opencv-python 
RUN pip install -r requirements.txt

EXPOSE 5000
# ENTRYPOINT [ "python3" ]
CMD [  "python3", "application.py" ]