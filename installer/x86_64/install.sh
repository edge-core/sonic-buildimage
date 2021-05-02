#!/bin/sh

#  Copyright (C) 2014-2015 Curt Brune <curt@cumulusnetworks.com>
#  Copyright (C) 2014-2015 david_yang <david_yang@accton.com>
#
#  SPDX-License-Identifier:     GPL-2.0

# Appends a command to a trap, which is needed because default trap behavior is to replace
# previous trap for the same signal
# - 1st arg:  code to add
# - ref: http://stackoverflow.com/questions/3338030/multiple-bash-traps-for-the-same-signal
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

# Main
set -e
cd $(dirname $0)

if [ -d "/etc/sonic" ]; then
    echo "Installing SONiC in SONiC"
    install_env="sonic"
elif grep -Fxqs "DISTRIB_ID=onie" /etc/lsb-release > /dev/null
then
    echo "Installing SONiC in ONIE"
    install_env="onie"
else
    echo "Installing SONiC in BUILD"
    install_env="build"
fi

if [ -r ./machine.conf ]; then
. ./machine.conf
fi

if [ -r ./onie-image.conf ]; then
. ./onie-image.conf
fi

echo "ONIE Installer: platform: $platform"

# Make sure run as root or under 'sudo'
if [ $(id -u) -ne 0 ]
    then echo "Please run as root"
    exit 1
fi

# get running machine from conf file
if [ -r /etc/machine.conf ]; then
    . /etc/machine.conf
elif [ -r /host/machine.conf ]; then
    . /host/machine.conf
elif [ "$install_env" != "build" ]; then
    echo "cannot find machine.conf"
    exit 1
fi

echo "onie_platform: $onie_platform"

# Get platform specific linux kernel command line arguments
ONIE_PLATFORM_EXTRA_CMDLINE_LINUX=""

# Default var/log device size in MB
VAR_LOG_SIZE=4096

[ -r platforms/$onie_platform ] && . platforms/$onie_platform

# Pick up console port and speed from install enviroment if not defined yet.
# Console port and speed setting in cmdline is like "console=ttyS0,9600n",
# so we can use pattern 'console=ttyS[0-9]+,[0-9]+' to match it.
# If failed to get the speed and ttyS from cmdline then set them to default: ttyS0 and 9600
if [ -z "$CONSOLE_PORT" ]; then
    console_ttys=$(cat /proc/cmdline | grep -Eo 'console=ttyS[0-9]+' | cut -d "=" -f2)
    if [ -z "$console_ttys" -o "$console_ttys" = "ttyS0" ]; then
        CONSOLE_PORT=0x3f8
        CONSOLE_DEV=0
    elif [ "$console_ttys" = "ttyS1" ]; then
        CONSOLE_PORT=0x2f8
        CONSOLE_DEV=1
    elif [ "$console_ttys" = "ttyS2" ]; then
        CONSOLE_PORT=0x3e8
        CONSOLE_DEV=2
    elif [ "$console_ttys" = "ttyS3" ]; then
        CONSOLE_PORT=0x2e8
        CONSOLE_DEV=3
    fi
fi

if [ -z "$CONSOLE_SPEED" ]; then
    speed=$(cat /proc/cmdline | grep -Eo 'console=ttyS[0-9]+,[0-9]+' | cut -d "," -f2)
    if [ -z "$speed" ]; then
        CONSOLE_SPEED=9600
    else
        CONSOLE_SPEED=$speed
    fi
fi

# Install demo on same block device as ONIE
if [ "$install_env" != "build" ]; then
    onie_dev=$(blkid | grep ONIE-BOOT | head -n 1 | awk '{print $1}' |  sed -e 's/:.*$//')
    blk_dev=$(echo $onie_dev | sed -e 's/[1-9][0-9]*$//' | sed -e 's/\([0-9]\)\(p\)/\1/')

    # check if we have an nvme device
    blk_suffix=
    echo $blk_dev | grep -q nvme0 && blk_suffix="p"

    # Note: ONIE has no mount setting for / with device node, so below will be empty string
    cur_part=$(cat /proc/mounts | awk "{ if(\$2==\"/\") print \$1 }" | grep $blk_dev || true)

    [ -b "$blk_dev" ] || {
        echo "Error: Unable to determine block device of ONIE install"
        exit 1
    }
fi

# If running in ONIE
if [ "$install_env" = "onie" ]; then
    # The onie bin tool prefix
    onie_bin=
    # The persistent ONIE directory location
    onie_root_dir=/mnt/onie-boot/onie
    # The onie file system root
    onie_initrd_tmp=/
