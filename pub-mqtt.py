#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import os
import time
import ADC0832
from mpu6050 import mpu6050
from setenv import BrokerAddress
from setenv2 import topic1, topic2, topic3

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def readSensor(id):
        tfile = open("/sys/bus/w1/devices/"+id+"/w1_slave")
        text = tfile.read()
        tfile.close()
        secondline = text.split("\n")[1]
        temperaturedata = secondline.split(" ")[9]
        temperature = float(temperaturedata[2:])
        temperature = temperature / 1000
        soundorg = ADC0832.getResult()
        soundorg = soundorg - 136
	mpu = mpu6050(0x68)
	accel_data = mpu.get_accel_data()
        print "MIC:" + "%d" % soundorg
        print "DS18B20: " + id  + " - Current temperature : %0.3f C" % temperature
	print ("MPU6050: x:" + "%6.3f" % (accel_data['x']) + " y:" + "%6.3f" % accel_data['y'] + " z:" + "%6.3f" % (accel_data['z']))
        client.publish(topic1, temperature, 0, True)
	client.publish(topic2, soundorg, 0, True)
	client.publish(topic3, (abs(accel_data['x'])+abs(accel_data['y'])+abs(accel_data['z']))-10, 0, True)

def readSensors():
        count = 0
        sensor = ""
        for file in os.listdir("/sys/bus/w1/devices/"):
                if (file.startswith("28-")):
                        readSensor(file)
                        count+=1
        if (count == 0):
                print "No sensor found! Check connection"

def loop():
        while True:
                readSensors()
                time.sleep(3)

def init():
        ADC0832.setup()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BrokerAddress, 1883)

try:
    init()
    loop()
except KeyboardInterrupt:
    ADC0832.destroy()
    print("Bye...")
    exit(0)
except:
    print("***** failed *****")
    exit(1)

