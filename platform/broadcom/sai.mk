BRCM_SAI = libsaibcm_3.1.3.4-24_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.4-24_amd64.deb?sv=2015-04-05&sr=b&sig=wVm5RKLoYiUDC9hlc4FazjA5lJiRpfBvoV%2BzjKTAiZs%3D&se=2033-02-11T21%3A45%3A57Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-24_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.4-24_amd64.deb?sv=2015-04-05&sr=b&sig=lb6aT8JY%2FldniendDehhgBhir1BCVNfS0FTgOIS62oA%3D&se=2033-02-11T21%3A46%3A16Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
