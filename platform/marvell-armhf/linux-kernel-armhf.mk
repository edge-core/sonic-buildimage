# linux kernel package for marvell armhf

KVERSION = 4.9.168


LINUX_KERNEL = linux-image-4.9.168-armhf.deb
export LINUX_KERNEL

$(LINUX_KERNEL)_SRC_PATH = $(PLATFORM_PATH)/linux
SONIC_MAKE_DEBS += $(LINUX_KERNEL)
