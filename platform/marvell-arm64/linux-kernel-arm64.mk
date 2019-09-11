# linux kernel package for marvell arm64

KVERSION = 4.9.168


LINUX_KERNEL = linux-image-4.9.168-arm64.deb
export LINUX_KERNEL

$(LINUX_KERNEL)_SRC_PATH = $(PLATFORM_PATH)/linux
SONIC_MAKE_DEBS += $(LINUX_KERNEL)
