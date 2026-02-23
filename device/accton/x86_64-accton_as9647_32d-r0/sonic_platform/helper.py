import os
import shlex
import subprocess
from sonic_py_common import device_info

HOST_CHK_CMD = "docker > /dev/null 2>&1"
EMPTY_STRING = ""


class APIHelper():

    def __init__(self):
        (self.platform, self.hwsku) = device_info.get_platform_and_hwsku()

    def is_host(self):
        return os.system(HOST_CHK_CMD) == 0

    def is_sonic(self):
        return os.path.exists("/etc/sonic/config_db.json")

    def run_command(self, cmd):
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

    def read_txt_file(self, file_path):
        try:
            with open(file_path, 'r') as fd:
                data = fd.read()
                return data.strip()
        except IOError:
            pass
        return None

    def write_txt_file(self, file_path, value):
        try:
            with open(file_path, 'w') as fd:
                fd.write(str(value))
        except IOError:
            return False
        return True

