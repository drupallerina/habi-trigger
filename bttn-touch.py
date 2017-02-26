#!/usr/bin/python
import paho.mqtt.client as mqtt
import json
from subprocess import call
from datetime import datetime
import sqlite3

false = 0
true = 1
doubleClickTimeoutMs = 1500
resetClickTimeoutMs =  3000

def set_state(ipAddress, state, timestamp):
    print ("set state " + state + " for " + ipAddress + " (" + timestamp + ")")
    global c
    global conn
    try:
        c.execute('INSERT INTO states(ip_address, state, timestamp) VALUES(?,?,?)', (ipAddress, state, timestamp))
    except:
        c.execute('UPDATE states SET state = ?, timestamp = ? WHERE ip_address = ?', (state, timestamp, ipAddress))
    conn.commit()

def set_led(ip, red, green, blue):
    rgb_str = 'r=' + str(red) + '&g=' + str(green) + '&b=' + str(blue)
    uri_str = 'coap://' + ip + '/led/RGB'
    call(['coap', 'put', '-p', rgb_str, uri_str])

def is_resetclick(ipAddress, userdata, json_msg):
    global c
    c.execute('SELECT state FROM states WHERE ip_address = "%s"' % (ipAddress))
    state = c.fetchone()[0]
    if state == 'reset':
       return false
    resetclickDetected = false
    currentTimestamp = datetime.strptime(json_msg['Timestamp'].split("+")[0], "%Y-%m-%dT%H:%M:%S.%f") # cut off timezone information beforehand
    if ipAddress in userdata:
       prevTimestamp = userdata[ipAddress]
       delta = currentTimestamp - prevTimestamp
       diffMs = int(delta.total_seconds()*1000)

       if diffMs > resetClickTimeoutMs:
          resetclickDetected = true
          userdata[ipAddress] = currentTimestamp
    return resetclickDetected

def is_doubleclick(ipAddress, userdata, json_msg):
    doubleclickDetected = false
    currentTimestamp = datetime.strptime(json_msg['Timestamp'].split("+")[0], "%Y-%m-%dT%H:%M:%S.%f") # cut off timezone information beforehand
    if ipAddress in userdata:
       prevTimestamp = userdata[ipAddress]
       delta = currentTimestamp - prevTimestamp
       diffMs = int(delta.total_seconds()*1000)

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
        if is_resetclick(ipAddress, userdata, data):
            print 'Got reset'
            set_led(ipAddress, 0, 0, 0)
            set_state(ipAddress, 'reset', data['Timestamp'])
        elif data['Age'] > 2000:
            print 'Got Bezahlen'
            set_led(ipAddress, 0, 0, 255)
            set_state(ipAddress, 'bezahlen', data['Timestamp'])
        elif is_doubleclick(ipAddress, userdata, data):
            print 'Got Reklamieren'
            set_led(ipAddress, 255, 0, 0)
            set_state(ipAddress, 'reklamieren', data['Timestamp'])
        else:
            print 'Got Bestellen'
            set_led(ipAddress, 0, 255, 0)
            set_state(ipAddress, 'bestellen', data['Timestamp'])


#Connect to mqtt client on localhost
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client._userdata = {} # empty dictionary
client.connect("localhost")

conn = sqlite3.connect('/home/pi/createcamp.db');
c = conn.cursor();
c.execute('CREATE TABLE IF NOT EXISTS states (ip_address TEXT PRIMARY KEY NOT NULL, state TEXT, timestamp TEXT)')
client.loop_forever()
