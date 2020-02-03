BRCM_SAI = libsaibcm_3.5.3.4-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.3.4-1_amd64.deb?sv=2015-04-05&sr=b&sig=YWM5jgpf8xVjNyQBo9Kx5CxOTKnnQGumjSiogn6ZY48%3D&se=2033-10-11T20%3A51%3A04Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.4-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.3.4-1_amd64.deb?sv=2015-04-05&sr=b&sig=EmoKe1tSTA2k39xI5kgM6FZMnLETgl75%2B0F9e8XH9N4%3D&se=2033-10-11T20%3A50%3A43Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
