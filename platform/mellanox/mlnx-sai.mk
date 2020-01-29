# Mellanox SAI

MLNX_SAI_VERSION = SAIRel1.15.5-master

export MLNX_SAI_VERSION

MLNX_SAI = mlnx-sai_1.mlnx.$(MLNX_SAI_VERSION)_amd64.deb
$(MLNX_SAI)_SRC_PATH = $(PLATFORM_PATH)/mlnx-sai
$(MLNX_SAI)_DEPENDS += $(MLNX_SDK_DEBS)
$(MLNX_SAI)_RDEPENDS += $(MLNX_SDK_RDEBS) $(MLNX_SDK_DEBS)
MLNX_SAI_DBGSYM = mlnx-sai-dbgsym_1.mlnx.$(MLNX_SAI_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(MLNX_SAI),$(MLNX_SAI_DBGSYM)))
SONIC_MAKE_DEBS += $(MLNX_SAI)
