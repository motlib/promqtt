FROM python:3.7

COPY requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

RUN mkdir /promqtt
COPY . /promqtt

ENTRYPOINT ["python", "-u", "/promqtt/promqtt.py"]
