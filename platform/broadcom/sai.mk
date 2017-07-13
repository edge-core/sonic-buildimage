BRCM_SAI = libsaibcm_2.1.5.1-16-20170712202323.49_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-16-20170712202323.49_amd64.deb?sv=2015-04-05&sr=b&sig=jsPXiAoSyKqZ1SmiyeEj73W8tRlri8ysExnWvc%2BWSi4%3D&se=2031-03-21T22%3A49%3A32Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-16-20170712202323.49_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-16-20170712202323.49_amd64.deb?sv=2015-04-05&sr=b&sig=azYZkCi%2FFGS4eELKhIozOok3qimfH%2FjdXlz%2BS2MRBco%3D&se=2031-03-21T22%3A49%3A57Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
