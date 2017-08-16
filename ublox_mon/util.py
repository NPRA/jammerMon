import os
import os.path
import logging
import subprocess
import shlex

log = logging.getLogger("jamMon")


def last_line(filename):
    """
    Find and return the last line in the file.
    Very efficient implementation - should be blazing fast even for
    large files.
    """
    if not os.path.exists(filename):
        return None

    try:
        with open(filename, 'rb') as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)

            last = f.readline()
            return last
    except OSError:
        return None


def slack_notification(msg, url):
    cmd = """curl -X POST --data-urlencode \
        'payload={{"channel": "#tran-notifications", "username": "webhookbot", \
        "text": "{}", \
        "icon_emoji": ":ghost:"}}' \
        {}"""
    splitted_args = cmd.format(msg, url)
    args = shlex.split(splitted_args)
    try:
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        log.error("Unable to send Slack notification!")
        log.exception(e)
