#!/usr/bin/env python
# from pymodbus.client.sync import ModbusSerialClient as ModbusClient


# client = ModbusClient(method='rtu', port='/dev/tty.usbserial-A403IMBZ', baudrate=19200, bytesize=8, stopbits=1, pairity="none", timeout=1)
# client.connect()
# rq = client.write_register(6, 1, unit=2)
# assert(rq.function_code < 0x80)
# rr = client.read_holding_registers(0,72, unit=2)
# print rr.registers[6];

# # assert(rq.function_code < 0x80)     # test that we are not an error
# # assert(rr.registers[0] == 10)
# client.close()






import minimalmodbus
import paho.mqtt.client as paho
import time

def onConnect(client, userdata, rc):
    print("Connected with code: " + str(rc))
    client.subscribe("$SYS/#")

def onMessage(client, userdata, msg):
    print msg.topic+" "+str(msg.payload)

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 2) # port name, slave address (in decimal)

## Read temperature (PV = ProcessValue) ##
temperature = instrument.read_register(0, 0) # Registernumber, number of decimals
print temperature

client = paho.Client()
client.on_connect = onConnect
client.on_message = onMessage

client.connect("iot.eclipse.org")
client.loop_start()
client.publish("wb/paho/temp", temperature)
run = True
while run:
    temperature = instrument.read_register(0, 0)
    client.publish("wb/paho/temp", temperature)    
    time.sleep(10)
