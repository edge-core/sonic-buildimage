#!/bin/bash
## This script is to automate the preparation for a debian file system, which will be used for
## an ONIE installer image.
##
## USAGE:
##   USERNAME=username PASSWORD=password ./build_debian
## ENVIRONMENT:
##   USERNAME
##          The name of the default admin user
##   PASSWORD
##          The password, expected by chpasswd command

## Default user
[ -n "$USERNAME" ] || {
    echo "Error: no or empty USERNAME"
    exit 1
}

## Password for the default user
[ -n "$PASSWORD" ] || {
    echo "Error: no or empty PASSWORD"
    exit 1
}

## Include common functions
. functions.sh

## Enable debug output for script
set -x -e

## docker engine version (with platform)
DOCKER_VERSION=5:18.09.2~3-0~debian-stretch
LINUX_KERNEL_VERSION=4.9.0-9-2

## Working directory to prepare the file system
FILESYSTEM_ROOT=./fsroot
PLATFORM_DIR=platform
## Hostname for the linux image
HOSTNAME=sonic
DEFAULT_USERINFO="Default admin user,,,"

## Read ONIE image related config file
. ./onie-image.conf
[ -n "$ONIE_IMAGE_PART_SIZE" ] || {
    echo "Error: Invalid ONIE_IMAGE_PART_SIZE in onie image config file"
    exit 1
}
[ -n "$ONIE_INSTALLER_PAYLOAD" ] || {
    echo "Error: Invalid ONIE_INSTALLER_PAYLOAD in onie image config file"
    exit 1
}
[ -n "$FILESYSTEM_SQUASHFS" ] || {
    echo "Error: Invalid FILESYSTEM_SQUASHFS in onie image config file"
    exit 1
}

## Prepare the file system directory
if [[ -d $FILESYSTEM_ROOT ]]; then
    sudo rm -rf $FILESYSTEM_ROOT || die "Failed to clean chroot directory"
fi
mkdir -p $FILESYSTEM_ROOT
mkdir -p $FILESYSTEM_ROOT/$PLATFORM_DIR
mkdir -p $FILESYSTEM_ROOT/$PLATFORM_DIR/x86_64-grub
touch $FILESYSTEM_ROOT/$PLATFORM_DIR/firsttime

## make / as a mountpoint in chroot env, needed by dockerd
pushd $FILESYSTEM_ROOT
sudo mount --bind . .
popd

## Build a basic Debian system by debootstrap
echo '[INFO] Debootstrap...'
sudo http_proxy=$http_proxy debootstrap --variant=minbase --arch amd64 stretch $FILESYSTEM_ROOT http://debian-archive.trafficmanager.net/debian

## Config hostname and hosts, otherwise 'sudo ...' will complain 'sudo: unable to resolve host ...'
sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo '$HOSTNAME' > /etc/hostname"
sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo '127.0.0.1       $HOSTNAME' >> /etc/hosts"
sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo '127.0.0.1       localhost' >> /etc/hosts"

## Config basic fstab
sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c 'echo "proc /proc proc defaults 0 0" >> /etc/fstab'
sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c 'echo "sysfs /sys sysfs defaults 0 0" >> /etc/fstab'

## Setup proxy
[ -n "$http_proxy" ] && sudo /bin/bash -c "echo 'Acquire::http::Proxy \"$http_proxy\";' > $FILESYSTEM_ROOT/etc/apt/apt.conf.d/01proxy"

## Note: mounting is necessary to makedev and install linux image
echo '[INFO] Mount all'
## Output all the mounted device for troubleshooting
mount
trap_push 'sudo umount $FILESYSTEM_ROOT/proc || true'
sudo LANG=C chroot $FILESYSTEM_ROOT mount proc /proc -t proc

## Pointing apt to public apt mirrors and getting latest packages, needed for latest security updates
sudo cp files/apt/sources.list $FILESYSTEM_ROOT/etc/apt/
sudo cp files/apt/apt.conf.d/{81norecommends,apt-{clean,gzip-indexes,no-languages}} $FILESYSTEM_ROOT/etc/apt/apt.conf.d/
sudo LANG=C chroot $FILESYSTEM_ROOT bash -c 'apt-mark auto `apt-mark showmanual`'

## Note: set lang to prevent locale warnings in your chroot
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y update
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y upgrade
echo '[INFO] Install packages for building image'
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y install makedev psmisc systemd-sysv

