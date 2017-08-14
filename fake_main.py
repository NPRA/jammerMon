#!/usr/bin/env python

from __future__ import absolute_import

import os
import logging
import sys
sys.path.append(os.path.realpath(__file__))

import ublox_mon.device
from ublox_mon.monitor import JammerMon

logfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "jamMon_fake.log")
log = logging.getLogger("jamMon")
log.setLevel(logging.DEBUG)
fh = logging.FileHandler(logfile)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.ERROR)

log.addHandler(fh)
log.addHandler(ch)

if __name__ == '__main__':
    log.info("This is only for development when you don't have access to the uBlox device!")
    device_path = "/dev/ttyUBlox"
    output_file = "test_output.dat"
    # if not os.path.exists(device_path):
    #    log.error("uBlox device missing! {}".format(device_path))
    device = ublox_mon.device.FakeEVK8N(device_path)
    jam_mon = JammerMon(device, output_file)
    log.info("Starting Jammer Monitor!")

    jam_mon.run()


