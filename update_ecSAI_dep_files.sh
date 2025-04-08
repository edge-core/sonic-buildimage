#!/bin/bash

export SONIC_BASE=$1

set +e

## update files for as4625

cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as4625_54t-r0/Accton-AS4625-54T/hr4-as4625-48x1G+6x10G_ec.config.bcm \
        $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as4625_54t-r0/Accton-AS4625-54T/hr4-as4625-48x1G+6x10G.config.bcm

cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as4625_54p-r0/Accton-AS4625-54P/hr4-as4625-48x1G+6x10G_ec.config.bcm \
        $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as4625_54p-r0/Accton-AS4625-54P/hr4-as4625-48x1G+6x10G.config.bcm        
        

## update files for as9736

cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/platform_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/platform.json
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D/th4-as9736-64x400G_ec.config.yml \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D/th4-as9736-64x400G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D/hwsku_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D/hwsku.json
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D/port_config_ec.ini \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D/port_config.ini
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D-100G/th4-as9736-64x100G_ec.config.yml \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D-100G/th4-as9736-64x100G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D-100G/hwsku_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D-100G/hwsku.json
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D-100G/port_config_ec.ini \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/Accton-AS9736-64D-100G/port_config.ini
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/media_settings_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9736_64d-r0/media_settings.json


## update files for as9817-64

cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64d-r0/Accton-AS9817-64D-100G/th5-as9817-64d-64x100G_ec.config.yml \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64d-r0/Accton-AS9817-64D-100G/th5-as9817-64d-64x100G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64d-r0/Accton-AS9817-64D-400G/th5-as9817-64d-64x400G_ec.config.yml \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64d-r0/Accton-AS9817-64D-400G/th5-as9817-64d-64x400G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64d-r0/Accton-AS9817-64D/th5-as9817-64d-64x800G_ec.config.yml \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64d-r0/Accton-AS9817-64D/th5-as9817-64d-64x800G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64d-r0/media_settings_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64d-r0/media_settings.json


cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64o-r0/Accton-AS9817-64O-100G/th5-as9817-64o-64x100G_ec.config.yml \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64o-r0/Accton-AS9817-64O-100G/th5-as9817-64o-64x100G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64o-r0/Accton-AS9817-64O-2x400G/th5-as9817-64o-128x400G_ec.config.yml \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64o-r0/Accton-AS9817-64O-2x400G/th5-as9817-64o-128x400G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64o-r0/Accton-AS9817-64O/th5-as9817-64o-64x800G_ec.config.yml \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64o-r0/Accton-AS9817-64O/th5-as9817-64o-64x800G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64o-r0/media_settings_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_64o-r0/media_settings.json

## update files for as9817-32
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32d-r0/media_settings_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32d-r0/media_settings.json
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32d-r0/Accton-AS9817-32D/th5-as9817-32d-32x800G_ec.config.yml \
        $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32d-r0/Accton-AS9817-32D/th5-as9817-32d-32x800G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32d-r0/Accton-AS9817-32D-400G/th5-as9817-32d-32x400G_ec.config.yml \
        $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32d-r0/Accton-AS9817-32D-400G/th5-as9817-32d-32x400G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32d-r0/Accton-AS9817-32D-100G/th5-as9817-32d-32x100G_ec.config.yml \
        $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32d-r0/Accton-AS9817-32D-100G/th5-as9817-32d-32x100G.config.yml

cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32o-r0/media_settings_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32o-r0/media_settings.json
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32o-r0/Accton-AS9817-32O/th5-as9817-32o-32x800G_ec.config.yml \
        $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32o-r0/Accton-AS9817-32O/th5-as9817-32o-32x800G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32o-r0/Accton-AS9817-32O-2x400G/th5-as9817-32o-64x400G_ec.config.yml \
        $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32o-r0/Accton-AS9817-32O-2x400G/th5-as9817-32o-64x400G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32o-r0/Accton-AS9817-32O-100G/th5-as9817-32o-32x100G_ec.config.yml \
        $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9817_32o-r0/Accton-AS9817-32O-100G/th5-as9817-32o-32x100G.config.yml
## rebuild sonic-device-data
rm -f $SONIC_BASE/sonic-buildimage/target/debs/bullseye/sonic-device-data_1.0-1_all.deb

set -e
