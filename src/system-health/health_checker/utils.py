import subprocess


def run_command(command):
    """
    Utility function to run an shell command and return the output.
    :param command: Shell command string.
    :return: Output of the shell command.
    """
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        return process.communicate()[0].encode('utf-8')
    except Exception:
        return None


def get_uptime():
    """
    Utility to get the system up time.
    :return: System up time in seconds.
    """
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    return uptime_seconds
