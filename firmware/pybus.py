#!/usr/bin/env python
from pymodbus.client.sync import ModbusSerialClient as ModbusClient


client = ModbusClient(method='rtu', port='/dev/tty.usbserial-A403IMBZ', baudrate=19200, bytesize=8, stopbits=1, pairity="none", timeout=1)
client.connect()
rq = client.write_register(6, 1, unit=2)
assert(rq.function_code < 0x80)
rr = client.read_holding_registers(0,72, unit=2)
print rr.registers[6];

# assert(rq.function_code < 0x80)     # test that we are not an error
# assert(rr.registers[0] == 10)
client.close()
