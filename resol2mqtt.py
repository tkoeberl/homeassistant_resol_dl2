#! /usr/bin/env python
"""
reads out the values from the resol, parses it and pushes it to mqtt
"""
from __future__ import print_function
import sys
import argparse
import urllib.request as urllib
import json
from paho.mqtt import client as mqtt_client #pip3 install paho-mqtt
import random, time

def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--ip', action='store', dest='ip',
                    help="ip/name of the dl2")

    parser.add_argument('--broker', action='store', dest='broker',
                    help="ip/name of the mqtt broker")
    parser.add_argument('--port', action='store', dest='port',
                    help="port of the mqtt broker")
    parser.add_argument('--topic', action='store', dest='topic',
                    help="topic to use")
    parser.add_argument('--device_name', action='store', dest='dvc_name',
                    help="name of the device to use")                    
    parser.add_argument('--client_id', action='store', dest='client_id',
                    help="client_id to use")
    parser.add_argument('--username', action='store', dest='username',
                    help="username to use")
    parser.add_argument('--password', action='store', dest='password',
                    help="password to use")

    args = parser.parse_args()
    

    mqttclient=connect_mqtt(args.broker,args.port, args.client_id,args.username,args.password)

    l_headers, l_units, l_values = downloadResolJson("http://"+args.ip+"/dlx/download/live?view=99")
    



    #publish the values:
    for i in range(len(l_values)):
            #publish the config first:
        match l_units[i]:
            case " s":
                device_class="DURATION"
            case "%":
                device_class="POWER_FACTOR"
            case _:
                device_class="temperature"
        publish(mqttclient, "homeassistant/sensor/" + args.dvc_name + "/" + l_headers[i].replace(" ","_") + "/config", '{"unit_of_measurement":"'+l_units[i].replace(" ","")+'", "name": "'+args.dvc_name+'_'+l_headers[i].replace(" ","_")+'", "device_class": "'+device_class+'", "state_topic": "'+args.topic + l_headers[i].replace(" ","_") + '/state"}')
        value=str(l_values[i]) + l_units[i]
        value=str(l_values[i])
#        print("publishing:" + args.topic + l_headers[i].replace(" ","_") + "/state") 
        publish(mqttclient, args.topic + l_headers[i].replace(" ","_") + "/state" , value) 

    
def downloadResolJson(url):
    json_object = urllib.urlopen(url)
    data = json.loads(json_object.read().decode())
    l_headers=[]
    l_units=[]
    l_values=[]

    headers=(data['headers'])
    for ids in headers:
        fields=ids['fields']
        source_name=ids['source_name'].replace("[","").replace("]","").replace("#","")
        for id_ids in fields:
            l_headers.append(source_name + "_" + id_ids['name'])
            l_units.append(id_ids['unit'])

    headersets=(data['headersets'])
    for packets in headersets:
        field_values=packets['packets']
        for field_values_values in field_values:
            #print(field_values_values['header_index'])
            packets=field_values_values['field_values']
            for headers in packets:
                l_values.append(headers['raw_value'])    

    return l_headers, l_units, l_values

def connect_mqtt(broker, port, client_id, username, password):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, int(port))
    return client

def publish(client, topic, msg):
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        status = result[0]
    else:
        print(f"Failed to send message to topic {topic}")

if __name__ == "__main__":
    main()

