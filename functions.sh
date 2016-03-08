#!/bin/bash
## Function Definitions

## Function: trap_push 'COMMAND_STRING'
## Appends a command to a trap, which is needed because default trap behavior is to replace
## previous trap for the same signal
## - 1st arg:  code to add
## - ref: http://stackoverflow.com/questions/3338030/multiple-bash-traps-for-the-same-signal
_trap_push() {
    local next="$1"
    eval "trap_push() {
        local oldcmd='$(echo "$next" | sed -e s/\'/\'\\\\\'\'/g)'
        local newcmd=\"\$1; \$oldcmd\"
        trap -- \"\$newcmd\" EXIT INT TERM HUP
        _trap_push \"\$newcmd\"
    }"
}
_trap_push true

## Function: warn MESSAGE
## Print message to stderr
warn() {
    local message="$1"
    echo "$message" >&2
}

## Function: die MESSAGE
## Print message to stderr and exit the whole process
## Note:
##   Using () makes the command inside them run in a sub-shell and calling a exit from there
##   causes you to exit the sub-shell and not your original shell, hence execution continues in
##   your original shell. To overcome this use { }
## ref: http://stackoverflow.com/questions/3822621/how-to-exit-if-a-command-failed
die() {
    local message="$1"
    warn "$message"
    exit 1
}
