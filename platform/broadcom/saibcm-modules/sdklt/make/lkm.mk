#
# $Copyright: Copyright 2018-2020 Broadcom. All rights reserved.
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
# Shared makefile include for building Linux kernel modules.
#

# KDIR must point to the Linux kernel sources
ifndef KDIR
nokdir:; @echo 'The $$KDIR variable is not set'; exit 1
endif

# Required for older kernels
export EXTRA_CFLAGS = $(ccflags-y)

PWD := $(shell pwd)

ifneq ($(LKM_BLDDIR),)
#
# If a build directory has been specified, then we symlink all sources
# to this directory and redirect the module build path.
#
# Note that the KBUILD_OUTPUT variable cannot be used to redirect the
# output as we want it.
#
MDIR = $(LKM_BLDDIR)
MSRCS = $(patsubst %.o,%.c,$($(MOD_NAME)-y))
MSRCS += Makefile Kbuild
BSRCS = $(addprefix $(PWD)/,$(MSRCS))
else
#
# Build in current directory by default.
#
MDIR = $(PWD)
endif

all:
	$(Q)echo Building kernel module $(MOD_NAME)
ifneq ($(LKM_BLDDIR),)
ifneq ($(LKM_BLDDIR),$(PWD))
	$(Q)mkdir -p $(MDIR)
	(cd $(MDIR); \
	 rm -rf *.c Makefile Kbuild; \
	 for f in $(BSRCS); do \
	     ln -s $$f; \
	 done)
endif
endif
	$(MAKE) -C $(KDIR) M=$(MDIR)

clean::
	$(Q)echo Cleaning kernel module $(MOD_NAME)
	$(MAKE) -C $(KDIR) M=$(MDIR) clean
ifneq ($(LKM_BLDDIR),)
ifneq ($(LKM_BLDDIR),$(PWD))
# Remove all files except for Makefile (needed by 'make clean')
	rm -f $(LKM_BLDDIR)/*[cdors]
endif
endif

.PHONY: all clean

# Standard documentation targets
-include $(SDK)/make/doc.mk
