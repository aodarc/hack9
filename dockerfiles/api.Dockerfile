FROM python:3.7.5

COPY requirements/*.txt /project/

ADD . /project/

RUN python3 -m pip install -r /project/requirements/base.txt --no-cache-dir

WORKDIR /project/