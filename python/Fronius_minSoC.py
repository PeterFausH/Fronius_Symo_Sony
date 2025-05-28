#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pf@nc-x.com 05/2025
# control Fronius (Sony) Battery from 2016 connected to Fronius Symo hybrid from 2016
# if tibber is low price set battlow=90 for 3-4 hours
# Both Charge and Discharge Limits (continued) - If it is desired to charge the battery at a constant rate (ie. ~3328 watts on a 12kWh system),

from pymodbus.client import ModbusTcpClient
# imports for using enumerations
from enum import Enum
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from time import sleep 
import sys

# Parameter für Fronius Batterie-Steuerung setzen
# mit xxrate=100, battmode=3 und battlow=50 wird vom Grid nachgeladen bis Min_SoC bei 50% liegt
battlow=10      # Untergrenze SoC min
chargerate=100    # in Prozent von 3328W, 0 ist aus, 100 ist max
deliverrate=100 # in Prozent von 3328W, 0 ist aus, 100 ist max
battmode=3      # 1 charge-limit, 2 discharge-limit, 3 both limits

device = ModbusTcpClient(host = "172.16.0.171", port = 502, timeout=1) # Adjust as needed
device.connect()

def check_args():
    # wurden 1 Parameter mit angegeben ?
    if len(sys.argv) == 2:
        # parameter zuordnen
        battlow=sys.argv[1]
    else:
        print("bitte so aufrufen:")
        print("  python3 "+sys.argv[0]+ " 50")
        print("um den minSoC bei 50% zu halten")
        print("setze jetzt Default = 10%")
        #print("")
        #defaultwerte
        battlow=10      


def read_reg(register,descr,remark):
    sleep(0.5) # Time in seconds
    result = device.read_holding_registers(register-1, count=1, slave=1)
    if (result.isError()):
        print("not available")
    else:
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        result= decoder.decode_16bit_uint()
        print(f'{register} {descr} {remark} {result/10} %') 

#Argumente checken
check_args()

# Parameterliste ausgeben:
print(f'battlow={battlow}      # Untergrenze SoC min')
print("---------------------")


# Untergrenze Batterie einstellen
register=40321
descr="MinRsvPct"
#alte Speicher-Untergrenze einlesen
read_reg(register,descr,"war bei")
#Speicher-Untergrenze neu setzen
print("setze Speicher-Untergrenze auf",battlow,"%")
device.write_register(register-1, battlow*100, slave=1)
#und prüfen ob ok
read_reg(register,descr,"neue Speicher-Untergrenze gesetzt bei")
print("---------------------")


#Und das war’s auch schon. Zum Schluss schließen wir noch die Verbindung und sind fertig!
device.close()

#Der Effekt ist nach ein paar Sekunden im Wechselrichter-Webinterface oder Solarweb zu sehen.


