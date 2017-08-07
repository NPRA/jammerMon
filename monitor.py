import os
import ublox
import logging

log = logging.getLogger(__name__)


class JammerMon:
    """
    Class to handle a stream of messages from our uBlox device and 
    store events from the stream in a timeseries output file on disk.
    """

    def __init__(self, device, output):
        self._device = device
        self._output = output

        # Creates the if missing + update mtime
        with open(self._output, 'a'):
            os.utime(self._output, None)

        self._file = None

    def write(self, packet):
        # id;utc;lat;lon;jam_ind
        fmt = "{id};{utc};{lat};{lon};{jam_ind}\n"

        self._file.write(fmt.format(*packet))

    def close(self):
        if self._file:
            self._file.close()

    def run(self):
        self._file = open(self._output, 'a+')

        for msg in self._device.stream():
            # Filter out messages we don't care about
            if not msg.msg_type() == (ublox.CLASS_MON, ublox.MSG_MON_HW):
                continue

            if not msg.valid():
                log.warn("Message invalid: {}".format(msg))

            if not msg.unpacked:
                msg.unpack()

            log.info("Name = {}, Fields = {}".format(msg.name(), msg.fields))
