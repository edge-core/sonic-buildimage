import datetime
import subprocess
import time

import yaml

from .log import log_debug, log_err, log_info, log_warn, log_crit


def run_command(command, shell=False, hide_errors=False):
    """
    Run a linux command. The command is defined as a list. See subprocess.Popen documentation on format
    :param command: command to execute. Type: List of strings
    :param shell: execute the command through shell when True. Type: Boolean
    :param hide_errors: don't report errors to syslog when True. Type: Boolean
    :return: Tuple: integer exit code from the command, stdout as a string, stderr as a string
    """
    log_debug("execute command '%s'." % str(command))
    p = subprocess.Popen(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        if not hide_errors:
            print_tuple = p.returncode, str(command), stdout, stderr
            log_err("command execution returned %d. Command: '%s', stdout: '%s', stderr: '%s'" % print_tuple)

    return p.returncode, stdout, stderr


def wait_for_daemons(daemons, seconds):
    """
    Wait until FRR daemons are ready for requests
    :param daemons: list of FRR daemons to wait
    :param seconds: number of seconds to wait, until raise an error
    """
    stop_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    log_info("Start waiting for FRR daemons: %s" % str(datetime.datetime.now()))
    while datetime.datetime.now() < stop_time:
        ret_code, out, err = run_command(["vtysh", "-c", "show daemons"], hide_errors=True)
        if ret_code == 0 and all(daemon in out for daemon in daemons):
            log_info("All required daemons have connected to vtysh: %s" % str(datetime.datetime.now()))
            return
        else:
            log_warn("Can't read daemon status from FRR: %s" % str(err))
        time.sleep(0.1)  # sleep 100 ms
    raise RuntimeError("FRR daemons hasn't been started in %d seconds" % seconds)


def read_constants():
    """ Read file with constants values from /etc/sonic/constants.yml """
    with open('/etc/sonic/constants.yml') as fp:
        content = yaml.load(fp) # FIXME: , Loader=yaml.FullLoader)
        if "constants" not in content:
            log_crit("/etc/sonic/constants.yml doesn't have 'constants' key")
            raise Exception("/etc/sonic/constants.yml doesn't have 'constants' key")
        return content["constants"]