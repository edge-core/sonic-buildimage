.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

LINUX_KERNEL_MRVL_URL = https://github.com/Marvell-switching/sonic-marvell-binaries/raw/master/arm64/kernel/$(LINUX_KERNEL)

$(addprefix $(DEST)/, $(LINUX_KERNEL)): $(DEST)/% :
	# get deb package
	wget -O $(DEST)/$(LINUX_KERNEL) $(LINUX_KERNEL_MRVL_URL)

