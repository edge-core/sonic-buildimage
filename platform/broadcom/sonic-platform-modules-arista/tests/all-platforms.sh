#!/bin/bash
#
# This script provides a simple helper to test if the initscripts for all
# platforms work.
# It runs in simulation mode and don't actually initialize anything but still
# checks most of the codepaths
#

# enable simulation mode
extra_args="-s"
errors=false

continue_on_failure=${CONTINUE_ON_FAILURE:-false}
python=${PYTHON:-python}

# TODO: check if library in venv
script="arista"
[ -x /usr/bin/arista ] && script="/usr/bin/arista"
[ -x utils/arista ] && script="utils/arista"

try_execute() {
   echo "Run: $script $extra_args $@"
   if ! $python $script $extra_args "$@" &>/dev/null; then
      $python $script $extra_args -v "$@"
      errors=true
      $continue_on_failure || exit 1
   fi
}

echo "Trying general commands"
for cmd in help syseeprom platforms; do
   try_execute $cmd
done
echo

# per platform commands
echo "Trying per platform commands"
for platform in $($script $extra_args platforms | awk '/ - / { print $2 }'); do
   try_execute -p $platform setup
   try_execute -p $platform setup --reset --background
   try_execute -p $platform reset --toggle
   try_execute -p $platform clean
   try_execute -p $platform dump
   echo
done

if $errors; then
   echo "Error were seen during testing"
   exit 1
fi

echo "All done!"
