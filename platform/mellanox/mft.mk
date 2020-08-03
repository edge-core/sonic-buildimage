# Mellanox SAI

MFT_VERSION = 4.15.0
MFT_REVISION = 104

export MFT_VERSION MFT_REVISION

MFT = mft_$(MFT_VERSION)-$(MFT_REVISION)_amd64.deb
$(MFT)_SRC_PATH = $(PLATFORM_PATH)/mft
$(MFT)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
SONIC_MAKE_DEBS += $(MFT)

KERNEL_MFT = kernel-mft-dkms-modules-$(KVERSION)_$(MFT_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(MFT),$(KERNEL_MFT)))

MFT_OEM = mft-oem_$(MFT_VERSION)-$(MFT_REVISION)_amd64.deb
$(eval $(call add_derived_package,$(MFT),$(MFT_OEM)))
