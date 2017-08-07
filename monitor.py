import os
import ublox
import logging

log = logging.getLogger(__name__)


class JammerMon:
    def __init__(self, device, output):
        self._device = device
        self._output = output

        # Creates the if missing + update mtime
        with open(self._output, 'a'):
            os.utime(self._output, None)

    def run(self):
        import time

        for msg in self._device.stream():
            # Filter out messages we don't care about
            if not msg.msg_type() == (ublox.CLASS_MON, ublox.MSG_MON_HW):
                continue

            if not msg.valid():
                log.warn("Message invalid: {}".format(msg))

            if not msg.unpacked:
                msg.unpack()
            log.info("Name = {}, Fields = {}".format(msg.name(), msg.fields))

            time.sleep(1)
