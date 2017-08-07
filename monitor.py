import os
import logging
import datetime
from collections import deque

from . import ublox
from . import util

log = logging.getLogger(__name__)


class JammerMon:
    """
    Class to handle a stream of messages from our uBlox device and
    store events from the stream in a timeseries output file on disk.
    """

    def __init__(self, device, output):
        self._device = device
        self._output = output

        output_dir = os.path.dirname(output)
        if output_dir and not os.path.exists(output_dir):
            os.mkdir(output_dir)

        # Creates the if missing + update mtime
        with open(self._output, 'a'):
            os.utime(self._output, None)

        # Find / create next ID
        previous_id = self.next_logical_id()
        self._next_id = previous_id + 1

        self._file = open(self._output, 'a+')
        self._today = datetime.datetime.now().date()
        self._gps_fixes = deque([], 5)

    def next_logical_id(self):
        last_line = util.last_line(self._output)
        if not last_line:
            return 0

        try:
            previous_id = int(last_line.split(b";")[0])
            return previous_id
        except ValueError as verr:
            log.error("Output file seems to be corrupt.. Try to debug!")
            log.error(verr)

            import sys
            sys.exit(1)

    def write(self, packet):
        last_gps_fix = None
        if self._gps_fixes:
            last_gps_fix = self._gps_fixes[-1]
        else:
            last_gps_fix = {'lat': -1, 'lon': -1}
        packet.update(last_gps_fix)

        fmt = "{timestamp_id};{utc};{jamInd};{lat};{lon}\n"
        self._file.write(fmt.format(**packet))
        self._file.flush()

    def close(self):
        if self._file:
            self._file.close()

    def add_gps(self, lat, lon, height):
        gps = {"lat": lat,
               "lon": lon,
               "height": height}
        self._gps_fixes.append(gps)

    def run(self):
        filter_messages = [
            (ublox.CLASS_MON, ublox.MSG_MON_HW),
            (ublox.CLASS_NAV, ublox.MSG_NAV_POSLLH),
            (ublox.CLASS_NAV, ublox.MSG_NAV_POSECEF),
            (ublox.CLASS_RXM, ublox.MSG_RXM_RAW),
            (ublox.CLASS_RXM, ublox.MSG_RXM_SFRB),
            (ublox.CLASS_AID, ublox.MSG_AID_EPH),
            (ublox.CLASS_NAV, ublox.MSG_NAV_SVINFO),
            (ublox.CLASS_NAV, ublox.MSG_NAV_TIMEGPS),
            (ublox.CLASS_NAV, ublox.MSG_NAV_TIMEUTC),
            (ublox.CLASS_NAV, ublox.MSG_NAV_CLOCK)
        ]

        for msg in self._device.stream():

            # Filter out messages we don't care about
            if msg.msg_type() not in filter_messages:
                continue

            if not msg.valid():
                log.warn("Message invalid: {}".format(msg))

            if not msg.unpacked:
                msg.unpack()

            if msg.msg_type() == (ublox.CLASS_NAV, ublox.MSG_NAV_POSLLH):
                log.info("MSG-NAV-POSLLH: {}".format(msg.fields))
                latitude = msg.fields.get('Latitude', -1) * 1e-7
                longitude = msg.fields.get('Longitude', -1) * 1e-7
                # hMSL: height above Mean Sea Level (in mm)
                # height: height above ellipsoid
                height = msg.fields.get('hMSL', -1) / 1000.0
                self.add_gps(latitude, longitude, height)
                continue

            if msg.msg_type() == (ublox.CLASS_NAV, ublox.MSG_NAV_TIMEGPS):
                log.info("MSG-NAV-TIMEGPS: {}".format(msg.fields))
                continue

            if msg.msg_type() == (ublox.CLASS_NAV, ublox.MSG_NAV_TIMEUTC):
                log.info("MSG-NAV-TIMEUTC: {}".format(msg.fields))
                continue

            if msg.msg_type() == (ublox.CLASS_NAV, ublox.MSG_NAV_CLOCK):
                log.info("MSG-NAV-TIMEUTC: {}".format(msg.fields))
                continue

            if msg.msg_type() != (ublox.CLASS_MON, ublox.MSG_MON_HW):
                continue

            log.info("Name = {}, Fields = {}".format(msg.name(), msg.fields))

            packet = msg.fields
            packet['utc'] = datetime.datetime.utcnow()
            packet['timestamp_id'] = self._next_id
            if 'jamInd' not in msg.fields:
                packet['jamInd'] = -1
            packet['lat'] = 0
            packet['lon'] = 0
            log.debug(packet)

            # Write data to timeseries output file
            self.write(packet)

            self._next_id += 1

