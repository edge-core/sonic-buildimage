#!/bin/bash

# Provide file paths to archive for debug image as relative to src subdir
#
for i in $debug_src_archive
do
    find $i/ -name "*.c" -o -name "*.cpp" -o -name "*.h" -o -name "*.hpp" -type f
done

