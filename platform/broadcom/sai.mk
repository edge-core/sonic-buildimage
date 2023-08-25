BRCM_XGS_SAI = libsaibcm-1.11_1.0.1+20230824-176_amd64.deb

BRCM_XGS_SAI_DEV = libsaibcm-1.11-dev_1.0.1+20230824-176_amd64.deb
$(eval $(call add_derived_package,$(BRCM_XGS_SAI),$(BRCM_XGS_SAI_DEV)))

$(BRCM_XGS_SAI)_PATH = ec_sai
$(BRCM_XGS_SAI_DEV)_PATH = ec_sai

#SONIC_ECONLINE_DEBS += $(BRCM_SAI)
SONIC_COPY_DEBS += $(BRCM_XGS_SAI)
$(BRCM_XGS_SAI_DEV)_DEPENDS += $(BRCM_XGS_SAI)
$(eval $(call add_conflict_package,$(BRCM_XGS_SAI_DEV),$(LIBSAIVS_DEV)))
