#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pf@nc-x.com 05/2025
# control Fronius (Sony) Battery from 2016 connected to Fronius Symo hybrid from 2016
# if SoC is above 80% reduce chargepower with chargerate=50

from pymodbus.client import ModbusTcpClient
# imports for using enumerations
from enum import Enum
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from time import sleep 
import sys

# Parameter für Fronius Batterie-Steuerung setzen
# mit chargerate=5 und battmode=1 wird die Beladung auf etwa 165W begrenzt,
# Rest von PV fürs Haus und wird eingespeist.
# mit xxrate=100, battmode=3 und battlow=50 wird vom Grid nachgeladen bis Min_SoC bei 50% liegt
chargerate=100    # in Prozent von 3328W, 0 ist aus, 100 ist max

device = ModbusTcpClient(host = "172.16.0.171", port = 502, timeout=1) # Adjust as needed
device.connect()

def read_reg(register,descr,remark):
    sleep(0.5) # Time in seconds
    result = device.read_holding_registers(register-1, count=1, slave=1)
    if (result.isError()):
        print("not available")
    else:
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        result= decoder.decode_16bit_uint()
        print(f'{register} {descr} {remark} {result/100}')
        return result

# SoC prüfen 40322: ChaState
register=40322
descr="ChaState"
soc=read_reg(register,descr," aktueller SoC")
soc=soc/100

if soc >= 98: 
    chargerate=0  # set to zero to stop charging
elif soc >= 90:
    chargerate=20 # charge very slow
elif soc >= 80:
    chargerate=50 # reduce charge rate
else:
    chargerate=100 # allow full chargerate 

# maximale Speicher-Rate in Prozent einstellen
register=40327
descr="InWRte"
print(f'setze chargerate auf {chargerate}%')
#alte Speicher-Rate einlesen
#read_reg(register,descr," alte Speicher-Rate war")
#Speicher-Rate neu setzen
#print("setze Speicher-Rate auf",chargerate,"%")
device.write_register(register-1, chargerate*100, slave = 1)
#und prüfen ob ok
read_reg(register,descr," neue Speicher-Rate ist")
print("---------------------")


#Und das war’s auch schon. Zum Schluss schließen wir noch die Verbindung und sind fertig!
device.close()

#Der Effekt ist nach ein paar Sekunden im Wechselrichter-Webinterface oder Solarweb zu sehen.


