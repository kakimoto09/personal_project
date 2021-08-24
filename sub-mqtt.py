#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import os
import time
import datetime
import redis
import requests
from decimal import Decimal
from redistimeseries.client import Client as RedisTimeSeries
from setenv import BrokerAddress, MqttTopic, RedisHost, RedisPort, RedisPwd, temperature_key, sound_key, vector_key, line_access_token 
from setenv2 import topic1, topic2, topic3

redis_obj = redis.Redis(host=RedisHost, port=RedisPort, password=RedisPwd)

line_url = "https://notify-api.line.me/api/notify"
line_headers = {'Authorization': 'Bearer ' + line_access_token}

def set_db(msg,flag):                            ### set data to Redis
     date = datetime.datetime.now()
     tstamp = int(date.timestamp() * 1000)
     pipe = redis_obj.pipeline()

     if flag==1:
         pipe.execute_command(
         "ts.add", temperature_key, tstamp,msg
         )
         if float(msg) > 28:
             d = Decimal(msg)
             line_message='部屋が暑いみたい！'+str(d.quantize(Decimal('1e-1')))+'℃だよ'
             line_payload={'message': line_message}
             r = requests.post(line_url, headers=line_headers, params=line_payload,)
     elif flag==2:
         pipe.execute_command(
         "ts.add", sound_key, tstamp, msg
         )
         if float(msg) > 4:
             line_message='大きい音がしてるみたい！泣いてるかも！？'
             line_payload={'message': line_message}
             r = requests.post(line_url, headers=line_headers, params=line_payload,)
     elif flag==3:
         pipe.execute_command(
         "ts.add",vector_key, tstamp, msg
         )
     else:
         print("Undefind process... Hmm..")

     pipe.execute()

     print("Updated Radis...", )

def on_message(client, userdata, message):  ### callback when get message from MQTT broker
    msg = str(message.payload.decode("utf-8"))
    if message.topic == topic1:
        set_db(msg,1)
    elif message.topic == topic2:
        set_db(msg,2)
    elif message.topic == topic3:
        set_db(msg,3)
    else:
        print("Undefind Topic Messages... Hmm..")
    print("Message received:" + msg + " on topic " + message.topic)

### Connect MQTT broker
print("Connecting to MQTT broker:" + BrokerAddress)
client = mqtt.Client()               # Create new instance with Any clientID
client.on_message=on_message         # Attach function to callback

try:
    client.connect(BrokerAddress)    #connect to broker
    print("Subscribe topic: ", MqttTopic)
    client.subscribe(MqttTopic)          # Subscribe MQTT
    client.loop_forever()                # Loop forever

except KeyboardInterrupt:
    print("Bye...")
    exit(0)
except:
    print("***** failed *****")
    exit(1)

