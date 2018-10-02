# FRRouting (frr) package

FRR_VERSION = 4.0
export FRR_VERSION

FRR = frr_$(FRR_VERSION)-1~sonic.debian8+1_amd64.deb
$(FRR)_DEPENDS += $(LIBSNMP_DEV)
$(FRR)_SRC_PATH = $(SRC_PATH)/sonic-frr
SONIC_MAKE_DEBS += $(FRR)