fi

# The build system prepares this script by replacing %%DEMO-TYPE%%
# with "OS" or "DIAG".
demo_type="%%DEMO_TYPE%%"

# The build system prepares this script by replacing %%IMAGE_VERSION%%
# with git revision hash as a version identifier
image_version="%%IMAGE_VERSION%%"
timestamp="$(date -u +%Y%m%d)"

demo_volume_label="SONiC-${demo_type}"
demo_volume_revision_label="SONiC-${demo_type}-${image_version}"

# auto-detect whether BIOS or UEFI
if [ -d "/sys/firmware/efi/efivars" ] ; then
    firmware="uefi"
else
    firmware="bios"
fi

if [ "$install_env" = "onie" ]; then
    # determine ONIE partition type
    onie_partition_type=$(${onie_bin} onie-sysinfo -t)
    # demo partition size in MB
    demo_part_size="%%ONIE_IMAGE_PART_SIZE%%"
    if [ "$firmware" = "uefi" ] ; then
        create_demo_partition="create_demo_uefi_partition"
    elif [ "$onie_partition_type" = "gpt" ] ; then
        create_demo_partition="create_demo_gpt_partition"
    elif [ "$onie_partition_type" = "msdos" ] ; then
        create_demo_partition="create_demo_msdos_partition"
    else
        echo "ERROR: Unsupported partition type: $onie_partition_type"
        exit 1
    fi
fi

# Creates a new partition for the DEMO OS.
#
# arg $1 -- base block device
#
# Returns the created partition number in $demo_part
demo_part=""
# TODO: remove reference to "ACS-OS" after all baseimages are upgraded
legacy_volume_label="ACS-OS"
create_demo_gpt_partition()
{
    blk_dev="$1"

    # Create a temp fifo and store string in variable
    tmpfifo=$(mktemp -u)
    trap_push "rm $tmpfifo || true"
    mkfifo -m 600 "$tmpfifo"

    # See if demo partition already exists
    demo_part=$(sgdisk -p $blk_dev | grep -e "$demo_volume_label" -e "$legacy_volume_label" | awk '{print $1}')
    if [ -n "$demo_part" ] ; then
        # delete existing partitions
        # if there are multiple partitions matched, we should delete each one, except the current OS's
        # Note: You can use any character as a separator for sed, not just '/'
        echo "$demo_part" > $tmpfifo &
        while read -r part_index; do
            if [ "$blk_dev$part_index" = "$cur_part" ]; then continue; fi
            echo "deleting partition $part_index ..."
            # if the partition is already mounted, umount first
            df $blk_dev$part_index 2>/dev/null && {
                umount $blk_dev$part_index || {
                    echo "Error: Unable to umount $blk_dev$part_index"
                    exit 1
                }
            }
            sgdisk -d $part_index $blk_dev || {
                echo "Error: Unable to delete partition $part_index on $blk_dev"
                exit 1
            }
            partprobe || {
                echo "Error: Unable to partprobe"
                exit 1
            }
        done < $tmpfifo
    fi

    # ASSUME: there are no more than 99999 partitions in a block device
    all_part=$(sgdisk -p $blk_dev | awk "{if (\$1 > 0 && \$1 <= 99999) print \$1}")
    # Get the index of last partition
    # Note: the double quotation marks for echo argument are necessary, otherwise the unquoted version replaces each sequence of
    #   one or more blanks, tabs and newlines with a single space.
    # Ref: http://stackoverflow.com/questions/613572/capturing-multiple-line-output-to-a-bash-variable
    last_part=$(echo "$all_part" | tail -n 1 | awk '{print $1}')
    # Find next available partition
    demo_part=1
    echo "$all_part" > $tmpfifo &
    # Find the first available partition number
    while read -r used_part; do
        echo "Partition #$used_part is in use."
        if [ "$used_part" -ne "$demo_part" ]; then break; fi
        demo_part=`expr $demo_part + 1`
    done < $tmpfifo
    echo "Partition #$demo_part is available"

    # Create new partition
    echo "Creating new $demo_volume_label partition ${blk_dev}${blk_suffix}$demo_part ..."

    if [ "$demo_type" = "DIAG" ] ; then
        # set the GPT 'system partition' attribute bit for the DIAG
        # partition.
        attr_bitmask="0x1"
    else
        attr_bitmask="0x0"
    fi
    sgdisk --new=${demo_part}::+${demo_part_size}MB \
        --attributes=${demo_part}:=:$attr_bitmask \
        --change-name=${demo_part}:$demo_volume_label $blk_dev \
    || {
        echo "Warning: The first trial of creating partition failed, trying the largest aligned available block of sectors on the disk"
        begin=$(sgdisk -F $blk_dev)
        end=$(sgdisk -E $blk_dev)
        sgdisk --new=${demo_part}:$begin:$end \
            --attributes=${demo_part}:=:$attr_bitmask \
            --change-name=${demo_part}:$demo_volume_label $blk_dev
    } || {
        echo "Error: Unable to create partition $demo_part on $blk_dev"
        exit 1
    }
    ## If running in normal Linux, partprobe will complain as below and return non-zero
    ##   Error: Partition(s) 4 on /dev/sda have been written, but we have been unable to inform the kernel of the change,
    ##   probably because it/they are in use.  As a result, the old partition(s) will remain in use.  You should reboot now
    ##   before making further changes.
    partprobe || true
}

