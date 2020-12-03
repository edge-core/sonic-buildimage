#!/usr/bin/env python3

import os
from collections import defaultdict
from datetime import datetime

from sonic_py_common.logger import Logger

SYSLOG_IDENTIFIER = 'core_cleanup.py'
CORE_FILE_DIR = '/var/core/'
MAX_CORE_FILES = 4


def main():
    logger = Logger(SYSLOG_IDENTIFIER)
    logger.set_min_log_priority_info()

    if os.getuid() != 0:
        logger.log_error('Root required to clean up core files')
        return

    logger.log_info('Cleaning up core files')
    core_files = [f for f in os.listdir(CORE_FILE_DIR) if os.path.isfile(os.path.join(CORE_FILE_DIR, f))]

    core_files_by_process = defaultdict(list)
    for f in core_files:
        process = f.split('.')[0]
        curr_files = core_files_by_process[process]
        curr_files.append(f)

        if len(curr_files) > MAX_CORE_FILES:
            curr_files.sort(reverse=True, key=lambda x: datetime.utcfromtimestamp(int(x.split('.')[1])))
            oldest_core = curr_files[MAX_CORE_FILES]
            logger.log_info('Deleting {}'.format(oldest_core))
            try:
                os.remove(os.path.join(CORE_FILE_DIR, oldest_core))
            except:
                logger.log_error('Unexpected error occured trying to delete {}'.format(oldest_core))
            core_files_by_process[process] = curr_files[0:MAX_CORE_FILES]

    logger.log_info('Finished cleaning up core files')


if __name__ == '__main__':
    main()