## Create device files
echo '[INFO] MAKEDEV'
sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c 'cd /dev && MAKEDEV generic'
## Install initramfs-tools and linux kernel
## Note: initramfs-tools recommends depending on busybox, and we really want busybox for
## 1. commands such as touch
## 2. mount supports squashfs
## However, 'dpkg -i' plus 'apt-get install -f' will ignore the recommended dependency. So
## we install busybox explicitly
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y install busybox
echo '[INFO] Install SONiC linux kernel image'
## Note: duplicate apt-get command to ensure every line return zero
sudo dpkg --root=$FILESYSTEM_ROOT -i $debs_path/initramfs-tools-core_*.deb || \
    sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y install -f
sudo dpkg --root=$FILESYSTEM_ROOT -i $debs_path/initramfs-tools_*.deb || \
    sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y install -f
sudo dpkg --root=$FILESYSTEM_ROOT -i $debs_path/linux-image-${LINUX_KERNEL_VERSION}-amd64_*.deb || \
    sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y install -f
sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y install acl
sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y install dmidecode

## Update initramfs for booting with squashfs+overlay
cat files/initramfs-tools/modules | sudo tee -a $FILESYSTEM_ROOT/etc/initramfs-tools/modules > /dev/null

## Hook into initramfs: change fs type from vfat to ext4 on arista switches
sudo mkdir -p $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-premount/
sudo cp files/initramfs-tools/arista-convertfs $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-premount/arista-convertfs
sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-premount/arista-convertfs
sudo cp files/initramfs-tools/arista-hook $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-premount/arista-hook
sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-premount/arista-hook
sudo cp files/initramfs-tools/mke2fs $FILESYSTEM_ROOT/etc/initramfs-tools/hooks/mke2fs
sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/hooks/mke2fs
sudo cp files/initramfs-tools/setfacl $FILESYSTEM_ROOT/etc/initramfs-tools/hooks/setfacl
sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/hooks/setfacl

# Hook into initramfs: rename the management interfaces on arista switches
sudo cp files/initramfs-tools/arista-net $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-premount/arista-net
sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-premount/arista-net

# Hook into initramfs: resize root partition after migration from another NOS to SONiC on Dell switches
sudo cp files/initramfs-tools/resize-rootfs $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-premount/resize-rootfs
sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-premount/resize-rootfs

## Hook into initramfs: after partition mount and loop file mount
## 1. Prepare layered file system
## 2. Bind-mount docker working directory (docker aufs cannot work over aufs rootfs)
sudo cp files/initramfs-tools/union-mount $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-bottom/union-mount
sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-bottom/union-mount
sudo cp files/initramfs-tools/varlog $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-bottom/varlog
sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-bottom/varlog
# Management interface (eth0) dhcp can be optionally turned off (during a migration from another NOS to SONiC)
#sudo cp files/initramfs-tools/mgmt-intf-dhcp $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-bottom/mgmt-intf-dhcp
#sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/scripts/init-bottom/mgmt-intf-dhcp
sudo cp files/initramfs-tools/union-fsck $FILESYSTEM_ROOT/etc/initramfs-tools/hooks/union-fsck
sudo chmod +x $FILESYSTEM_ROOT/etc/initramfs-tools/hooks/union-fsck
pushd $FILESYSTEM_ROOT/usr/share/initramfs-tools/scripts/init-bottom && sudo patch -p1 < $OLDPWD/files/initramfs-tools/udev.patch; popd

## Install latest intel ixgbe driver
sudo cp $files_path/ixgbe.ko $FILESYSTEM_ROOT/lib/modules/${LINUX_KERNEL_VERSION}-amd64/kernel/drivers/net/ethernet/intel/ixgbe/ixgbe.ko

## Install docker
echo '[INFO] Install docker'
## Install apparmor utils since they're missing and apparmor is enabled in the kernel
## Otherwise Docker will fail to start
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y install apparmor
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y install apt-transport-https \
                                                       ca-certificates \
                                                       curl \
                                                       gnupg2 \
                                                       software-properties-common
sudo https_proxy=$https_proxy LANG=C chroot $FILESYSTEM_ROOT curl -o /tmp/docker.gpg -fsSL https://download.docker.com/linux/debian/gpg
sudo LANG=C chroot $FILESYSTEM_ROOT apt-key add /tmp/docker.gpg
sudo LANG=C chroot $FILESYSTEM_ROOT rm /tmp/docker.gpg
sudo LANG=C chroot $FILESYSTEM_ROOT add-apt-repository \
                                    "deb [arch=amd64] https://download.docker.com/linux/debian stretch stable"
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get update
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y install docker-ce=${DOCKER_VERSION}
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y remove software-properties-common gnupg2

