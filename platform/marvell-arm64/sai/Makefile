.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

MRVL_SAI_URL = https://github.com/Marvell-switching/SAI-plugin/raw/$(MRVL_SAI_TAG)/sai_deb/$(MRVL_SAI)

$(addprefix $(DEST)/, $(MRVL_SAI)): $(DEST)/% :
	# get deb package
	wget -O $(DEST)/$(MRVL_SAI) $(MRVL_SAI_URL)
