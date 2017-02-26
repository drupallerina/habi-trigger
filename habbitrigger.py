#!/usr/bin/python
import yaml
import json
import paho.mqtt.client as mqtt
from subprocess import call


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/opentrigger/signals/trigger")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    ipAddress = data['UniqueIdentifier']
    if ipAddress in userdata:
        call(["habitica", "dailies", "done", str(userdata[ipAddress])])
    else:
        print(ipAddress + " is not in list")

#Connect to mqtt client on localhost
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

configFile = file('habbitrigger.yaml', 'r')
client._userdata = yaml.load(configFile)

client.connect("localhost")

#Display all dailies
call(["habitica", "dailies"])

client.loop_forever()
