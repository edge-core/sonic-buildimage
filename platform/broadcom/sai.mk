BRCM_SAI = libsaibcm_4.3.3.5_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.3.5_amd64.deb?sv=2015-04-05&sr=b&sig=7XHTTf9%2FWBxEqX0Y8g7KqH8t3AFz1dJIZeY3YEDRypc%3D&se=2034-12-30T07%3A06%3A11Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.5_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.3.5_amd64.deb?sv=2015-04-05&sr=b&sig=7I70XjzysspEht%2BsOwCM5QbtCe%2Boelh0%2FfwrhHPGh1g%3D&se=2034-12-30T07%3A06%3A51Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
