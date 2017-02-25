BRCM_SAI = libsaibcm_2.1.3.1-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.3.1-3_amd64.deb?sv=2015-04-05&sr=b&sig=j5U8yxIqk4B1Wk8OZp9HbMQ7J9u5GPQNmzTDLilJDjU%3D&se=2030-11-03T20%3A45%3A59Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.3.1-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.3.1-3_amd64.deb?sv=2015-04-05&sr=b&sig=7FPU5S234yjDIPJUUasC%2BRDqPdrJjdOmSodEApzQjTo%3D&se=2030-11-03T20%3A49%3A38Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
