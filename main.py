#!/usr/bin/env python

import ublox
import sys
import os
import os.path
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


class JammerMon:
    def __init__(self, output, device_port, baudrate=115200, timeout=2):
        self._output = output

        # Creates the if missing + update mtime
        with open(self._output, 'a'):
            os.utime(self._output, None)

        self._setup_device(device_port, baudrate, timeout)

    def _setup_device(self, device_port, baudrate, timeout):
        self._device = ublox.UBlox(device_port, baudrate, timeout=2)
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

    def run(self):
        for msg in self._device.stream():
            # Filter out messages we don't care about
            if not msg.msg_type() == (ublox.CLASS_MON, ublox.MSG_MON_HW):
                continue

            if not msg.valid():
                log.warn("Message invalid: {}".format(msg))

            if not msg.unpacked:
                msg.unpack()
            log.info("Name = {}, Fields = {}".format(msg.name, msg.fields))


if __name__ == '__main__':
    device_path = "/dev/ttyUBlox"
    output_file = "test_output.dat"
    if not os.path.exists(device_path):
        log.error("uBlox device missing! {}".format(device_path))
    jam_mon = JammerMon(output_file, device_path)
    log.info("Starting Jammer Monitor!")
    
    jam_mon.run()


