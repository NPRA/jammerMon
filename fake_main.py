#!/usr/bin/env python

from __future__ import absolute_import

import os
import logging
import yaml
import argparse
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
ch.setLevel(logging.INFO)

log.addHandler(fh)
log.addHandler(ch)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", default="config.yml", help="Configuration file")
parser.add_argument("-p", "--port", help="serial port")
parser.add_argument("-b", "--baudrate", type=int, help="serial baud rate", default=115200)
parser.add_argument("-o", "--output", help="""output file for timeseries data. \
NOTE: A datetime will be added to each file to track records over multiple days.""", default="data/test_output")
parser.add_argument("-s", "--slack_url", help="Slack webhook url for notificatoins")
parser.add_argument("-d", "--db_path", help="Path to sqlite3 database file (will be created if missing)")


if __name__ == '__main__':
    args = parser.parse_args()
    log.info("This is only for development when you don't have access to the uBlox device!")
    config_file = args.config
    cfg = {}

    if os.path.exists(config_file):
        log.info("Reading conf file found.. '{}'".format(config_file))

        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

    device_path = cfg.get("port", args.port)
    output_file = cfg.get("output", args.output)
    _ = cfg.get("slack_webhook_url", args.slack_url)
    db_path     = cfg.get("db_path", args.db_path)

    device = ublox_mon.device.FakeEVK8N(device_path)
    jam_mon = JammerMon(device, output_file, db_path)
    log.info("Starting Jammer Monitor!")

    log.info("Running the fake monitor.")
    jam_mon.run()
