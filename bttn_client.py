#!/usr/bin/python
import yaml
import json
import time
import requests
import paho.mqtt.client as mqtt

"""
Structure of bttn_client.yaml:
---
'api_key': 'bt.tn API KEY'
'bttn_id': 'bt.tn ID'
'sleep_time': 10
---
* The sleep time defines the polling frequency in seconds
* The api_key and the bttn_id can be found in the bt.tn web interface
"""


configFile = file('bttn_client.yaml', 'r')
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
