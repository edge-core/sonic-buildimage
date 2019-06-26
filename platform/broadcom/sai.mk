BRCM_SAI = libsaibcm_3.5.2.3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.2.3_amd64.deb?sv=2015-04-05&sr=b&sig=OCYEP1DOHEVlfy6qjckfME%2FoD%2F914zIueu4UKgNsyQA%3D&se=2156-05-18T17%3A37%3A54Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.5.2.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.2.3_amd64.deb?sv=2015-04-05&sr=b&sig=Ohiw%2FaNhnbB%2FKFn%2BTaZgDrG1ziGfwjwrr2l%2BoIKCmA4%3D&se=2156-05-18T17%3A38%3A34Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
