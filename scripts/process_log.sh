#!/bin/bash

add_timestamp=""

while getopts ":t" opt; do
    case $opt in
        t)
            add_timestamp="y"
            ;;
    esac
done

while IFS= read -r line; do
    if [ $add_timestamp ]; then
        printf '[%s] ' "$(date +%T)"
    fi
    printf '%s\n' "$line"
done


