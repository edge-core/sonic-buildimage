BRCM_SAI = libsaibcm_3.7.5.2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.5.2_amd64.deb?sv=2015-04-05&sr=b&sig=wVtVNSk6%2BiWoUefcr%2FeyyI0Z8w1CrRGRryL%2BLLMdBKo%3D&se=2034-05-27T22%3A06%3A37Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.5.2_amd64.deb?sv=2015-04-05&sr=b&sig=Qd0aKbLKiAi3pOZDwL6SfgfKW2eaP6RVfrZSS5YV49s%3D&se=2034-05-27T22%3A07%3A12Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
