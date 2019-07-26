# linux kernel package for marvell arm64

KVERSION= 4.4.8


LINUX_KERNEL= linux-image-4.4.8_4.4.8-4_arm64.deb
$(LINUX_KERNEL)_PATH = /sonic
SONIC_COPY_DEBS += $(LINUX_KERNEL)
