import os
import logging
import datetime
from collections import deque
import signal

from . import ublox
from . import util

from . import db, models

log = logging.getLogger("jamMon")


class GracefulKiller:
    kill_now = False

    def __init__(self, notify_callback=None):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

        self._callback = notify_callback

    def exit_gracefully(self, signum, frame):
        self.kill_now = True

        # Send out notification that we were terminated
        log.info("jamMon terminated! signum={}".format(signum))
        if self._callback:
            self._callback("jamMon: Monitor was terminated.")


class JammerMon:
    """
    Class to handle a stream of messages from our uBlox device and
    store events from the stream in a timeseries output file on disk.
    """

    def __init__(self, device, output_prefix, db_path):
        self._device = device
        self._today = datetime.datetime.now().date()
        self._output_prefix = output_prefix

        self.setup_output_file()

        log.info("JammerMon outputting to {}".format(self._output))

        # Setup database
        self._session = db.get_session(db_path)

        # Find / create next ID
        previous_id = self.next_logical_id()
        self._next_id = previous_id + 1

        # List of the last GPS fixes
        self._gps_fixes = deque([], 5)

    def rotate_output_file(self):
        """
        Quick check if we are on a new date or not. If
        new date then we will close the current 'self._file'
        and construct a new one.

        This ensures a neat output file rotation.
        """
        today = datetime.datetime.now().date()

        # If the date is still the same, don't do anything
        if today == self._today:
            return

        # date has changed, create and setup new output file
        self._file.close()
        self.setup_output_file()

    def setup_output_file(self):
        """
        Setup the correct output file based on the "output" prefix
        from the configuration file / input arguments. Each output
        file is separated based on the current date.

        Note that we create the output directory if not existing.
        """
        self._today = datetime.datetime.now().date()
        self._output = "_".join([self._output_prefix, str(self._today)])

        output_dir = os.path.dirname(self._output)
        if output_dir and not os.path.exists(output_dir):
            os.mkdir(output_dir)

        # Creates file if missing + update mtime + write header
        if not os.path.exists(self._output):
            with open(self._output, 'a') as f:
                os.utime(self._output, None)
                f.write("#id;utc;jamInd;lat;lon\n")

        self._file = open(self._output, 'a+')

    def next_logical_id(self):
        last_line = util.last_line(self._output)
        if not last_line:
            return 0

        # Ignore if the last line is a comment!
        if last_line.startswith(b"#"):
            return 0

        try:
            previous_id = int(last_line.split(b";")[0])
            return previous_id + 1
        except ValueError as verr:
            log.error("Output file seems to be corrupt.. Try to debug!")
            log.error(verr)
            return 0

    def write(self, packet):
        # Will only create new output file if the date has changed
        self.rotate_output_file()

        last_gps_fix = None
        if self._gps_fixes:
            last_gps_fix = self._gps_fixes[-1]
        else:
            last_gps_fix = {'lat': -1, 'lon': -1}
        packet.update(last_gps_fix)

        packet["gps_ts"] = packet.get("utc")

        jam_ts = models.JamTimeseries(packet.get("timestamp_id"),
                                      packet.get("jamInd"), packet.get("utc"), packet.get("lat"),
                                      packet.get("lon"), packet.get("gps_ts"))
        self._session.add(jam_ts)

        fmt = "{timestamp_id};{utc};{jamInd};{lat};{lon}\n"
        self._file.write(fmt.format(**packet))

    def close(self):
        if self._file:
            self._file.close()

        # Clean up sqlite3 session
        db.session.remove()

    def add_gps(self, lat, lon, height):
        gps = {"lat": lat,
               "lon": lon,
               "height": height}
        self._gps_fixes.append(gps)

    def run(self, notify_callback=None):
        self.signal_handler = GracefulKiller(notify_callback)

        filter_messages = [
            (ublox.CLASS_MON, ublox.MSG_MON_HW),
            (ublox.CLASS_NAV, ublox.MSG_NAV_POSLLH),
            (ublox.CLASS_NAV, ublox.MSG_NAV_TIMEGPS),
            (ublox.CLASS_NAV, ublox.MSG_NAV_TIMEUTC),
            (ublox.CLASS_NAV, ublox.MSG_NAV_CLOCK)
        ]

        for msg in self._device.stream():
            if self.signal_handler.kill_now:
                break

            # Filter out messages we don't care about
            if msg.msg_type() not in filter_messages:
                continue

            if not msg.valid():
                log.warn("Message invalid: {}".format(msg))

            if not msg.unpacked:
                msg.unpack()

            if msg.msg_type() == (ublox.CLASS_NAV, ublox.MSG_NAV_POSLLH):
                log.debug("MSG-NAV-POSLLH: {}".format(msg.fields))
                latitude = msg.fields.get('Latitude', -1) * 1e-7
                longitude = msg.fields.get('Longitude', -1) * 1e-7
                # hMSL: height above Mean Sea Level (in mm)
                # height: height above ellipsoid
                height = msg.fields.get('hMSL', -1) / 1000.0
                self.add_gps(latitude, longitude, height)
                continue

            if msg.msg_type() == (ublox.CLASS_NAV, ublox.MSG_NAV_TIMEGPS):
                # log.debug("MSG-NAV-TIMEGPS: {}".format(msg.fields))
                continue

            gps_utc = None
            if msg.msg_type() == (ublox.CLASS_NAV, ublox.MSG_NAV_TIMEUTC):
                # log.debug("MSG-NAV-TIMEUTC: {}".format(msg.fields))
                # continue
                # gps_utc = msg.fields.get("")
                year = msg.fields.get("year")
                month = msg.fields.get("month")
                day = msg.fields.get("day")
                hour = msg.fields.get("hour")
                minutes = msg.fields.get("min")
                seconds = msg.fields.get("sec")
                gps_utc = datetime.datetime(year, month, day, hour, minutes, seconds)

            if msg.msg_type() == (ublox.CLASS_NAV, ublox.MSG_NAV_CLOCK):
                # log.debug("MSG-NAV-TIMEUTC: {}".format(msg.fields))
                continue

            if msg.msg_type() != (ublox.CLASS_MON, ublox.MSG_MON_HW):
                continue

            # log.debug("Name = {}, Fields = {}".format(msg.name(), msg.fields))

            packet = msg.fields
            packet['utc'] = datetime.datetime.now().replace(microsecond=0)
            packet['timestamp_id'] = self._next_id
            if 'jamInd' not in msg.fields:
                packet['jamInd'] = -1
            packet['lat'] = 0
            packet['lon'] = 0
            log.debug("{}: {}".format(self._next_id, packet))

            # Write data to timeseries output file
            self.write(packet)

            self._next_id += 1