create_demo_msdos_partition()
{
    blk_dev="$1"

    # See if demo partition already exists -- look for the filesystem
    # label.
    part_info="$(blkid | grep -e "$demo_volume_label" -e "$legacy_volume_label" | awk -F: '{print $1}')"
    if [ -n "$part_info" ] ; then
        # delete existing partition
        demo_part="$(echo -n $part_info | sed -e s#${blk_dev}##)"
        parted -s $blk_dev rm $demo_part || {
            echo "Error: Unable to delete partition $demo_part on $blk_dev"
            exit 1
        }
        partprobe
    fi

    # Find next available partition
    last_part_info="$(parted -s -m $blk_dev unit s print | tail -n 1)"
    last_part_num="$(echo -n $last_part_info | awk -F: '{print $1}')"
    last_part_end="$(echo -n $last_part_info | awk -F: '{print $3}')"
    # Remove trailing 's'
    last_part_end=${last_part_end%s}
    demo_part=$(( $last_part_num + 1 ))
    demo_part_start=$(( $last_part_end + 1 ))
    # sectors_per_mb = (1024 * 1024) / 512 = 2048
    sectors_per_mb=2048
    demo_part_end=$(( $demo_part_start + ( $demo_part_size * $sectors_per_mb ) - 1 ))

    # Create new partition
    echo "Creating new partition ${blk_dev}$demo_part ..."
    parted -s --align optimal $blk_dev unit s \
      mkpart primary $demo_part_start $demo_part_end set $demo_part boot on || {
        echo "ERROR: Problems creating msdos partition $demo_part on: $blk_dev"
        exit 1
    }
    partprobe
}

