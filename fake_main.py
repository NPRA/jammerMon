#!/usr/bin/env python

from __future__ import absolute_import

import sys
import logging
import monitor
from device import FakeEVK8N

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

if __name__ == '__main__':
    log.info("This is only for development when you don't have access to the uBlox device!")
    device_path = "/dev/ttyUBlox"
    output_file = "test_output.dat"
    # if not os.path.exists(device_path):
    #    log.error("uBlox device missing! {}".format(device_path))
    device = FakeEVK8N(device_path)
    jam_mon = monitor.JammerMon(device, output_file)
    log.info("Starting Jammer Monitor!")

    jam_mon.run()


