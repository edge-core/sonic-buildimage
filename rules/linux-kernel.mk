# redis package

KVERSION = 3.16.0-4-amd64

export KVERSION

LINUX_KERNEL = linux-image-3.16.0-4-amd64_3.16.7-ckt11-2+acs8u2_amd64.deb
$(LINUX_KERNEL)_SRC_PATH = $(SRC_PATH)/sonic-linux-kernel
SONIC_MAKE_DEBS += $(LINUX_KERNEL)
