#!/bin/bash -x

wget -N 'http://mirrors.accretive-networks.net/debian/pool/main/r/redis/redis_3.2.4.orig.tar.gz'
wget -N 'http://mirrors.accretive-networks.net/debian/pool/main/r/redis/redis_3.2.4-1~bpo8+1.dsc'
wget -N 'http://mirrors.accretive-networks.net/debian/pool/main/r/redis/redis_3.2.4-1~bpo8+1.debian.tar.xz'

dpkg-source -x redis_3.2.4-1~bpo8+1.dsc

pushd redis-3.2.4; fakeroot debian/rules binary; popd

cp *.deb ..
