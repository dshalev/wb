import paho.mqtt.client as paho
import time
import json
import ssl

def onConnect(client, userdata, rc):
    print("Connected with code: " + str(rc))
    client.subscribe("aws/things/WBHomeServerNew/shadow/update")
    client.subscribe("$aws/things/WBHomeServerNew/shadow/update/#")

def onMessage(client, userdata, msg):
	print "message arrived"
	if "delta" in msg.topic:
		print(msg.topic+" "+str(msg.payload))

		with open("./dummyResponse.json") as jsonFile:
			serverData = json.load(jsonFile)
		deltaData = json.loads(str(msg.payload))
		# serverData["state"]["reported"]["rooms"] = deltaData["state"]["rooms"]
		# for key, room in serverData["state"]["reported"]["rooms"].iteritems():
		# 	room["room_temp"] = 70
		for roomNum, room in deltaData["state"]["rooms"].iteritems():
			for serverRoomNum, serverRoom in serverData["state"]["reported"]["rooms"].iteritems():
				if serverRoomNum == roomNum:
					if "room_name" in room:
						serverRoom["room_name"] = room["room_name"]
					if "set_point" in room:
						serverRoom["set_point"] = room["set_point"]
					if "fan" in room:
						serverRoom["fan"] = room["fan"]
					if "power" in room:
						serverRoom["power"] = room["power"]

		if "power" in deltaData["state"]:
			serverData["state"]["reported"]["power"] = deltaData["state"]["power"]
	
		with open('./dummyResponse.json', 'w') as outfile:
			json.dump(serverData, outfile)
		with open("./dummyResponse.json") as jsonFile:
			jsonData = json.load(jsonFile)
		print json.dumps(jsonData)
		client.publish("$aws/things/WBHomeServerNew/shadow/update", json.dumps(jsonData))
		client.publish("aws/things/WBHomeServerNew/shadow/update", json.dumps(jsonData))

client = paho.Client()
client.on_connect = onConnect
client.on_message = onMessage

client.tls_set("../aws/7ac393d0f2-certificate.pem.crt", 
				certfile="../aws/wbGateWay.pem",
				keyfile="../aws/privateKey.pem",
				tls_version=ssl.PROTOCOL_TLSv1_2, 
              	ciphers=None)
client.connect("A1TTLRECU8VD0V.iot.us-east-1.amazonaws.com", port=8883)

client.loop_start()
run = True
while run:
	with open("./dummyResponse.json") as jsonFile:
		jsonData = json.load(jsonFile)
	client.publish("$aws/things/WBHomeServerNew/shadow/update", json.dumps(jsonData))
	client.publish("aws/things/WBHomeServerNew/shadow/update", json.dumps(jsonData))
	shouldWrite = False
	for serverRoomNum, serverRoom in jsonData["state"]["reported"]["rooms"].iteritems():
		if serverRoom["set_point"] > serverRoom["room_temp"]:
			serverRoom["room_temp"] += 1
			shouldWrite = True
		if serverRoom["set_point"] < serverRoom["room_temp"]:
			serverRoom["room_temp"] -= 1
			shouldWrite = True

	if shouldWrite:
		with open('./dummyResponse.json', 'w') as outfile:
			json.dump(jsonData, outfile)
	time.sleep(10)


		