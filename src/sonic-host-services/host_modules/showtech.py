"""Show techsupport command handler"""

import host_service
import subprocess
import re

MOD_NAME = 'showtech'

class Showtech(host_service.HostModule):
    """DBus endpoint that executes the "show techsupport" command
    """
    @host_service.method(host_service.bus_name(MOD_NAME), in_signature='s', out_signature='is')
    def info(self, date):

        ERROR_TAR_FAILED = 5
        ERROR_PROCFS_SAVE_FAILED = 6
        ERROR_INVALID_ARGUMENT = 10

        err_dict = {ERROR_INVALID_ARGUMENT: 'Invalid input: Incorrect DateTime format',
                    ERROR_TAR_FAILED: 'Failure saving information into compressed output file',
                    ERROR_PROCFS_SAVE_FAILED: 'Saving of process information failed'}

        cmd = ['/usr/local/bin/generate_dump']
        if date:
            cmd.append("-s")
            cmd.append(date)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    check=True)

        except subprocess.CalledProcessError as err:
            errmsg = err_dict.get(err.returncode)

            if errmsg is None:
                output = 'Error: Failure code {:-5}'.format(err.returncode)
            else:
                output = errmsg

            print("%Error: Host side: Failed: " + str(err.returncode))
            return err.returncode, output

        output_file_match = re.search('\/var\/.*dump.*\.gz', result.stdout)
        output_filename = output_file_match.group()
        return result.returncode, output_filename

def register():
    """Return the class name"""
    return Showtech, MOD_NAME