## Add docker config drop-in to select aufs, otherwise it may select other storage driver
sudo mkdir -p $FILESYSTEM_ROOT/etc/systemd/system/docker.service.d/
## Note: $_ means last argument of last command
sudo cp files/docker/docker.service.conf $_
## Fix systemd race between docker and containerd
sudo sed -i '/After=/s/$/ containerd.service/' $FILESYSTEM_ROOT/lib/systemd/system/docker.service

## Create default user
## Note: user should be in the group with the same name, and also in sudo/docker group
sudo LANG=C chroot $FILESYSTEM_ROOT useradd -G sudo,docker $USERNAME -c "$DEFAULT_USERINFO" -m -s /bin/bash
## Create password for the default user
echo "$USERNAME:$PASSWORD" | sudo LANG=C chroot $FILESYSTEM_ROOT chpasswd

## Pre-install hardware drivers
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y install      \
    firmware-linux-nonfree

## Pre-install the fundamental packages
## Note: gdisk is needed for sgdisk in install.sh
## Note: parted is needed for partprobe in install.sh
## Note: ca-certificates is needed for easy_install
## Note: don't install python-apt by pip, older than Debian repo one
sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y install      \
    file                    \
    ifupdown2               \
    iproute2                \
    bridge-utils            \
    isc-dhcp-client         \
    sudo                    \
    vim                     \
    tcpdump                 \
    dbus                    \
    ntp                     \
    ntpstat                 \
    openssh-server          \
    python                  \
    python-setuptools       \
    monit                   \
    python-apt              \
    traceroute              \
    iputils-ping            \
    net-tools               \
    bsdmainutils            \
    ca-certificates         \
    i2c-tools               \
    efibootmgr              \
    usbutils                \
    pciutils                \
    iptables-persistent     \
    ebtables                \
    logrotate               \
    curl                    \
    kexec-tools             \
    less                    \
    unzip                   \
    gdisk                   \
    sysfsutils              \
    squashfs-tools          \
    grub2-common            \
    rsyslog                 \
    ethtool                 \
    screen                  \
    hping3                  \
    python-scapy            \
    tcptraceroute           \
    mtr-tiny                \
    locales                 \
    flashrom                \
    cgroup-tools

#Adds a locale to a debian system in non-interactive mode
sudo sed -i '/^#.* en_US.* /s/^#//' $FILESYSTEM_ROOT/etc/locale.gen && \
    sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT locale-gen "en_US.UTF-8"
sudo LANG=en_US.UTF-8 DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT update-locale "LANG=en_US.UTF-8"
sudo LANG=C chroot $FILESYSTEM_ROOT bash -c "find /usr/share/i18n/locales/ ! -name 'en_US' -type f -exec rm -f {} +"

# Install certain fundamental packages from stretch-backports in order to get
# more up-to-date (but potentially less stable) versions
sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y -t stretch-backports install \
    picocom

sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y download \
    grub-pc-bin

sudo mv $FILESYSTEM_ROOT/grub-pc-bin*.deb $FILESYSTEM_ROOT/$PLATFORM_DIR/x86_64-grub

## Disable kexec supported reboot which was installed by default
sudo sed -i 's/LOAD_KEXEC=true/LOAD_KEXEC=false/' $FILESYSTEM_ROOT/etc/default/kexec

## Modifty ntp default configuration: disable initial jump (add -x), and disable
## jump when time difference is greater than 1000 seconds (remove -g).
sudo sed -i "s/NTPD_OPTS='-g'/NTPD_OPTS='-x'/" $FILESYSTEM_ROOT/etc/default/ntp

## Fix ping tools permission so non root user can directly use them
## Note: this is a workaround since aufs doesn't support extended attributes
## Ref: https://github.com/moby/moby/issues/5650#issuecomment-303499489
## TODO: remove workaround when the overlay filesystem support extended attributes
sudo chmod u+s $FILESYSTEM_ROOT/bin/ping{,6}

