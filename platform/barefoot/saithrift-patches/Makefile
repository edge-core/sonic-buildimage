SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

MAIN_TARGET = saithrift-patches

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
# To add some BFN specific patches to SAI under sonic-sairedis while sai is not updated
SRC_DIR = ../saithrift-patches
DST_DIR = ../../../src/sonic-sairedis/SAI.patch/

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# copy patches to SAI
	mkdir -p $(DST_DIR)
	cp -f $(SRC_DIR)/* $(DST_DIR)

	touch $(DEST)/saithrift-patches


