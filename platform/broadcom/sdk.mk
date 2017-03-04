BRCM_OPENNSL = libopennsl_3.2.2.2-20170303224751.24_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.2.2-20170303224751.24_amd64.deb?sv=2015-04-05&sr=b&sig=rFu55R4M6M9vJ%2FlJgv6wvp2fbZnKpiHNnhzCddEidgo%3D&se=2030-11-10T23%3A59%3A41Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.2.2-20170303224751.24_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.2.2-20170303224751.24_amd64.deb?sv=2015-04-05&sr=b&sig=DMN91a5PwxG7ow15K1YyHudRF%2F2l0ipAXJ7c1dOW6QY%3D&se=2030-11-11T00%3A00%3A09Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
