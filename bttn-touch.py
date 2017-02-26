#!/usr/bin/python
import paho.mqtt.client as mqtt
import json
from subprocess import call
from datetime import datetime

false = 0
true = 1
doubleClickTimeoutMs = 1000

def set_led(ip, red, green, blue):
    rgb_str = 'r=' + str(red) + '&g=' + str(green) + '&b=' + str(blue)
    uri_str = 'coap://' + ip + '/led/RGB'
    call(['coap', 'put', '-p', rgb_str, uri_str])

def is_doubleclick(ipAddress, userdata, json_msg):
    doubleclickDetected = false
    currentTimestamp = datetime.strptime(json_msg['Timestamp'].split("+")[0], "%Y-%m-%dT%H:%M:%S.%f") # cut off timezone information beforehand
    if ipAddress in userdata:
       prevTimestamp = userdata[ipAddress]
       delta = currentTimestamp - prevTimestamp
       diffMs = int(delta.total_seconds()*1000)

#       print("Diff: " + str(diffMs))
       if diffMs <= doubleClickTimeoutMs:
          doubleclickDetected = true
    userdata[ipAddress] = currentTimestamp
    return doubleclickDetected

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #client.subscribe("/opentrigger/signals/trigger")
    client.subscribe("/opentrigger/signals/release")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    ipAddress = data['UniqueIdentifier']
    if msg.topic == '/opentrigger/signals/release':
        if data['Age'] > 2000:
            print 'Got Bezahlen'
            set_led(ipAddress, 0, 0, 255)
        elif is_doubleclick(ipAddress, userdata, data):
            print 'Got Reklamieren'
            set_led(ipAddress, 255, 0, 0)
        else:
            print 'Got Bestellen'
            set_led(ipAddress, 0, 255, 0)

#Connect to mqtt client on localhost
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client._userdata = {} # empty dictionary

client.connect("localhost")

client.loop_forever()
