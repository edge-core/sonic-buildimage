#!/usr/bin/env bash

rm -f /var/run/rsyslogd.pid

supervisorctl start rsyslogd

. /opt/bfn/install/bin/dma_setup.sh
# . /opt/bfn/install/bin/bf_kdrv_mod_load /opt/bfn/install
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/bfn/install/lib supervisorctl start syncd
