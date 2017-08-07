# Jammer Monitor

This monitor is primarily built to receive a stream of Ublox messages from the EVK-8N device.
These messages contain a lot of data along regular GPS positions and time. The interesting parts for
the purpose of this project is the detect if there are a lot of interference and detect if the device 
sees any attempts of Jamming.


## Quickstart

The code is tested with Python3. Not 100% sure about Python2, but maybe.. :)

For development / testing without having the uBlox device connected:
```
python -m jam_mon.fake_main
```

If you have the uBlox device connected then first figure out the path to the device.
Something like `/dev/cu.usbmodem123124`..

Then first install or make sure you have pyserial
```
python -m venv venv
source venv/bin/activate
pip install pyserial

# then start the monitor
python -m jam_mon.main
```

## Development

Well, its Python so it should be pretty easy to get started with.
