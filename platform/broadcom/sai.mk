BRCM_SAI = libsaibcm_3.5.3.6-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.3.6-2_amd64.deb?sv=2019-10-10&st=2021-01-07T19%3A44%3A15Z&se=2036-01-08T19%3A44%3A00Z&sr=b&sp=r&sig=VgJZNnPYfITkP1pLhisBdNmWKKRuaLCVNWVGgUnUW3Q%3D"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.6-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.3.6-2_amd64.deb?sv=2019-10-10&st=2021-01-07T19%3A42%3A40Z&se=2036-01-08T19%3A42%3A00Z&sr=b&sp=r&sig=V18w8%2BSnrhUXEOJhcyaYXiagBolg0f0Dr0TqsO7YJ9A%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
