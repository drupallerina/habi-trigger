#!/usr/bin/python
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe("/opentrigger/signals/trigger")
    client.subscribe("/opentrigger/signals/release")

def on_message(client, userdata, msg):
    publish.single(msg.topic, msg.payload, hostname = "192.168.188.41")


#Connect to mqtt client on localhost
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost")

client.loop_forever()