## Remove sshd host keys, and will regenerate on first sshd start
sudo rm -f $FILESYSTEM_ROOT/etc/ssh/ssh_host_*_key*
sudo cp files/sshd/host-ssh-keygen.sh $FILESYSTEM_ROOT/usr/local/bin/
sudo cp -f files/sshd/sshd.service $FILESYSTEM_ROOT/lib/systemd/system/ssh.service
# Config sshd
# 1. Set 'UseDNS' to 'no'
# 2. Configure sshd to close all SSH connetions after 15 minutes of inactivity
sudo augtool -r $FILESYSTEM_ROOT <<'EOF'
touch /files/etc/ssh/sshd_config/EmptyLineHack
rename /files/etc/ssh/sshd_config/EmptyLineHack ""
set /files/etc/ssh/sshd_config/UseDNS no
ins #comment before /files/etc/ssh/sshd_config/UseDNS
set /files/etc/ssh/sshd_config/#comment[following-sibling::*[1][self::UseDNS]] "Disable hostname lookups"

rm /files/etc/ssh/sshd_config/ClientAliveInterval
rm /files/etc/ssh/sshd_config/ClientAliveCountMax
touch /files/etc/ssh/sshd_config/EmptyLineHack
rename /files/etc/ssh/sshd_config/EmptyLineHack ""
set /files/etc/ssh/sshd_config/ClientAliveInterval 900
set /files/etc/ssh/sshd_config/ClientAliveCountMax 0
ins #comment before /files/etc/ssh/sshd_config/ClientAliveInterval
set /files/etc/ssh/sshd_config/#comment[following-sibling::*[1][self::ClientAliveInterval]] "Close inactive client sessions after 15 minutes"
save
quit
EOF
# Configure sshd to listen for v4 connections; disable listening for v6 connections
sudo sed -i 's/^ListenAddress ::/#ListenAddress ::/' $FILESYSTEM_ROOT/etc/ssh/sshd_config
sudo sed -i 's/^#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/' $FILESYSTEM_ROOT/etc/ssh/sshd_config

## Config monit
sudo sed -i '
    s/^# set logfile syslog/set logfile syslog/;
    s/^\s*set logfile \/var/# set logfile \/var/;
    s/^# set httpd port/set httpd port/;
    s/^#    use address localhost/   use address localhost/;
    s/^#    allow localhost/   allow localhost/;
    s/^#    allow admin:monit/   allow admin:monit/;
    s/^#    allow @monit/   allow @monit/;
    s/^#    allow @users readonly/   allow @users readonly/
    ' $FILESYSTEM_ROOT/etc/monit/monitrc

sudo tee -a $FILESYSTEM_ROOT/etc/monit/monitrc > /dev/null <<'EOF'
check filesystem root-overlay with path /
  if space usage > 90% for 5 times within 10 cycles then alert
check filesystem var-log with path /var/log
  if space usage > 90% for 5 times within 10 cycles then alert
check system $HOST
  if memory usage > 50% for 5 times within 10 cycles then alert
  if cpu usage (user) > 90% for 5 times within 10 cycles then alert
  if cpu usage (system) > 90% for 5 times within 10 cycles then alert
check process rsyslog with pidfile /var/run/rsyslogd.pid
  start program = "/bin/systemctl start rsyslog.service"
  stop program = "/bin/systemctl stop rsyslog.service"
  if totalmem > 800 MB for 5 times within 10 cycles then restart
EOF

## Config sysctl
sudo mkdir -p $FILESYSTEM_ROOT/var/core
sudo augtool --autosave "
set /files/etc/sysctl.conf/kernel.core_pattern '|/usr/bin/coredump-compress %e %t %p'

set /files/etc/sysctl.conf/kernel.softlockup_panic 1
set /files/etc/sysctl.conf/kernel.panic 10
set /files/etc/sysctl.conf/vm.panic_on_oom 2
set /files/etc/sysctl.conf/fs.suid_dumpable 2

set /files/etc/sysctl.conf/net.ipv4.conf.default.forwarding 1
set /files/etc/sysctl.conf/net.ipv4.conf.all.forwarding 1
set /files/etc/sysctl.conf/net.ipv4.conf.eth0.forwarding 0

set /files/etc/sysctl.conf/net.ipv4.conf.default.arp_accept 0
set /files/etc/sysctl.conf/net.ipv4.conf.default.arp_announce 0
set /files/etc/sysctl.conf/net.ipv4.conf.default.arp_filter 0
set /files/etc/sysctl.conf/net.ipv4.conf.default.arp_notify 0
set /files/etc/sysctl.conf/net.ipv4.conf.default.arp_ignore 0
set /files/etc/sysctl.conf/net.ipv4.conf.all.arp_accept 0
set /files/etc/sysctl.conf/net.ipv4.conf.all.arp_announce 1
set /files/etc/sysctl.conf/net.ipv4.conf.all.arp_filter 0
set /files/etc/sysctl.conf/net.ipv4.conf.all.arp_notify 1
set /files/etc/sysctl.conf/net.ipv4.conf.all.arp_ignore 2

