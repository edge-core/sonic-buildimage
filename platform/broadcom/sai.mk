BRCM_SAI = libsaibcm_3.5.3.7-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.3.7-2_amd64.deb?sv=2019-10-10&st=2021-04-14T19%3A58%3A40Z&se=2036-04-15T19%3A58%3A00Z&sr=b&sp=r&sig=vfB9GZxdlHrJv1bhwCkADDIXe%2FO12dWZYf9i9ya7CGk%3D"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.7-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.3.7-2_amd64.deb?sv=2019-10-10&st=2021-04-14T19%3A57%3A29Z&se=2036-04-15T19%3A57%3A00Z&sr=b&sp=r&sig=DSH1o6MduwF2ZyJRxHdYAQkjBDFWiQx84PKyi6JtmlM%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
