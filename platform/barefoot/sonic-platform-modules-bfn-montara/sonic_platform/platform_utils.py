#!/usr/bin/env python

try:
    import os
    import subprocess

except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

def file_create(path, mode=None):
    def run_cmd(cmd):
        if os.geteuid() != 0:
            cmd.insert(0, 'sudo')
        subprocess.check_output(cmd)

    file_path = os.path.dirname(path)
    if not os.path.exists(file_path):
        run_cmd(['mkdir', '-p', file_path])
    if not os.path.isfile(path):
        run_cmd(['touch', path])
    if (mode is not None):    
        run_cmd(['chmod', mode, path])
