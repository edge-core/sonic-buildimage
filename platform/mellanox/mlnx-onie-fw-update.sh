#!/bin/sh

# Copyright (C) 2019 Mellanox Technologies Ltd.
# Copyright (C) 2019 Michael Shych <michaelsh@mellanox.com>
#
# SPDX-License-Identifier:     GPL-2.0

this_script=${ONIE_FWPKG_PROGRAM_NAME:-$(basename $(realpath $0))}

onie_mount=/mnt/onie-boot
os_boot=/host
onie_partition=

export ONIE_FWPKG_PROGRAM_NAME=$(basename $(realpath $0))

usage()
{
cat <<EOF
  update
    The 'update' command will reboot system to ONIE update mode
    and ONIE will perform automatically update of previously 
    added (i.e. pending) FW (ONIE itself, BIOS or CPLD) image.

EOF
}

enable_onie_access()
{
	onie_partition=$(fdisk -l | grep "ONIE boot" | awk '{print $1}')
	if [ ! -d $onie_mount ]; then
		mkdir /mnt/onie-boot
	fi
	mount $onie_partition /mnt/onie-boot
	if [ ! -e /lib/onie ]; then
		ln -s /mnt/onie-boot/onie/tools/lib/onie /lib/onie
	fi
	PATH=/sbin:/usr/sbin:/bin:/usr/bin:$onie_mount/onie/tools/bin/
	export PATH
}

clean_onie_access()
{
	rm -f /lib/onie
	umount $onie_partition
}

change_grub_boot_order()
{
	grub-editenv $os_boot/grub/grubenv set onie_entry=ONIE
	grub-editenv $onie_mount/grub/grubenv set onie_mode=update
	return 0
}

show_pending()
{
	curr_dir=$(pwd)
	cd $onie_mount/onie/update/pending || return 0
	num=$(find . -type f | wc -l)
	if [ $num -ge 1 ]; then
		echo "Number of FW update pending files are: "$num
		ls -l * | awk {'print $9"  "$5"  "$7"-"$6" "$8'}
	else
		echo "There is no pending files for FW update."
	fi
	cd $curr_dir

	return $num
}

# Process command arguments
cmd=$1
# optional argument
name="$2"

if [ -z "$cmd" ] ; then
	# Default to 'show' if no command is specified.
	cmd="show"
fi

case "$cmd" in
	add | remove)
		[ -z "$name" ] && {
			echo "ERROR: This command requires a firmware update file name."
			echo "Run '$this_script help' for complete details."
			exit 1
		}
		;;
	update)
		enable_onie_access
		show_pending
		rc=$?
		if [ $rc -ne 0 ]; then
			change_grub_boot_order
			rc=$?
			clean_onie_access
			exit $rc
		else
			echo "ERROR: NO FW images for update."
			echo "Run: $this_script add <image>  before update."
			clean_onie_access
			exit 1
		fi
		;;
	purge | show | show-results | show-log | show-pending | help)
		;;
	*)
		echo "Unknown command: $cmd"
		exit 1
	;;
esac

enable_onie_access
$onie_mount/onie/tools/bin/onie-fwpkg "$@"
rc=$?
if [ $cmd = "help" ]; then
	usage
fi
clean_onie_access

exit $rc
