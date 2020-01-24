.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

LINUX_KERNEL_MRVL_URL = https://github.com/Marvell-switching/sonic-marvell-binaries/raw/master/arm64/kernel/$(LINUX_KERNEL_DTB)

$(addprefix $(DEST)/, $(LINUX_KERNEL_DTB)): $(DEST)/% :
	# get deb package
	wget -O $(DEST)/$(LINUX_KERNEL_DTB) $(LINUX_KERNEL_MRVL_URL)

