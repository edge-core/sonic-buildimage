#!/bin/bash

# Install build dependency for snmpd
sudo apt-get -y build-dep snmpd

# download debian net-snmp 5.7.3
wget http://http.debian.net/debian/pool/main/n/net-snmp/net-snmp_5.7.3+dfsg-1.5.dsc
wget http://http.debian.net/debian/pool/main/n/net-snmp/net-snmp_5.7.3+dfsg.orig.tar.xz
wget http://http.debian.net/debian/pool/main/n/net-snmp/net-snmp_5.7.3+dfsg-1.5.debian.tar.xz

dpkg-source -x net-snmp_5.7.3+dfsg-1.5.dsc

pushd net-snmp-5.7.3+dfsg

fakeroot debian/rules binary

popd

cp *.deb ../
