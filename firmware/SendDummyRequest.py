import paho.mqtt.client as paho
import time
import json
import ssl

def onConnect(client, userdata, rc):
    print("Connected with code: " + str(rc))

def onMessage(client, userdata, msg):
	print "message arrived"

client = paho.Client()
client.on_connect = onConnect
client.on_message = onMessage

client.tls_set("../aws/7ac393d0f2-certificate.pem.crt", 
				certfile="../aws/wbGateWay.pem",
				keyfile="../aws/privateKey.pem",
				tls_version=ssl.PROTOCOL_TLSv1_2, 
              	ciphers=None)
client.connect("A1TTLRECU8VD0V.iot.us-east-1.amazonaws.com", port=8883)
# client.loop_start()
with open("./DummyRequest.json") as jsonFile:
	jsonData = json.load(jsonFile)
	
	print json.dumps(jsonData)
	client.publish("$aws/things/WBHomeServerNew/shadow/update", json.dumps(jsonData))
	client.publish("aws/things/WBHomeServerNew/shadow/update", json.dumps(jsonData))