set /files/etc/sysctl.conf/net.ipv4.neigh.default.base_reachable_time_ms 1800000
set /files/etc/sysctl.conf/net.ipv6.neigh.default.base_reachable_time_ms 1800000

set /files/etc/sysctl.conf/net.ipv6.conf.default.forwarding 1
set /files/etc/sysctl.conf/net.ipv6.conf.all.forwarding 1
set /files/etc/sysctl.conf/net.ipv6.conf.eth0.forwarding 0

set /files/etc/sysctl.conf/net.ipv6.conf.default.accept_dad 0
set /files/etc/sysctl.conf/net.ipv6.conf.all.accept_dad 0
set /files/etc/sysctl.conf/net.ipv6.conf.eth0.accept_dad 0

set /files/etc/sysctl.conf/net.ipv6.conf.default.keep_addr_on_down 1
set /files/etc/sysctl.conf/net.ipv6.conf.all.keep_addr_on_down 1
set /files/etc/sysctl.conf/net.ipv6.conf.eth0.keep_addr_on_down 1

set /files/etc/sysctl.conf/net.ipv6.conf.eth0.accept_ra_defrtr 0
set /files/etc/sysctl.conf/net.ipv6.conf.eth0.accept_ra 0

set /files/etc/sysctl.conf/net.ipv4.tcp_l3mdev_accept 1
set /files/etc/sysctl.conf/net.ipv4.udp_l3mdev_accept 1

set /files/etc/sysctl.conf/net.core.rmem_max 2097152
set /files/etc/sysctl.conf/net.core.wmem_max 2097152
" -r $FILESYSTEM_ROOT

## docker-py is needed by Ansible docker module
sudo https_proxy=$https_proxy LANG=C chroot $FILESYSTEM_ROOT easy_install pip
sudo https_proxy=$https_proxy LANG=C chroot $FILESYSTEM_ROOT pip install 'docker-py==1.6.0'
## Note: keep pip installed for maintainance purpose

## Get gcc and python dev pkgs
sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y install gcc libpython2.7-dev
sudo https_proxy=$https_proxy LANG=C chroot $FILESYSTEM_ROOT pip install 'netifaces==0.10.7'

## Create /var/run/redis folder for docker-database to mount
sudo mkdir -p $FILESYSTEM_ROOT/var/run/redis

## Config DHCP for eth0
sudo tee -a $FILESYSTEM_ROOT/etc/network/interfaces > /dev/null <<EOF

auto eth0
allow-hotplug eth0
iface eth0 inet dhcp
EOF

sudo cp files/dhcp/rfc3442-classless-routes $FILESYSTEM_ROOT/etc/dhcp/dhclient-exit-hooks.d
sudo cp files/dhcp/sethostname $FILESYSTEM_ROOT/etc/dhcp/dhclient-exit-hooks.d/
sudo cp files/dhcp/graphserviceurl $FILESYSTEM_ROOT/etc/dhcp/dhclient-exit-hooks.d/
sudo cp files/dhcp/snmpcommunity $FILESYSTEM_ROOT/etc/dhcp/dhclient-exit-hooks.d/
sudo cp files/dhcp/vrf $FILESYSTEM_ROOT/etc/dhcp/dhclient-exit-hooks.d/
sudo cp files/dhcp/dhclient.conf $FILESYSTEM_ROOT/etc/dhcp/

## Version file
sudo mkdir -p $FILESYSTEM_ROOT/etc/sonic
sudo tee $FILESYSTEM_ROOT/etc/sonic/sonic_version.yml > /dev/null <<EOF
build_version: '$(sonic_get_version)'
debian_version: '$(cat $FILESYSTEM_ROOT/etc/debian_version)'
kernel_version: '$kversion'
asic_type: $sonic_asic_platform
commit_id: '$(git rev-parse --short HEAD)'
build_date: $(date -u)
build_number: ${BUILD_NUMBER:-0}
built_by: $USER@$BUILD_HOSTNAME
EOF

