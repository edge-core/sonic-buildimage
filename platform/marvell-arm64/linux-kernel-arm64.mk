# linux kernel package for marvell arm64

# Add platform specific DTB
LINUX_KERNEL_DTB = linux-image-4.9.168-arm64.deb
$(LINUX_KERNEL_DTB)_URL = https://github.com/Marvell-switching/sonic-marvell-binaries/raw/master/arm64/kernel/$(LINUX_KERNEL_DTB)
SONIC_ONLINE_DEBS += $(LINUX_KERNEL_DTB)
