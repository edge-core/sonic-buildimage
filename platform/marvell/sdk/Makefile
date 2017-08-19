.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MRVL_FPA_URL = https://github.com/Marvell-switching/SAI-plugin/raw/$(MRVL_FPA_TAG)/sdk_deb/$(MRVL_FPA)

$(addprefix $(DEST)/, $(MRVL_FPA)): $(DEST)/% :
	# get deb package
	wget -O $(DEST)/$(MRVL_FPA) $(MRVL_FPA_URL)
