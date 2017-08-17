# Jammer Monitor

This monitor is primarily built to receive a stream of Ublox messages from the EVK-8N device.
These messages contain a lot of data along regular GPS positions and time. The interesting parts for
the purpose of this project is the detect if there are a lot of interference and detect if the device 
sees any attempts of Jamming.


## Quickstart

The code is tested with Python3. Not 100% sure about Python2, but maybe.. :)



For development / testing without having the uBlox device connected:
```
python fake_main.py
```

If you have the uBlox device connected then first figure out the path to the device.
Something like `/dev/cu.usbmodem123124`..

Then first install or make sure you have pyserial
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# then start the monitor
python main.py

# help menu
python main.py --help
```

*Note:*
You want to rename the `template_config.yml` file to something like `config.yml`. Then ofcourse you need to change the settings to reflect your setup. If you don´t want to use a config file you can always use the command line arguments. Check out the "help" menu "--help".


## Configuration file

```yaml
baudrate: 115200
port: /dev/ttyMyDevice
slack_webhook_url: https://hooks.slack.com/services/XXXXX/YYYYY
output: data/out
```

TODO: explain each setting


## Development

Well, its Python so it should be pretty easy to get started with.