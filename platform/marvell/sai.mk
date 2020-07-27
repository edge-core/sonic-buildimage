# Marvell SAI

export MRVL_SAI = mrvllibsai_amd64_1.4.1.deb

$(MRVL_SAI)_SRC_PATH = $(PLATFORM_PATH)/sai
$(eval $(call add_conflict_package,$(MRVL_SAI),$(LIBSAIVS_DEV)))

SONIC_MAKE_DEBS += $(MRVL_SAI)
