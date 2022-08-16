#
# $Copyright: Copyright 2018-2021 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries.
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License 
# version 2 as published by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# A copy of the GNU General Public License version 2 (GPLv2) can
# be found in the LICENSES folder.$
#

help:
	@echo ''
	@echo 'Build Linux GPL kernel modules for SDKLT.'
	@echo ''
	@echo 'Available make targets:'
	@echo 'kmod          - Build kernel modules'
	@echo 'clean         - Remove object files'
	@echo ''
	@echo 'Supported make variables:'
	@echo 'KDIR          - Linux kernel source directory (mandatory)'
	@echo 'CROSS_COPILE  - Cross-compiler prefix (optional)'
	@echo ''
	@echo 'Examples:'
	@echo 'make -s KDIR=$$KERNEL/linux kmod'
	@echo 'make -s clean'
	@echo ''

ifndef KDIR
nokdir:
	@echo 'Error: The $$KDIR environment variable is not set.'
	@echo '$$KDIR must point to a configured Linux kernel source tree.'
	exit 1
endif

export KDIR
export CROSS_COMPILE

override SDK := $(CURDIR)

kmod: bde knet knetcb

bde:
	$(MAKE) -C $(SDK)/linux/bde SDK=$(SDK) \
		$(TARGET)
	ln -sf $(SDK)/linux/bde/*.ko

knet: bde
	$(MAKE) -C $(SDK)/linux/knet SDK=$(SDK) \
		KBUILD_EXTRA_SYMBOLS=$(SDK)/linux/bde/Module.symvers \
		$(TARGET)
	ln -sf $(SDK)/linux/knet/*.ko

knetcb: knet
	$(MAKE) -C $(SDK)/linux/knetcb SDK=$(SDK) \
		KBUILD_EXTRA_SYMBOLS=$(SDK)/linux/knet/Module.symvers \
		$(TARGET)
	ln -sf $(SDK)/linux/knetcb/*.ko

clean:
	$(MAKE) kmod TARGET=clean
	rm -f *.ko

.PHONY: help kmod bde knet knetcb $(PSAMPLE) clean
