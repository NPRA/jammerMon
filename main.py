#!/usr/bin/env python

"""
TODO: Describe the main entrypoint here!

@author asbjorn
"""

import os
import os.path
import logging
import argparse
import serial
import yaml
import ublox_mon.util as util

import sys
sys.path.append(os.path.realpath(__file__))

import ublox_mon.device
from ublox_mon.monitor import JammerMon

logfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "jamMon.log")
log = logging.getLogger("jamMon")
log.setLevel(logging.DEBUG)
fh = logging.FileHandler(logfile)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.INFO)

log.addHandler(fh)
log.addHandler(ch)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", default="config.yml", help="Configuration file")
parser.add_argument("-p", "--port", help="serial port")
parser.add_argument("-b", "--baudrate", type=int, help="serial baud rate", default=115200)
parser.add_argument("-o", "--output", help="""output file for timeseries data. \
NOTE: A datetime will be added to each file to track records over multiple days.""", default="data/output")
parser.add_argument("-s", "--slack_url", help="Slack webhook url for notifications")
parser.add_argument("-d", "--db_path", help="Path to sqlite3 database file (will be created if missing)")


if __name__ == '__main__':
    args = parser.parse_args()

    config_file = args.config
    cfg = {}

    if os.path.exists(config_file):
        log.info("Reading conf file found.. '{}'".format(config_file))

        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

    device_path = cfg.get("port", args.port)
    output_file = cfg.get("output", args.output)
    slack_url   = cfg.get("slack_webhook_url", args.slack_url)
    db_path     = cfg.get("db_path", args.db_path)

    if not device_path or not os.path.exists(device_path):
        log.error("uBlox device missing! {}".format(device_path))
        sys.exit(1)

    try:
        device = ublox_mon.device.EVK8N(device_path)

        log.info("Starting Jammer Monitor!")
        jam_mon = JammerMon(device, output_file)
        jam_mon.run()

    except serial.seriaulutil.SerialExceptkion as se:
        log.warn("SerialException: Most likely lost connection to serial device.")
        log.exception(se)
        util.slack_notification("jamMon: SerialException occured. Lost connection to serial device!", slack_url)
    except Exception as e:
        log.error("Exception occured in monitor!")
        log.exception(e)
        util.slack_notification("jamMon: Exception occured: {}".format(str(e)), slack_url)
    finally:
        device.close()
        jam_mon.close()
