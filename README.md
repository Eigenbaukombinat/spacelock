# spacelock

## installation
```
git clone https://github.com/Eigenbaukombinat/spacelock.git
cd spacelock
python3 -m venv .
bin/pip install -r requirements.txt
```

## run

via supervisor:

```
[program:spacelock]
directory = /home/<user>/spacelock
command=/home/<user>/spacelock/bin/python /home/<user>/spacelock/spacelock.py --mqtt_broker=<mqtt host>
user = <user>
```
