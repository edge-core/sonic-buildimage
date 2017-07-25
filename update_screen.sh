#!/bin/bash

lockfile .screen

target_list_file=/tmp/target_list
touch ${target_list_file}

function scroll_up {
# Check if TERM is available
[[ "${TERM}" == "dumb" ]] && return

for i in $(cat ${target_list_file}); do
    tput cuu1
    tput el
done
}

function print_targets {
# Check if TERM is available
[[ "${TERM}" == "dumb" ]] && return

count=1
for i in $(cat ${target_list_file}); do
    printf "[ %02d ] [ %s ]\n" "${count}" "$i"
    ((count++))
done
}

function remove_target {
# Check if TERM is available
[[ "${TERM}" == "dumb" ]] && echo "[ finished ] [ $1 ] " && return

old_list=$(cat ${target_list_file})
rm ${target_list_file}
for target in ${old_list}; do
    if [[ "${target}" != "$1" ]]; then
        echo ${target} >> ${target_list_file}
    fi
done
touch ${target_list_file}
}

function add_target {
# Check if TERM is available
[[ "${TERM}" == "dumb" ]] && echo "[ building ] [ $1 ] " && return

echo $1 >> ${target_list_file}
}

function print_targets_delay {
sleep 2 && print_targets  && rm -f .screen &
exit 0
}

while getopts ":a:d:e:" opt; do
    case $opt in
        a)
            scroll_up
            add_target ${OPTARG}
            print_targets
            ;;
        d)
            scroll_up
            remove_target ${OPTARG}
            print_targets
            ;;
        e)
            scroll_up
            remove_target ${OPTARG}
            echo "[ FAIL LOG START ] [ ${OPTARG} ]"
            cat ${OPTARG}.log
            echo "[  FAIL LOG END  ] [ ${OPTARG} ]"
            print_targets_delay
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            rm -f .screen
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            rm -f .screen
            exit 1
            ;;
    esac
done

rm -f .screen
