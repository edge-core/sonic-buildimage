Arista platform support for SONiC
=================================

Copyright (C) 2016 Arista Networks, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

## License

All linux kernel code is licensed under the GPLv2. All other code is
licensed under the GPLv3. Please see the LICENSE file for copies of
both licenses.

## Purpose

This package contains kernel drivers, a python library and a python binary to
provide platform support for Arista switches.

The `arista` tool will identify the platform on which it is running and will
then load and initialise the required kernel drivers. Once initialised, the
system will expose transceivers, leds, fans, temperature sensors and gpios
through the sysfs.

## Supported platforms

The following platforms are currently supported,

 - DCS-7050QX-32
 - DCS-7050QX-32S
 - DCS-7060CX-32
 - DCS-7260CX3-64

Some platforms will require some custom kernel patches.
They are available on the Azure/sonic-linux-kernel repository.

## Usage

This repository contains both a `systemd` and `LSB` init script to properly
integrate with the system startup and shutdown.

Alternatively the `arista` tool can be used in standalone to load and unload
the platform support.

```
   arista --help
```

Since the python library knows about the current platform, it can provides a
common and unified implementation of the SONiC plugins.
Currently supports `eeprom`, `sfputil` and `led_control`.

The python library and tools are python2 and python3 compatible.

## Drivers

The kernel drivers in this repository have currently been tested against a
3.16 and 3.18 based kernel image.

### scd-hwmon vs sonic-support-driver

The `scd-hwmon` is the newer implementation of the scd driver and is used
for all supported platforms except `DCS-7050QX-32` and `DCS-7050QX-32S` which
use `sonic-support driver`.

When the `scd-hwmon` driver is loaded, the various gpios and resets can be set
and unset by writing into the sysfs file.
The meaning of the value `0` or `1` read from or written to is determined by
the name of the sysfs entry.

```
cd /sys/module/scd/drivers/pci:scd/<pciAddr>/
echo 1 > switch_chip_reset
```

When the legacy `sonic-support-driver` is in use, the gpios and resets behave
according to the gpio subsystem of the kernel. The driver will properly set
`value` and `active_low`, whereas `direction` must be set to `out` when
setting the gpio and to `in` when reading it. Read only entries don't have
a `direction` file.

```
cd /sys/module/scd/drivers/pci:scd/<pciAddr>/
echo out > switch_chip_reset/direction
echo 1 > switch_chip_reset/value
echo 0 > switch_chip_reset/value
```

## Components

This section describes how to interact with the various components exposed by
the kernel drivers.
In order to see them, the platform must be successfully initialized.

The following sections describe how to manually interact with the components.
Examples shown may differ across platforms but the logic stays the same.

### LEDs

LED entries can be found under `/sys/class/leds`. Since the sysfs interface
for LEDs is not very expressive, the brightness field is used here
to toggle between off and different colors. The brightness to LED
color mappings are as follows (0 maps to off for all LEDs):

```
status, fan_status, psu1, psu2:
  0 => off
  1 => green
  2 => red

beacon:
  1+ => blue

qsfp:
  1 => green
  2 => yellow

fan:
  1 => green
  2 => red
  3 => yellow
```

Given that this repository is primarily aimed at running on SONiC, an
implementation of the `led_control` plugin is available under
`arista.utils.sonic_leds`. It requires access to the `port_config.ini` file to
translate from `interface name` to `front panel port`.

### Fans

