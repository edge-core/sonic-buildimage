# p4 switch package

P4_SWITCH = p4-switch_1.0.0_amd64.deb
$(P4_SWITCH)_DEPENDS += $(P4C_BM) $(P4_BMV)
$(P4_SWITCH)_RDEPENDS += $(P4C_BM) $(P4_BMV)
$(P4_SWITCH)_SRC_PATH = $(PLATFORM_PATH)/p4-switch
SONIC_MAKE_DEBS += $(P4_SWITCH)
