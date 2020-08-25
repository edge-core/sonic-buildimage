#!/usr/bin/env python

import swsssdk
import time

def enable_counter_group(db, name):
    info = {}
    info['FLEX_COUNTER_STATUS'] = 'enable'
    db.mod_entry("FLEX_COUNTER_TABLE", name, info)

def enable_counters():
    db = swsssdk.ConfigDBConnector()
    db.connect()
    enable_counter_group(db, 'PORT')
    enable_counter_group(db, 'RIF')
    enable_counter_group(db, 'QUEUE')
    enable_counter_group(db, 'PFCWD')
    enable_counter_group(db, 'PG_WATERMARK')
    enable_counter_group(db, 'QUEUE_WATERMARK')
    enable_counter_group(db, 'BUFFER_POOL_WATERMARK')
    enable_counter_group(db, 'PORT_BUFFER_DROP')

def get_uptime():
    with open('/proc/uptime') as fp:
        return float(fp.read().split(' ')[0])

def main():
    # If the switch was just started (uptime less than 5 minutes),
    # wait for 3 minutes and enable counters
    # otherwise wait for 60 seconds and enable counters
    uptime = get_uptime()
    if uptime < 300:
        time.sleep(180)
    else:
        time.sleep(60)
    enable_counters()

if __name__ == '__main__':
    main()