if [ -f sonic_debian_extension.sh ]; then
    ./sonic_debian_extension.sh $FILESYSTEM_ROOT $PLATFORM_DIR
fi

## Organization specific extensions such as Configuration & Scripts for features like AAA, ZTP...
if [ "${enable_organization_extensions}" = "y" ]; then
   if [ -f files/build_templates/organization_extensions.sh ]; then
      sudo chmod 755 files/build_templates/organization_extensions.sh
      ./files/build_templates/organization_extensions.sh -f $FILESYSTEM_ROOT -h $HOSTNAME
   fi
fi

## Setup ebtable rules (rule file is in binary format)
sudo sed -i 's/EBTABLES_LOAD_ON_START="no"/EBTABLES_LOAD_ON_START="yes"/g' ${FILESYSTEM_ROOT}/etc/default/ebtables
sudo cp files/image_config/ebtables/ebtables.filter ${FILESYSTEM_ROOT}/etc

## Debug Image specific changes
## Update motd for debug image
if [ "$DEBUG_IMG" == "y" ]
then
    sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo '**************' >> /etc/motd"
    sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo 'Running DEBUG image' >> /etc/motd"
    sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo '**************' >> /etc/motd"
    sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo '/src has the sources' >> /etc/motd"
    sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo '/src is mounted in each docker' >> /etc/motd"
    sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo '/debug is created for core files or temp files' >> /etc/motd"
    sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo 'Create a subdir under /debug to upload your files' >> /etc/motd"
    sudo LANG=C chroot $FILESYSTEM_ROOT /bin/bash -c "echo '/debug is mounted in each docker' >> /etc/motd"

    sudo mkdir -p $FILESYSTEM_ROOT/src
    pushd src
        ../scripts/dbg_files.sh | sudo tar -cvzf ../$FILESYSTEM_ROOT/src/sonic_src.tar.gz -T -
    popd

    sudo mkdir -p $FILESYSTEM_ROOT/debug

fi

## Remove gcc and python dev pkgs
sudo LANG=C DEBIAN_FRONTEND=noninteractive chroot $FILESYSTEM_ROOT apt-get -y remove gcc libpython2.7-dev

## Update initramfs
sudo chroot $FILESYSTEM_ROOT update-initramfs -u

## Clean up apt
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get -y autoremove
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get autoclean
sudo LANG=C chroot $FILESYSTEM_ROOT apt-get clean
sudo LANG=C chroot $FILESYSTEM_ROOT bash -c 'rm -rf /usr/share/doc/* /usr/share/locale/* /var/lib/apt/lists/* /tmp/*'

## Clean up proxy
[ -n "$http_proxy" ] && sudo rm -f $FILESYSTEM_ROOT/etc/apt/apt.conf.d/01proxy

## Umount all
echo '[INFO] Umount all'
## Display all process details access /proc
sudo LANG=C chroot $FILESYSTEM_ROOT fuser -vm /proc
## Kill the processes
sudo LANG=C chroot $FILESYSTEM_ROOT fuser -km /proc || true
## Wait fuser fully kill the processes
sleep 15
sudo umount $FILESYSTEM_ROOT/proc || true

## Prepare empty directory to trigger mount move in initramfs-tools/mount_loop_root, implemented by patching
sudo mkdir $FILESYSTEM_ROOT/host

## Compress most file system into squashfs file
sudo rm -f $ONIE_INSTALLER_PAYLOAD $FILESYSTEM_SQUASHFS
## Output the file system total size for diag purpose
## Note: -x to skip directories on different file systems, such as /proc
sudo du -hsx $FILESYSTEM_ROOT
sudo mkdir -p $FILESYSTEM_ROOT/var/lib/docker
sudo mksquashfs $FILESYSTEM_ROOT $FILESYSTEM_SQUASHFS -e boot -e var/lib/docker -e $PLATFORM_DIR

## Compress docker files
pushd $FILESYSTEM_ROOT && sudo tar czf $OLDPWD/$FILESYSTEM_DOCKERFS -C var/lib/docker .; popd

## Compress together with /boot, /var/lib/docker and $PLATFORM_DIR as an installer payload zip file
pushd $FILESYSTEM_ROOT && sudo zip $OLDPWD/$ONIE_INSTALLER_PAYLOAD -r boot/ $PLATFORM_DIR/; popd
sudo zip -g $ONIE_INSTALLER_PAYLOAD $FILESYSTEM_SQUASHFS $FILESYSTEM_DOCKERFS
