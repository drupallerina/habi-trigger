#!/usr/bin/python
import yaml
import json
import time
import requests
import paho.mqtt.client as mqtt

configFile = file('bttn_trigger.yaml', 'r')
config = yaml.load(configFile)

#Connect to mqtt client on localhost
client = mqtt.Client()
client.connect("localhost")

prev_timestamp = time.time()

while 1:
   resp = requests.get("https://api.bt.tn/2014-06/"+config['bttn_id']+"/feed?limit=1&after="+str(prev_timestamp), headers={'X-Api-Key':config['api_key']})
   resp_json=json.loads(resp.text)
   print resp_json['address'][0]
   print resp_json['events']
   if resp_json['events']:
     mqtt_payload='{"UniqueIdentifier":"' + resp_json['address'][0] + '"}'
     client.publish("/opentrigger/signals/trigger", mqtt_payload)
   prev_timestamp = time.time()
   time.sleep(config['sleep_time'])
