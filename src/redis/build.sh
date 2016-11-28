#!/bin/bash -x

REDIS_VERION=3.2.4
REDIS_VERION_FULL=$REDIS_VERION-1~bpo8+1

wget -O redis_$REDIS_VERION.orig.tar.gz -N "https://sonicstorage.blob.core.windows.net/packages/redis_$REDIS_VERION.orig.tar.gz?sv=2015-04-05&sr=b&sig=B3qGEoSHe%2FBh5rVwvXHpKijgBtKF7dHeuJWp1p17UnU%3D&se=2026-11-26T22%3A31%3A31Z&sp=r"
wget -O redis_$REDIS_VERION_FULL.dsc -N "https://sonicstorage.blob.core.windows.net/packages/redis_$REDIS_VERION_FULL.dsc?sv=2015-04-05&sr=b&sig=LoUtjLXa%2BCcoM%2BsPewRLkY7YPRvSJTbsvQoW%2BL%2B3QWM%3D&se=2026-11-26T22%3A32%3A11Z&sp=r"

wget -O redis_$REDIS_VERION_FULL.debian.tar.xz -N "https://sonicstorage.blob.core.windows.net/packages/redis_$REDIS_VERION_FULL.debian.tar.xz?sv=2015-04-05&sr=b&sig=I33UsbDHiffEkQRndpFwY9y3I%2FrKTu0wmG%2FMXB98kys%3D&se=2026-11-26T22%3A32%3A34Z&sp=r"

dpkg-source -x redis_$REDIS_VERION_FULL.dsc

pushd redis-$REDIS_VERION; fakeroot debian/rules binary; popd

cp *.deb ..
