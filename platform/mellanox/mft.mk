# Mellanox SAI

MFT_VERSION = 4.13.3
MFT_REVISION = 6

export MFT_VERSION MFT_REVISION

MFT = mft_$(MFT_VERSION)-$(MFT_REVISION)_amd64.deb
$(MFT)_SRC_PATH = $(PLATFORM_PATH)/mft
$(MFT)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
SONIC_MAKE_DEBS += $(MFT)

KERNEL_MFT = kernel-mft-dkms_$(MFT_VERSION)-$(KVERSION)_all.deb
$(eval $(call add_derived_package,$(MFT),$(KERNEL_MFT)))

MFT_OEM = mft-oem_$(MFT_VERSION)-$(MFT_REVISION)_amd64.deb
$(eval $(call add_derived_package,$(MFT),$(MFT_OEM)))

SONIC_STRETCH_DEBS += $(KERNEL_MFT)