# For UEFI systems, create a new partition for the DEMO OS.
#
# arg $1 -- base block device
#
# Returns the created partition number in $demo_part
create_demo_uefi_partition()
{
    create_demo_gpt_partition "$1"

    # erase any related EFI BootOrder variables from NVRAM.
    for b in $(efibootmgr | grep -e "$demo_volume_label" -e "$legacy_volume_label" | awk '{ print $1 }') ; do
        local num=${b#Boot}
        # Remove trailing '*'
        num=${num%\*}
        efibootmgr -b $num -B > /dev/null 2>&1
    done
}

# Install legacy BIOS GRUB for DEMO OS
demo_install_grub()
{
    local demo_mnt="$1"
    local blk_dev="$2"

    # Pretend we are a major distro and install GRUB into the MBR of
    # $blk_dev.
    grub-install --boot-directory="$onie_initrd_tmp/$demo_mnt" --recheck "$blk_dev" || {
        echo "ERROR: grub-install failed on: $blk_dev"
        exit 1
    }

    if [ "$demo_type" = "DIAG" ] ; then
        # Install GRUB in the partition also.  This allows for
        # chainloading the DIAG image from another OS.
        #
        # We are installing GRUB in a partition, as opposed to the
        # MBR.  With this method block lists are used to refer to the
        # the core.img file.  The sector locations of core.img may
        # change whenever the file system in the partition is being
        # altered (files copied, deleted etc.). For more info, see
        # https://bugzilla.redhat.com/show_bug.cgi?id=728742 and
        # https://bugzilla.redhat.com/show_bug.cgi?id=730915.
        #
        # The workaround for this is to set the immutable flag on
        # /boot/grub/i386-pc/core.img using the chattr command so that
        # the sector locations of the core.img file in the disk is not
        # altered. The immutable flag on /boot/grub/i386-pc/core.img
        # needs to be set only if GRUB is installed to a partition
        # boot sector or a partitionless disk, not in case of
        # installation to MBR.

        core_img="$demo_mnt/grub/i386-pc/core.img"
        # remove immutable flag if file exists during the update.
        [ -f "$core_img" ] && chattr -i $core_img

        grub_install_log=$(mktemp)
        grub-install --force --boot-directory="$onie_initrd_tmp/$demo_mnt" \
            --recheck "$demo_dev" > /$grub_install_log 2>&1 || {
            echo "ERROR: grub-install failed on: $demo_dev"
            cat $grub_install_log && rm -f $grub_install_log
            exit 1
        }

        rm -f $grub_install_log

        # restore immutable flag on the core.img file as discussed
        # above.
        [ -f "$core_img" ] && chattr +i $core_img

    fi

}

# Install UEFI BIOS GRUB for DEMO OS
demo_install_uefi_grub()
{
    local demo_mnt="$1"
    local blk_dev="$2"

    # make sure /boot/efi is mounted
    if ! mount | grep -q "/boot/efi"; then
        mount /boot/efi
    fi

    # Look for the EFI system partition UUID on the same block device as
    # the ONIE-BOOT partition.
    local uefi_part=0
    for p in $(seq 8) ; do
        if sgdisk -i $p $blk_dev | grep -q C12A7328-F81F-11D2-BA4B-00A0C93EC93B ; then
            uefi_part=$p
            break
        fi
    done

    [ $uefi_part -eq 0 ] && {
        echo "ERROR: Unable to determine UEFI system partition"
        exit 1
    }

    grub_install_log=$(mktemp)
    grub-install \
        --no-nvram \
        --bootloader-id="$demo_volume_label" \
        --efi-directory="/boot/efi" \
        --boot-directory="$demo_mnt" \
        --recheck \
        "$blk_dev" > /$grub_install_log 2>&1 || {
        echo "ERROR: grub-install failed on: $blk_dev"
        cat $grub_install_log && rm -f $grub_install_log
        exit 1
    }
    rm -f $grub_install_log

    # Configure EFI NVRAM Boot variables.  --create also sets the
    # new boot number as active.
    efibootmgr --quiet --create \
        --label "$demo_volume_label" \
        --disk $blk_dev --part $uefi_part \
        --loader "/EFI/$demo_volume_label/grubx64.efi" || {
        echo "ERROR: efibootmgr failed to create new boot variable on: $blk_dev"
        exit 1
    }

}

image_dir="image-$image_version"

if [ "$install_env" = "onie" ]; then
    eval $create_demo_partition $blk_dev
    demo_dev=$(echo $blk_dev | sed -e 's/\(mmcblk[0-9]\)/\1p/')$demo_part
    echo $blk_dev | grep -q nvme0 && demo_dev=$(echo $blk_dev | sed -e 's/\(nvme[0-9]n[0-9]\)/\1p/')$demo_part

    # Make filesystem
    mkfs.ext4 -L $demo_volume_label $demo_dev

    # Mount demo filesystem
    demo_mnt=$(${onie_bin} mktemp -d) || {
        echo "Error: Unable to create file system mount point"
        exit 1
    }
    trap_push "${onie_bin} fuser -km $demo_mnt || ${onie_bin} umount $demo_mnt || ${onie_bin} rmdir $demo_mnt || true"
    ${onie_bin} mount -t ext4 -o defaults,rw $demo_dev $demo_mnt || {
        echo "Error: Unable to mount $demo_dev on $demo_mnt"
        exit 1
    }

elif [ "$install_env" = "sonic" ]; then
    demo_mnt="/host"
    # Get current SONiC image (grub/aboot/uboot)
    eval running_sonic_revision="$(cat /proc/cmdline | sed -n 's/^.*loop=\/*image-\(\S\+\)\/.*$/\1/p')"
    # Verify SONiC image exists
    if [ ! -d "$demo_mnt/image-$running_sonic_revision" ]; then
        echo "ERROR: SONiC installation is corrupted: path $demo_mnt/image-$running_sonic_revision doesn't exist"
        exit 1
    fi
    # Prevent installing existing SONiC if it is running
    if [ "$image_dir" = "image-$running_sonic_revision" ]; then
        echo "Not installing SONiC version $running_sonic_revision, as current running SONiC has the same version"
        exit 0
    fi
    # Remove extra SONiC images if any
    for f in $demo_mnt/image-* ; do
        if [ -d $f ] && [ "$f" != "$demo_mnt/image-$running_sonic_revision" ] && [ "$f" != "$demo_mnt/$image_dir" ]; then
            echo "Removing old SONiC installation $f"
            rm -rf $f
        fi
    done
else
    demo_mnt="build_raw_image_mnt"
    demo_dev=$cur_wd/"%%OUTPUT_RAW_IMAGE%%"

    mkfs.ext4 -L $demo_volume_label $demo_dev

    echo "Mounting $demo_dev on $demo_mnt..."
    mkdir $demo_mnt
    mount -t auto -o loop $demo_dev $demo_mnt
fi

echo "Installing SONiC to $demo_mnt/$image_dir"

# Create target directory or clean it up if exists
if [ -d $demo_mnt/$image_dir ]; then
    echo "Directory $demo_mnt/$image_dir/ already exists. Cleaning up..."
    rm -rf $demo_mnt/$image_dir/*
else
    mkdir $demo_mnt/$image_dir || {
        echo "Error: Unable to create SONiC directory"
        exit 1
    }
fi

# Decompress the file for the file system directly to the partition
if [ x"$docker_inram" = x"on" ]; then
    # when disk is small, keep dockerfs.tar.gz in disk, expand it into ramfs during initrd
    unzip -o $ONIE_INSTALLER_PAYLOAD -d $demo_mnt/$image_dir
else
    unzip -o $ONIE_INSTALLER_PAYLOAD -x "$FILESYSTEM_DOCKERFS" -d $demo_mnt/$image_dir

    if [ "$install_env" = "onie" ]; then
        TAR_EXTRA_OPTION="--numeric-owner"
    else
        TAR_EXTRA_OPTION="--numeric-owner --warning=no-timestamp"
    fi
    mkdir -p $demo_mnt/$image_dir/$DOCKERFS_DIR
    unzip -op $ONIE_INSTALLER_PAYLOAD "$FILESYSTEM_DOCKERFS" | tar xz $TAR_EXTRA_OPTION -f - -C $demo_mnt/$image_dir/$DOCKERFS_DIR
fi

if [ "$install_env" = "onie" ]; then
    # Store machine description in target file system
    if [ -f /etc/machine-build.conf ]; then
        # onie_ variable are generate at runtime.
        # they are no longer hardcoded in /etc/machine.conf
        # also remove single quotes around the value
        set | grep ^onie | sed -e "s/='/=/" -e "s/'$//" > $demo_mnt/machine.conf
    else
        cp /etc/machine.conf $demo_mnt
    fi

    # Store installation log in target file system
    rm -f $onie_initrd_tmp/tmp/onie-support*.tar.bz2
    ${onie_bin} onie-support /tmp
    mv $onie_initrd_tmp/tmp/onie-support*.tar.bz2 $demo_mnt/$image_dir/

    if [ "$firmware" = "uefi" ] ; then
        demo_install_uefi_grub "$demo_mnt" "$blk_dev"
    else
        demo_install_grub "$demo_mnt" "$blk_dev"
    fi
fi

# Create a minimal grub.cfg that allows for:
#   - configure the serial console
#   - allows for grub-reboot to work
#   - a menu entry for the DEMO OS
#   - menu entries for ONIE

grub_cfg=$(mktemp)
trap_push "rm $grub_cfg || true"

# Set a few GRUB_xxx environment variables that will be picked up and
# used by the 50_onie_grub script.  This is similiar to what an OS
# would specify in /etc/default/grub.
#
# GRUB_SERIAL_COMMAND
# GRUB_CMDLINE_LINUX

[ -r ./platform.conf ] && . ./platform.conf

# Check if the CPU vendor is 'Intel' and disable c-states if True
CPUVENDOR="$(cat /proc/cpuinfo | grep -m 1 vendor_id | awk '{print $3}')"
echo "Switch CPU vendor is: $CPUVENDOR"
if echo "$CPUVENDOR" | grep -i 'Intel' >/dev/null 2>&1; then
    echo "Switch CPU cstates are: disabled"
    CSTATES="intel_idle.max_cstate=0"
else
    CSTATES=""
fi

DEFAULT_GRUB_SERIAL_COMMAND="serial --port=${CONSOLE_PORT} --speed=${CONSOLE_SPEED} --word=8 --parity=no --stop=1"
DEFAULT_GRUB_CMDLINE_LINUX="console=tty0 console=ttyS${CONSOLE_DEV},${CONSOLE_SPEED}n8 quiet $CSTATES"
GRUB_SERIAL_COMMAND=${GRUB_SERIAL_COMMAND:-"$DEFAULT_GRUB_SERIAL_COMMAND"}
GRUB_CMDLINE_LINUX=${GRUB_CMDLINE_LINUX:-"$DEFAULT_GRUB_CMDLINE_LINUX"}
export GRUB_SERIAL_COMMAND
export GRUB_CMDLINE_LINUX

# Add common configuration, like the timeout and serial console.
cat <<EOF > $grub_cfg
$GRUB_SERIAL_COMMAND
terminal_input console serial
terminal_output console serial

set timeout=5

EOF

# Add the logic to support grub-reboot and grub-set-default
cat <<EOF >> $grub_cfg
if [ -s \$prefix/grubenv ]; then
    load_env
fi
if [ "\${saved_entry}" ]; then
    set default="\${saved_entry}"
fi
if [ "\${next_entry}" ]; then
    set default="\${next_entry}"
    unset next_entry
    save_env next_entry
fi
if [ "\${onie_entry}" ]; then
    set next_entry="\${default}"
    set default="\${onie_entry}"
    unset onie_entry
    save_env onie_entry next_entry
fi

EOF

if [ "$demo_type" = "DIAG" ] ; then
    # Make sure ONIE install mode is the default boot mode for the
    # diag partition.
    cat <<EOF >> $grub_cfg
set default=ONIE
EOF
    $onie_root_dir/tools/bin/onie-boot-mode -q -o install
fi

# Add a menu entry for the SONiC OS
# Note: assume that apparmor is supported in the kernel
demo_grub_entry="$demo_volume_revision_label"
if [ "$install_env" = "sonic" ]; then
    old_sonic_menuentry=$(cat /host/grub/grub.cfg | sed "/$running_sonic_revision/,/}/!d")
    grub_cfg_root=$(echo $old_sonic_menuentry | sed -e "s/.*root\=\(.*\)rw.*/\1/")
    onie_menuentry=$(cat /host/grub/grub.cfg | sed "/menuentry ONIE/,/}/!d")
elif [ "$install_env" = "build" ]; then
    grub_cfg_root=%%SONIC_ROOT%%
else # install_env = "onie"
    uuid=$(blkid "$demo_dev" | sed -ne 's/.* UUID=\"\([^"]*\)\".*/\1/p')
    if [ -z "$uuid" ]; then
        grub_cfg_root=$demo_dev
    else
        grub_cfg_root=UUID=$uuid
    fi
fi

cat <<EOF >> $grub_cfg
menuentry '$demo_grub_entry' {
        search --no-floppy --label --set=root $demo_volume_label
        echo    'Loading $demo_volume_label $demo_type kernel ...'
        insmod gzio
        if [ x$grub_platform = xxen ]; then insmod xzio; insmod lzopio; fi
        insmod part_msdos
        insmod ext2
        linux   /$image_dir/boot/vmlinuz-4.19.0-12-2-amd64 root=$grub_cfg_root rw $GRUB_CMDLINE_LINUX  \
                net.ifnames=0 biosdevname=0 \
                loop=$image_dir/$FILESYSTEM_SQUASHFS loopfstype=squashfs                       \
                systemd.unified_cgroup_hierarchy=0 \
                apparmor=1 security=apparmor varlog_size=$VAR_LOG_SIZE usbcore.autosuspend=-1 $ONIE_PLATFORM_EXTRA_CMDLINE_LINUX
        echo    'Loading $demo_volume_label $demo_type initial ramdisk ...'
        initrd  /$image_dir/boot/initrd.img-4.19.0-12-2-amd64
}
EOF

if [ "$install_env" = "onie" ]; then
    # Add menu entries for ONIE -- use the grub fragment provided by the
    # ONIE distribution.
    $onie_root_dir/grub.d/50_onie_grub >> $grub_cfg
    mkdir -p $onie_initrd_tmp/$demo_mnt/grub
else
cat <<EOF >> $grub_cfg
$old_sonic_menuentry
$onie_menuentry
EOF
fi

if [ "$install_env" = "build" ]; then
    cp $grub_cfg $demo_mnt/grub.cfg
    umount $demo_mnt
else
    cp $grub_cfg $onie_initrd_tmp/$demo_mnt/grub/grub.cfg
fi

cd /

echo "Installed SONiC base image $demo_volume_label successfully"
