#! /bin/bash

VERBOSE=no

function debug()
{
    /usr/bin/logger "$0 : $1"
    if [[ x"${VERBOSE}" == x"yes" ]]; then
        echo "$(date) $0: $1"
    fi
}


function disable_watchdog()
{
    if [[ -x /usr/bin/watchdog ]]; then
        debug "Disabling Watchdog during bootup"
        /usr/bin/watchdog -d
    fi
}

disable_watchdog
