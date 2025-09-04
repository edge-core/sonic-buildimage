#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2024 Xsightlabs Ltd.

try:
    import os
    import sys
    import logging
    import time
    import signal
    import subprocess
    import shlex
except ImportError as e:
    raise ImportError('%s - required module not found' % str(e))

FUNCTION_NAME = 'as9647_32d_monitor'
SHUTDOWN_FILE = '/usr/share/sonic/firmware/pmon_system_shutdown'
SHUTDOWN_OVERHEAT_CODE = "overheat"

global logger

def handler(signum, frame):
    logging.info('Cause signal %d.', signum)
    sys.exit(0)

def run_command(cmd):
    status = True
    result = ""
    try:
        args = shlex.split(cmd)
        p = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        raw_data, err = p.communicate()
        if err == '':
            result = raw_data.strip()
        else:
            status = False
            result = err.strip()
    except Exception:
        status = False
    return status, result

def main(argv):
    logger = logging.getLogger(FUNCTION_NAME)
    logging.basicConfig(level=logging.INFO)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    logger.info("Started endless loop.")
    while True:
        if os.path.exists(SHUTDOWN_FILE) and os.path.isfile(SHUTDOWN_FILE):
            try:
                file = open(SHUTDOWN_FILE)
                file_content = file.readline().strip()
                if SHUTDOWN_OVERHEAT_CODE == file_content:
                    sts, res = run_command("systemctl is-active swss")
                    if sts == True and res == 'active':
                        # Stop `SWSS` Docker container
                        cmd = "systemctl stop swss"
                        logger.info("Stop `SWSS` Docker container")
                        sts, res = run_command(cmd)
                        if sts == False:
                            logger.error("Failed to run command: {}".format(cmd))

                        # Reset X2 chip
                        cmd = "/opt/xplt/utils/reset_x2.sh"
                        logger.info("Reset X2 chip")
                        sts, res = run_command(cmd)
                        if sts == False:
                            logger.error("Failed to run command: {}".format(cmd))
            except:
                time.sleep(1)
            os.remove(SHUTDOWN_FILE)
        else:
            time.sleep(2)

if __name__ == '__main__':
    main(sys.argv[1:])
