BRCM_SAI = libsaibcm_4.3.7.1-6_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.7.1-6_amd64.deb?sv=2021-04-10&st=2022-10-25T06%3A49%3A16Z&se=2037-10-26T06%3A49%3A00Z&sr=b&sp=r&sig=NceGVsZ%2BG9DwI7t82bdQRsXSI5ewZdvx6rtEx8KTB74%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.7.1-6_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.7.1-6_amd64.deb?sv=2021-04-10&st=2022-10-25T06%3A50%3A50Z&se=2037-10-26T06%3A50%3A00Z&sr=b&sp=r&sig=bW8ORoQqQl0SGhWSge8C2KH1FcnELM5wxEZ1lMWgH6w%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
