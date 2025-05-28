# Fronius_Symo_Sony
run a 10yrs old inverter and battery grid friendly / netzdienlicher Betrieb Batteriespeicher


## Features

    - [x] easy to use small python scripts
    - [x] made for crontab
    - [x] support parameter / args

## Installation

copy the python *.py files in your folder
modify your presets and IP-adress of your Fronius inverter
```python
battlow=10      # Untergrenze SoC min
chargerate=100    # in Prozent von 3328W, 0 ist aus, 100 ist max
deliverrate=100 # in Prozent von 3328W, 0 ist aus, 100 ist max
battmode=3      # 1 charge-limit, 2 discharge-limit, 3 both limits

device = ModbusTcpClient(host = "172.16.0.171", port = 502, timeout=1) # Adjust as needed
```


## Usage
### fill battery slowly 

call the python script to slowly charge your battery from 80% to 98% from i.e. noon til 5pm every 2 minutes

```sh
# m h  dom mon dow   command
# Batterie vom Fronius im Chalet sanft voll-laden:
*/2 12-17 * * * /usr/bin/python3 /home/peterf/python-scripte/modbus/FroniusBatterie_full.py &>/dev/null
```

### flatten duck-curve

call the script to avoid the duck-curbe at 8 in the morning til noon. Check proper hours for your location and your  amount of storage.
as i'm calling it having chargerate 5%, it still charges the battery with 3.328W * 0.05 at around 165W. 
All Watts deliverd from PV above 165W are fed into the grid.

```sh
# Batterie vom Fronius netzdienlich betreiben, morgens erstmal einspeisen, nicht laden. 2.Parameter Chargerate 5%
0 8 * * *  /usr/bin/python3 /home/peterf/python-scripte/modbus/FroniusBatterie.py 10 5 100 3
# Batterie vom Fronius netzdienlich betreiben, mittags im Peak dann aufladen statt einspeisen, Chargerate 100%
0 12 * * *  /usr/bin/python3 /home/peterf/python-scripte/modbus/FroniusBatterie.py 10 100 100 3
```
### forced charging from grid in cheap hours

using dynamic prices for your energy, like aWATTar or tibber, you may call Fronius_minSoC.py for a few hours with parameter 90
this will charge your battery from grid upto 90% SoC. At ending of cheap hours call it with parameter 10 to allow discharging of battery

```sh
# Batterie vom Fronius im Chalet zwangsladen:
0 02 * * * /usr/bin/python3 /home/peterf/python-scripte/modbus/Fronius_minSoC.py 90 &>/dev/null
0 05 * * * /usr/bin/python3 /home/peterf/python-scripte/modbus/Fronius_minSoC.py 10 &>/dev/null
```

## Authors

[Max Kueng](https://github.com/maxkueng), [Yoshua Wuyts](https://github.com/yoshuawuyts)
and [contributors](https://github.com/yoshuawuyts/vmd/graphs/contributors).

## License

[MIT](https://tldrlegal.com/license/mit-license)

[fronius-logo-url]: https://upload.wikimedia.org/wikipedia/commons/2/2e/Fronius-logo.png
[fronius-24h-url]: https://www.energie-experten.org/fileadmin/_processed_/0/b/csm_Neues_Fronius_Energy_Package_verspricht_24_Stunden_Solarstrom_Foto_Fronius_International_GmbH_38716e4307.jpg

