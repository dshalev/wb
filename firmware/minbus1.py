import paho.mqtt.client as paho
import time
import json
import ssl
from pymodbus.client.sync import ModbusSerialClient as ModbusClient


instrument = ModbusClient(method='rtu', port='/dev/tty.usbserial-A403IMBZ', baudrate=9600, bytesize=8, stopbits=1, pairity="none", timeout=1)
instrument.connect()

def onConnect(client, userdata, rc):
    print("Connected with code: " + str(rc))
    client.subscribe("aws/things/WBHomeServerNew/shadow/update")
    client.subscribe("$aws/things/WBHomeServerNew/shadow/update/#")

def onMessage(client, userdata, msg):
    global instrument
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
					setPoint = 48
					if roomNum == "room_2":
						setPoint = 51
					if roomNum == "room_3":
						setPoint = 54

					if "room_name" in room:
						serverRoom["room_name"] = room["room_name"]
					if "set_point" in room:
						if room["set_point"] < 40:
							room["set_point"] = 40
						if room["set_point"] > 90:
							room["set_point"] = 90
						instrument.write_register(setPoint, room["set_point"], unit=1)
						serverRoom["set_point"] = room["set_point"]
					if "fan" in room:
						serverRoom["fan"] = room["fan"]
					if "power" in room:

						if room["power"] == 0:
							# serverRoom["set_point"] = serverRoom["room_temp"]
							instrument.write_register(setPoint, serverRoom["room_temp"], unit=1)
						else:
							instrument.write_register(setPoint, serverRoom["set_point"], unit=1)


			# if "power" in deltaData["state"]:
			# 	serverData["state"]["reported"]["power"] = deltaData["state"]["power"]

			with open('./dummyResponse.json', 'w') as outfile:
				json.dump(serverData, outfile)
		# deltaData = json.loads(str(msg.payload))
		
		# for roomNum, room in deltaData["state"]["rooms"].iteritems():
		# 	if "set_point" in room:
		# 		setPoint = 48
		# 		if roomNum == "room_2":
		# 			setPoint = 51
		# 		if roomNum == "room_3":
		# 			setPoint = 54
		# 		instrument.write_register(setPoint, room["set_point"], unit=1)

		# # if "power" in deltaData["state"]:
         #    instrument.write_register(29, deltaData["state"]["power"])

def updateDummyResponse():
	global instrument
	with open("./dummyResponse.json") as jsonFile:
		jsonData = json.load(jsonFile)
	response =  instrument.read_holding_registers(0, 99, unit=1)
	for serverRumNum, serverRoom in jsonData["state"]["reported"]["rooms"].iteritems():
		if serverRumNum == "room_1":
			serverRoom["room_temp"] = response.registers[44]/10
			serverRoom["damper_open"] = response.registers[11]
			serverRoom["power"] = (1 if response.registers[11] > 10 else 0)
		if serverRumNum == "room_2":
			serverRoom["room_temp"] = response.registers[44]/10
			serverRoom["damper_open"] = response.registers[12]
			serverRoom["power"] = (1 if response.registers[12] > 10 else 0)
		if serverRumNum == "room_3":
			serverRoom["room_temp"] = response.registers[44]/10
			serverRoom["damper_open"] = response.registers[13]
			serverRoom["power"] = (1 if response.registers[13] > 10 else 0)
	with open('./dummyResponse.json', 'w') as outfile:
			json.dump(jsonData, outfile)
	
def createHouseJson(registers):
	house = dict()
	rooms = dict()
	room1Power = (1 if registers[11] > 10 else 0)
	room2Power = (1 if registers[12] > 10 else 0)
	room3Power = (1 if registers[13] > 10 else 0)
	rooms["room_1"] = {
				"set_point": registers[48],
				"damper_open": registers[11],
				"room_temp": registers[44]/10,
				"room_id": 1,
				"power": room1Power,
				"room_name": ""

				}
	rooms["room_2"] = {
				"set_point": registers[51],
				"damper_open": registers[12],
				"room_temp": registers[44]/10,
				"room_id": 2,
				"power": room2Power,
				"room_name": ""
				}
	rooms["room_3"] = {
				"set_point": registers[54],
				"damper_open": registers[13],
				"room_temp": registers[44]/10,
				"room_id": 3,
				"power": room3Power,
				"room_name": ""
				}
	house["rolbit_version"] = registers[0]
	house["power"] = registers[29]
	house["control_temp"] = registers[44]
	house["return_air_sensor_main"] = registers[1]
	house["id"] = 1
	house["rooms"] = rooms

	return house


# instrument = minimalmodbus.Instrument('/dev/tty.usbserial-A403IMBZ', 1) # port name, slave address (in decimal)
# instrument.serial.baudrate = 9600
# instrument.serial.timeout = 60



## Read temperature (PV = ProcessValue) ##
response =  instrument.read_holding_registers(0, 99, unit=1)
regTab = response.registers
instrument.write_register(54, 50)

temperature = regTab[43]
print temperature
client = paho.Client()
client.on_connect = onConnect
client.on_message = onMessage

client.tls_set("/Users/dshalev/dev/IOT/WiseBreeze/aws/7ac393d0f2-certificate.pem.crt", 
				certfile="/Users/dshalev/dev/IOT/WiseBreeze/aws/wbGateWay.pem",
				keyfile="/Users/dshalev/dev/IOT/WiseBreeze/aws/privateKey.pem",
				tls_version=ssl.PROTOCOL_TLSv1_2, 
              	ciphers=None)
client.connect("A1TTLRECU8VD0V.iot.us-east-1.amazonaws.com", port=8883)

client.loop_start()
run = True
while run:
	updateDummyResponse()
	# response =  instrument.read_holding_registers(0, 99, unit=1)
	# regTab = response.registers

	# json = '{"state":{\n"desired":{\n"temperature":' + str(current) +'\n}\n,"reported":{\n"temperature":' + str(current) + '\n}\n}\n}'
	# pubHouse = dict()
	# report = dict()
	# report["reported"] = createHouseJson(regTab) 
	# pubHouse["state"] = report
	# client.publish("$aws/things/WBHomeServerNew/shadow/update", json.dumps(pubHouse))
	# client.publish("aws/things/WBHomeServerNew/shadow/update", json.dumps(pubHouse))
	with open("./dummyResponse.json") as jsonFile:
		jsonData = json.load(jsonFile)
	print json.dumps(jsonData)
	client.publish("$aws/things/WBHomeServerNew/shadow/update", json.dumps(jsonData))
	client.publish("aws/things/WBHomeServerNew/shadow/update", json.dumps(jsonData))
	time.sleep(10)
