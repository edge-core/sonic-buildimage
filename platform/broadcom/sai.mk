BRCM_SAI = libsaibcm_6.0.0.10-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/6.0/master/XGS/libsaibcm_6.0.0.10-1_amd64.deb?sv=2015-04-05&sr=b&sig=5fW6otWPCPrsSIXeomEcllS8sEDXMo0YOD8UhB370U0%3D&se=2035-07-22T20%3A50%3A51Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_6.0.0.10-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/6.0/master/XGS/libsaibcm-dev_6.0.0.10-1_amd64.deb?sv=2015-04-05&sr=b&sig=8h7bO9EizzMXduSOf%2Ffc3JH0EcHxcE8p51LyUw0CA6o%3D&se=2035-07-22T20%3A51%3A57Z&sp=r"

# SAI module for DNX Asic family
BRCM_DNX_SAI = libsaibcm_dnx_6.0.0.10-1_amd64.deb
$(BRCM_DNX_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/6.0/master/DNX/libsaibcm_dnx_6.0.0.10-1_amd64.deb?sv=2015-04-05&sr=b&sig=J1lE1SI1Mtwrl0vZ2tAPvkNLKpkyz2XVgRe98DnPNfo%3D&se=2035-07-22T20%3A53%3A24Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
SONIC_ONLINE_DEBS += $(BRCM_DNX_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
