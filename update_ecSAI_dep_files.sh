#!/bin/bash

export SONIC_BASE=$1

set +e

## update files for as4630

cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as4630_54pe-r0/Accton-AS4630-54PE/hx5-as4630-48x1G+4x25G+2x100G_ec.bcm  \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as4630_54pe-r0/Accton-AS4630-54PE/hx5-as4630-48x1G+4x25G+2x100G.bcm
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as4630_54te-r0/Accton-AS4630-54TE/hx5-as4630-48x1G+4x25G+2x100G_ec.bcm \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as4630_54te-r0/Accton-AS4630-54TE/hx5-as4630-48x1G+4x25G+2x100G.bcm
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as4630_54te-r0/media_settings_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as4630_54te-r0/media_settings.json

##update files for as5835

cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as5835_54t-r0/Accton-AS5835-54T/mv2-as5835t-48x10G+6x100G_ec.config.bcm  \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as5835_54t-r0/Accton-AS5835-54T/mv2-as5835t-48x10G+6x100G.config.bcm
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as5835_54x-r0/Accton-AS5835-54X/mv2-as5835-48x10G+6x100G_ec.config.bcm \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as5835_54x-r0/Accton-AS5835-54X/mv2-as5835-48x10G+6x100G.config.bcm
rm -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as5835_54x-r0/led_proc_init.soc

##update files for as7326 & as7726

cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as7326_56x-r0/Accton-AS7326-56X/td3-as7326-48x25G+8x100G_ec.config.bcm  \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as7326_56x-r0/Accton-AS7326-56X/td3-as7326-48x25G+8x100G.config.bcm
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as7726_32x-r0/Accton-AS7726-32X/td3-as7726-32x100G_ec.config.bcm \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as7726_32x-r0/Accton-AS7726-32X/td3-as7726-32x100G.config.bcm

##update files for  as9716

cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9716_32d-r0/Accton-AS9716-32D-100G/th3-as9716-32x100G_ec.config.bcm  \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9716_32d-r0/Accton-AS9716-32D-100G/th3-as9716-32x100G.config.bcm
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9716_32d-r0/Accton-AS9716-32D/th3-as9716-32x400G_ec.config.bcm \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9716_32d-r0/Accton-AS9716-32D/th3-as9716-32x400G.config.bcm
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9716_32d-r0/media_settings_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9716_32d-r0/media_settings.json
rm -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9716_32d-r0/Accton-AS9716-32D-100G/media_settings.json

## update files for as9726

cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9726_32d-r0/Accton-AS9726-32D-100G/td4-as9726-32x100G_ec.config.yml \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9726_32d-r0/Accton-AS9726-32D-100G/td4-as9726-32x100G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9726_32d-r0/Accton-AS9726-32D/td4-as9726-32x400G_ec.config.yml \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9726_32d-r0/Accton-AS9726-32D/td4-as9726-32x400G.config.yml
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9726_32d-r0/media_settings_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9726_32d-r0/media_settings.json

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

## update files for as9737
cp -f $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9737_32db-r0/media_settings_ec.json \
         $SONIC_BASE/sonic-buildimage/device/accton/x86_64-accton_as9737_32db-r0/media_settings.json

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
