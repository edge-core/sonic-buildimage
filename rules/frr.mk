# FRRouting (frr) package

FRR_VERSION = 6.0.2
export FRR_VERSION

FRR = frr_$(FRR_VERSION)-1~sonic.debian9+1_amd64.deb
$(FRR)_DEPENDS += $(LIBSNMP_DEV)
$(FRR)_SRC_PATH = $(SRC_PATH)/sonic-frr
SONIC_MAKE_DEBS += $(FRR)

# FRRouting pythontools
FRR_PYTHONTOOLS = frr-pythontools_$(FRR_VERSION)-1~sonic.debian9+1_amd64.deb
$(FRR_PYTHONTOOLS)_DEPENDS += $(LIBSNMP_DEV)
$(FRR_PYTHONTOOLS)_SRC_PATH = $(SRC_PATH)/sonic-frr
SONIC_MAKE_DEBS += $(FRR_PYTHONTOOLS)
