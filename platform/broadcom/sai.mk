BRCM_SAI = libsaibcm_3.1.3.5-12_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.5-12_amd64.deb?sv=2015-04-05&sr=b&sig=6%2Fwcn0EN0krkXMCeOpAgo4N2d%2FgiZJAuU%2FwYhaXNpBE%3D&se=2032-08-07T16%3A57%3A37Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.5-12_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.5-12_amd64.deb?sv=2015-04-05&sr=b&sig=9Tf4Rm0Hftx9IavbLmV6PzsxzejuUzwCRFKNmU2pAkU%3D&se=2032-08-07T16%3A57%3A08Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
