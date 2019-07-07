FROM python:3.7

RUN python -m pip install paho-mqtt

RUN mkdir tasmota_mqtt
COPY . /tasmota_mqtt

CMD ["python", "-u", "/tasmota_mqtt/promqtt.py"]
