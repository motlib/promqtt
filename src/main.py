import paho.mqtt.client as mqtt
import os
import json
from pprint import pprint
import traceback
from prom import PrometheusExporter
    

pe = PrometheusExporter()

def handle_sensor(nodename, payload):
    data = json.loads(payload)

    if 'BME280' in data:
        pe.set(
            name='tasmota_temperature',
            value=data['BME280']['Temperature'],
            labels={'node': nodename, 'sensor': 'BME280'})
        pe.set(
            name='tasmota_rel_humidity',
            value=data['BME280']['Humidity'],
            labels={'node': nodename, 'sensor': 'BME280'})
        pe.set(
            name='tasmota_pressure',
            value=data['BME280']['Pressure'],
            labels={'node': nodename, 'sensor': 'BME280'})
    else:
        print('Unsupported sensor.')

def handle_state(nodename, payload):
    data = json.loads(payload)
    
    pe.set(
        name='tasmota_vcc',
        value=data['Vcc'],
        labels={'node': nodename})
    pe.set(
        name='tasmota_wifi_rssi',
        value=data['Wifi']['RSSI'],
        labels={'node': nodename})
    
# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))

def on_message(client, obj, msg):

    tparts = msg.topic.split('/')
    #tasmota/tele/sens-br1/SENSOR
    # {"Time":"2019-06-29T14:27:51","BME280":{"Temperature":25.5,"Humidity":76.0,"Pressure":991.2},"PressureUnit":"hPa","TempUnit":"C"}
    try:
        if tparts[0] == 'tasmota' and tparts[1] == 'tele' and tparts[3] == 'SENSOR':
            handle_sensor(nodename=tparts[2], payload=msg.payload)

        #tasmota/tele/sens-br1/STATE
        #b'{"Time":"2019-06-29T15:27:51","Uptime":"13T05:21:05","Vcc":2.818,"SleepMode":"Dynamic","Sleep":50,"LoadAvg":19,
        # "Wifi":{"AP":1,"SSId":"ChaosWLAN","BSSId":"7C:DD:90:D4:30:43","Channel":7,"RSSI":96,"LinkCount":2,"Downtime":"5T14:55:50"}}'
        elif tparts[0] == 'tasmota' and tparts[1] == 'tele' and tparts[3] == 'STATE':
            handle_state(nodename=tparts[2], payload=msg.payload)
        
            
    except Exception as e:
        print('EX:', e)
        traceback.print_exc()
    
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print('LOG:', string)


def mqtt_setup(host, port):
    mqttc = mqtt.Client()
    
    # Assign event callbacks
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    
    # Uncomment to enable debug messages
    mqttc.on_log = on_log
    
    # Connect
    #mqttc.username_pw_set(url.username, url.password)
    mqttc.connect(host, port)

    return mqttc
    

def main():
    pe.reg(
        name='tasmota_temperature',
        datatype='gauge',
        helpstr='Temperature in degree celsius')
    pe.reg(
        name='tasmota_pressure',
        datatype='gauge',
        helpstr='Air pressure in millibar')
    pe.reg(
        name='tasmota_rel_humidity',
        datatype='gauge',
        helpstr='Relative humidity in percent')
    pe.reg(
        name='tasmota_vcc',
        datatype='gauge',
        helpstr='Supply voltate of tasmota node')
    pe.reg(
        name='tasmota_wifi_rssi',
        datatype='gauge',
        helpstr='Relative wifi signal strength indicator')
    
    mqttc = mqtt_setup(host='npi2', port=1883)

    # Start subscribe, with QoS level 0
    mqttc.subscribe('tasmota/#')

    mqttc.loop_forever()
    

if __name__ == '__main__':
    main()

