BRCM_OPENNSL = libopennsl_3.2.2.2-1-20170406004418.26_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.2.2-1-20170406004418.26_amd64.deb?sv=2015-04-05&sr=b&sig=aWbjpqH2A5JewLoVs8o%2BkriOCRvqDwuVTZygwy%2B1XMQ%3D&se=2030-12-14T19%3A41%3A16Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.2.2-1-20170406004418.26_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.2.2-1-20170406004418.26_amd64.deb?sv=2015-04-05&sr=b&sig=fL88BnMJ9uMMozh6xDqYn7oDc%2FwhX53sd3WG1v%2BkqDA%3D&se=2030-12-14T19%3A40%3A23Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
