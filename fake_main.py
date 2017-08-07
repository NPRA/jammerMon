#!/usr/bin/env python

import ublox
import sys
import os
import os.path
import logging
import unittest
from unittest.mock import patch, Mock

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


class JammerMon:
    def __init__(self, output, device_port, baudrate=115200, timeout=2):
        self._output = output

        # Creates the if missing + update mtime
        with open(self._output, 'a'):
            os.utime(self._output, None)

        self._setup_device(device_port, baudrate, timeout)

    @patch('ublox.UBlox')
    def _setup_device(self, device_port, baudrate, timeout, UBloxMock):
        # self._device = ublox.UBlox(device_port, baudrate, timeout=2)
        self._device = UBloxMock(device_port, baudrate, timeout=2)
        self._device.set_binary()
        self._device.configure_poll_port()
        self._device.configure_poll(ublox.CLASS_CFG, ublox.MSG_CFG_USB)
        self._device.configure_poll(ublox.CLASS_MON, ublox.MSG_MON_HW)
        self._device.configure_port(port=ublox.PORT_SERIAL1, inMask=1, outMask=0)
        self._device.configure_port(port=ublox.PORT_USB, inMask=1, outMask=1)
        self._device.configure_port(port=ublox.PORT_SERIAL2, inMask=1, outMask=0)
        self._device.configure_poll_port()
        self._device.configure_poll_port(ublox.PORT_SERIAL1)
        self._device.configure_poll_port(ublox.PORT_SERIAL2)
        self._device.configure_poll_port(ublox.PORT_USB)
        self._device.configure_solution_rate(rate_ms=1000)

        # self._device.set_preferred_dynamic_model(opts.dynModel)
        # self._device.set_preferred_usePPP(opts.usePPP)

        self._device.configure_message_rate(ublox.CLASS_NAV, ublox.MSG_NAV_POSLLH, 1)
        self._device.configure_message_rate(ublox.CLASS_NAV, ublox.MSG_NAV_STATUS, 1)
        self._device.configure_message_rate(ublox.CLASS_NAV, ublox.MSG_NAV_SOL, 1)
        self._device.configure_message_rate(ublox.CLASS_NAV, ublox.MSG_NAV_VELNED, 1)
        self._device.configure_message_rate(ublox.CLASS_NAV, ublox.MSG_NAV_SVINFO, 1)
        self._device.configure_message_rate(ublox.CLASS_NAV, ublox.MSG_NAV_VELECEF, 1)
        self._device.configure_message_rate(ublox.CLASS_NAV, ublox.MSG_NAV_POSECEF, 1)
        self._device.configure_message_rate(ublox.CLASS_RXM, ublox.MSG_RXM_RAW, 1)
        self._device.configure_message_rate(ublox.CLASS_RXM, ublox.MSG_RXM_SFRB, 1)
        self._device.configure_message_rate(ublox.CLASS_RXM, ublox.MSG_RXM_SVSI, 1)
        self._device.configure_message_rate(ublox.CLASS_RXM, ublox.MSG_RXM_ALM, 1)
        self._device.configure_message_rate(ublox.CLASS_RXM, ublox.MSG_RXM_EPH, 1)
        self._device.configure_message_rate(ublox.CLASS_NAV, ublox.MSG_NAV_TIMEGPS, 5)
        self._device.configure_message_rate(ublox.CLASS_NAV, ublox.MSG_NAV_CLOCK, 5)
        # self._device.configure_message_rate(ublox.CLASS_NAV, ublox.MSG_NAV_DGPS, 5)

        self._device.configure_message_rate(ublox.CLASS_MON, ublox.MSG_MON_HW, 1)

    @staticmethod
    def gen_test_messages():
        import itertools

        m1 = Mock()
        m1.msg_type.return_value = (ublox.CLASS_MON, ublox.MSG_MON_HW)
        m1.valid.return_value = True
        m1.unpacked.return_value = True
        m1.name = "MON-HW"
        m1.fields = {'pinSel': 128000, 'pinBank': 0, 'pinDir': 65536, 'pinVal': 129007, 'noisePerMS': 102, 'agcCnt': 468, 'aStatus': 2, 'aPower': 1, 'flags': 1, 'reserved1': 132, 'usedMask': 125951, 'VP': [10, 11, 12, 13, 14, 15, 1, 0, 2, 3, 255, 16, 255, 18, 19, 54, 53], 'jamInd': 6, 'reserved3': [239, 92], 'pinInq': 0, 'pullH': 128896, 'pullL': 0}

        messages = [
            m1
        ]

        return itertools.cycle(messages)

    def run(self):
        import time

        self._device.stream.return_value = JammerMon.gen_test_messages()
        for msg in self._device.stream():
            # Filter out messages we don't care about
            if not msg.msg_type() == (ublox.CLASS_MON, ublox.MSG_MON_HW):
                continue

            if not msg.valid():
                log.warn("Message invalid: {}".format(msg))

            if not msg.unpacked:
                msg.unpack()
            log.info("Name = {}, Fields = {}".format(msg.name, msg.fields))

            time.sleep(1)




if __name__ == '__main__':
    log.info("This is only for development when you don't have access to the uBlox device!")
    device_path = "/dev/ttyUBlox"
    output_file = "test_output.dat"
    # if not os.path.exists(device_path):
    #    log.error("uBlox device missing! {}".format(device_path))
    jam_mon = JammerMon(output_file, device_path)
    log.info("Starting Jammer Monitor!")

    jam_mon.run()