Fans are exposed under `/sys/class/hwmon/*` and respect the
[sysfs-interface](https://www.kernel.org/doc/Documentation/hwmon/sysfs-interface)
guidelines.

This repository provides the kernel modules to handle the fans.

### Temperature sensors

Temperature sensors are exposed under `/sys/class/hwmon/*` and also respect
the [sysfs-interface](https://www.kernel.org/doc/Documentation/hwmon/sysfs-interface).

They are all managed by linux standard modules like `lm73` and `max6658`.

### Power supplies

Power supplies and power controllers can be managed by the kernel's
generic `pmbus` module. Assuming the pmbus module was compiled into the
kernel.

Some power supplies may need kernel patches against the `pmbus` driver.

### System EEPROM

The system eeprom contains platform specific information like the `SKU`, the
`serial number` and the `base mac address`.

The way to read the system eeprom from a platform can differ from one SKU to the
other.
The most reliable way to get this information is by issuing `arista syseeprom`

In the case of SONiC the module `arista.utils.sonic_eeprom` provide the plugin
implementation.

### Transceivers - QSFPs / SFPs

Currently only platforms with QSFP+ and SFP+ ports are supported.
These transceivers provide 2 kind of information.

#### Pins

The first piece of information is obtained from the transceiver physical pins.
 - QSFP: present, reset, low power mode, interrupt, module select
 - SFP: present, rxlos, txfault, txdisable

These knobs are accessible under `/sys/module/scd/drivers/pci:scd/.../`
The name of the entries follow this naming `<type><id>_<pin>`
For example `qsfp2_reset` or `sfp66_txdisable`.

See [this section](#scd-hwmon-vs-sonic-support-driver) on how to use them.

#### Eeproms

The second piece of information provided by a transceiver is the content of its
`eeprom`. It is accessible via `SMBus` at the fixed address `0x50`.

On linux, an unoffical module called `sff_8436_eeprom` can handle such devices.
The arista initialisation library takes care of loading the module for all the
transceivers.
They should then all be available under
`/sys/module/sff_8436_eeprom/drivers/i2c:sff8436`

After instantiation, the EEPROM information can be read like so:

```
root@sonic# hexdump -C /sys/bus/i2c/devices/19-0050/eeprom
00000000  0d 00 02 f0 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000010  00 00 00 00 00 00 19 5c  00 00 7f 9c 00 00 00 00  |.......\........|
00000020  00 00 1f cd 20 2e 26 b8  22 94 00 00 00 00 00 00  |.... .&.".......|
00000030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000070  00 00 00 00 00 04 02 00  00 00 00 00 00 00 00 00  |................|
00000080  0d 00 0c 04 00 00 00 00  00 00 00 05 67 00 00 32  |............g..2|
00000090  00 00 00 00 41 72 69 73  74 61 20 4e 65 74 77 6f  |....Arista Netwo|
000000a0  72 6b 73 20 00 00 1c 73  51 53 46 50 2d 34 30 47  |rks ...sQSFP-40G|
000000b0  2d 53 52 34 20 20 20 20  30 33 42 68 07 d0 46 0d  |-SR4    03Bh..F.|
000000c0  00 00 0f de 58 4d 44 31  34 30 34 30 30 35 56 52  |....XMD1404005VR|
000000d0  20 20 20 20 31 34 30 31  32 36 20 20 08 00 00 d2  |    140126  ....|
000000e0  10 03 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000000f0  00 00 00 00 00 00 02 f8  00 00 00 00 98 44 64 d1  |.............Dd.|
00000100  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000180  40 6b a1 2e 3c f4 2b eb  cd c1 e9 51 50 93 bb fe  |@k..<.+....QP...|
00000190  05 aa 32 3f 1c 4c 00 00  00 00 00 00 00 00 00 00  |..2?.L..........|
000001a0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000200  4b 00 fb 00 46 00 00 00  00 00 00 00 00 00 00 00  |K...F...........|
00000210  8d cc 74 04 87 5a 7a 75  00 00 00 00 00 00 00 00  |..t..Zzu........|
00000220  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000230  55 76 01 be 43 e2 04 62  13 88 00 fa 12 8e 01 f4  |Uv..C..b........|
00000240  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000260  00 00 00 00 00 00 00 00  00 00 00 00 33 33 77 77  |............33ww|
00000270  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000280
```

Before being read, the QSFP+ modules must be taken out of reset and
have their module select signals asserted. This can be done through
the GPIO interface.

### QSFP - SFP multiplexing

On the `DCS-7050QX-32S`, the first QSFP port and the 4 SFP ports are multiplexed.
To choose between one or the other, write into the sysfs file located under
`/sys/modules/scd/drivers/pci:scd/.../mux_sfp_qsfp`

### GPIOs and resets

Most of the GPIOs are exposed by the `scd-hwmon` and the `sonic-support-driver`.
They should be available under `/sys/module/scd/drivers/pci:scd/.../`.
