# linux kernel package for marvell armhf

# Add platform specific DTB
LINUX_KERNEL_DTB = linux-image-4.9.189-armhf.deb
$(LINUX_KERNEL_DTB)_URL = https://github.com/Marvell-switching/sonic-marvell-binaries/raw/master/armhf/kernel/$(LINUX_KERNEL_DTB)
SONIC_ONLINE_DEBS += $(LINUX_KERNEL_DTB)
