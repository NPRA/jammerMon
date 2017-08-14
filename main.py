#!/usr/bin/env python

"""
TODO: Describe the main entrypoint here!

@author asbjorn
"""

import os
import os.path
import logging
import argparse
import sys
sys.path.append(os.path.realpath(__file__))

import ublox_mon.device
from ublox_mon.monitor import JammerMon

logfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "jamMon.log")
#logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger("jamMon")
log.setLevel(logging.DEBUG)
fh = logging.FileHandler(logfile)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.ERROR)

log.addHandler(fh)
log.addHandler(ch)

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="serial port", required=True)
parser.add_argument("-b", "--baudrate", type=int, help="serial baud rate", default=115200)
parser.add_argument("-o", "--output", help="""output file for timeseries data. \
NOTE: A datetime will be added to each file to track records over multiple days.""", default="data/output")


if __name__ == '__main__':
    args = parser.parse_args()

    device_path = args.port
    output_file = args.output
    if not os.path.exists(device_path):
        log.error("uBlox device missing! {}".format(device_path))

    try:
        device = ublox_mon.device.EVK8N(args.port)

        log.info("Starting Jammer Monitor!")
        jam_mon = JammerMon(device, output_file)
        jam_mon.run()
    except Exception as e:
        log.error("Exception occured in monitor!")
        log.exception(e)
    finally:
        jam_mon.close()
