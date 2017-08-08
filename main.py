#!/usr/bin/env python

"""
TODO: Describe the main entrypoint here!

@author asbjorn
"""

import sys
import os
import os.path
import logging
from . import monitor
from .device import EVK8N
import argparse


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="serial port", required=True)
parser.add_argument("-b", "--baudrate", type=int, help="serial baud rate", default=115200)
parser.add_argument("-o", "--output", help="""output file for timeseries data. 
NOTE: A datetime will be added to each file to track records over multiple days.""", default="data/output")


if __name__ == '__main__':
    args = parser.parse_args()

    device_path = args.port
    output_file = args.output
    if not os.path.exists(device_path):
        log.error("uBlox device missing! {}".format(device_path))

    device = EVK8N(args.port)
    jam_mon = monitor.JammerMon(device, output_file)
    log.info("Starting Jammer Monitor!")

    jam_mon.run()
