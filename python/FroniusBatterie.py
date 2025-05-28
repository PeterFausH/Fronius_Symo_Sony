#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pf@nc-x.com 05/2025
# control Fronius (Sony) Battery from 2016 connected to Fronius Symo hybrid from 2016
# todo: use battmode, battlow and chargerate as args
# if tibber is low price set battlow=90 for 3-4 hours
# if wallbox is active, set battmode=2 to avoid draining battery
# if SoC is above 80% reduce chargepower with chargerate=50
# Both Charge and Discharge Limits (continued) - If it is desired to charge the battery at a constant rate (ie. ~3328 watts on a 12kWh system),
# StorCtl_Mod should be set to value 3. Concurrently, Charge Limit should be set to +50% and Discharge Limit should be set to -50%.
# With these settings, the Charge Limit will prevent the battery charging from the sun at greater than 3328 watts (the excess will be fed to the grid instead),
# while the Discharge Limit will keep the charge rate at 3328 watts if the sun is insufficient (using grid power if required).
# StorCrl_Mod 0 should be no limits

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
battlow=10      # Untergrenze SoC min
chargerate=100    # in Prozent von 3328W, 0 ist aus, 100 ist max
deliverrate=100 # in Prozent von 3328W, 0 ist aus, 100 ist max
battmode=3      # 1 charge-limit, 2 discharge-limit, 3 both limits

device = ModbusTcpClient(host = "172.16.0.171", port = 502, timeout=1) # Adjust as needed
device.connect()


def check_args():
    # wurden 4 Parameter mit angegeben ?
    if len(sys.argv) == 5:
        # parameter zuordnen
        battlow=sys.argv[1]
        chargerate=sys.argv[2]
        deliverrate=sys.argv[3]
        battmode=sys.argv[4]
    else:
        print("bitte so aufrufen:")
        print("  python3 FroniusBatterie.py 10 100 100 3")
        print("")
        print("")
        print("")
        #defaultwerte
        battlow=10      
        chargerate=100  
        deliverrate=100 
        battmode=3      


def read_reg(register,descr,remark):
    sleep(0.5) # Time in seconds
    result = device.read_holding_registers(register-1, count=1, slave=1)
    if (result.isError()):
        print("not available")
    else:
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        result= decoder.decode_16bit_uint()
        print(f'{register}: {result} - {descr} {remark}') 

#Argumente checken
check_args()

# Parameterliste ausgeben:
print(f'battlow={battlow}      # Untergrenze SoC min')
print(f'chargerate={chargerate}  # in Prozent, 0 ist aus, 100 ist max')
print(f'deliverrate={deliverrate} # in Prozent, 0 ist aus, 100 ist max')
#StorCtl_Mod = 1 (activates Charge Limit)
#StorCtl_Mod = 2 (activates Discharge Limit)
#StorCtl_Mod = 3 (activates both Charge and Discharge Limits)
print(f'battmode={battmode}      # 1 für charge, 2 für discharge 3 beide limits')
print("---------------------")

#erstmal einlesen welchen Zustand wir haben im Register Speicherkontrolle
register=40319
descr="StorCtl_Mod"
read_reg(register,descr," alten Speichermodus einlesen")
#Speicherbatterie ein- oder ausschalten mit #bit 0 = charge, bit 1 = discharge
print("setze Speichermodus auf:",battmode," 1 für charge, 2 für discharge")
device.write_register(register-1, battmode, slave=1) # bei 2 ist Batterie abgeschaltet
#geänderten Modus einlesen
read_reg(register,descr," neuer Speichermodus")
print("---------------------")

# maximale Entlade-Rate in Prozent einstellen (Faktor 100)
register=40326
descr="OutWRte"
#alte Entlade-Rate einlesen
read_reg(register,descr," alte Entladerate")
#Entlade-Rate neu setzen
print("setze Entlade-Rate auf",deliverrate,"%")
device.write_register(register-1, deliverrate*100, slave = 1)
#und prüfen ob ok
read_reg(register,descr," neue Entlade-Rate")
print("---------------------")

# maximale Speicher-Rate in Prozent einstellen
register=40327
descr="InWRte"
#alte Speicher-Rate einlesen
read_reg(register,descr," alte Speicher-Rate")
#Speicher-Rate neu setzen
print("setze Speicher-Rate auf",chargerate,"%")
device.write_register(register-1, chargerate*100, slave = 1)
#und prüfen ob ok
read_reg(register,descr," neue Speicher-Rate")
print("---------------------")


# Untergrenze Batterie einstellen
register=40321
descr="MinRsvPct"
#alte Speicher-Untergrenze einlesen
read_reg(register,descr," alte Speicher-Untergrenze")
#Speicher-Untergrenze neu setzen
print("setze Speicher-Untergrenze auf",battlow,"%")
device.write_register(register-1, battlow*100, slave=1)
#und prüfen ob ok
read_reg(register,descr," neue Speicher-Untergrenze")
print("---------------------")


#Und das war’s auch schon. Zum Schluss schließen wir noch die Verbindung und sind fertig!
device.close()

#Der Effekt ist nach ein paar Sekunden im Wechselrichter-Webinterface oder Solarweb zu sehen.


