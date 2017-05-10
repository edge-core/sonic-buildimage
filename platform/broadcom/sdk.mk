BRCM_OPENNSL = libopennsl_3.2.2.2-6-20170509231001.38_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.2.2-6-20170509231001.38_amd64.deb?sv=2015-04-05&sr=b&sig=xawExeGCWMMToo%2Fsk%2BNFRHIXK1eJiqOir4lZ5FUvIdo%3D&se=2031-01-17T07%3A00%3A10Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.2.2-6-20170509231001.38_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.2.2-6-20170509231001.38_amd64.deb?sv=2015-04-05&sr=b&sig=PPo0AKc%2FwnaAwNsA2O6e5erAZ4vso6KRXxgrNN%2FlJ3A%3D&se=2031-01-17T07%3A00%3A56Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
