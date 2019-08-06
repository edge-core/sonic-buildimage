.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MRVL_SAI_URL = https://github.com/Marvell-switching/sonic-marvell-binaries/raw/master/armhf/sai-plugin/$(MRVL_SAI)

$(addprefix $(DEST)/, $(MRVL_SAI)): $(DEST)/% :
	# get deb package
	wget -O $(DEST)/$(MRVL_SAI) $(MRVL_SAI_URL)
