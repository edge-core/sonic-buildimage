# mock link here, need to be replaced by real link from MSFT

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-6-amd64_3.4.1.11-7_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/opennsl-modules-3.16.0-6-amd64_3.4.1.11-7_amd64.deb?sv=2015-04-05&sr=b&sig=HGePoJSCcURIMW3bPRh5iXlx6z5SWiElmqD44mqUchI%3D&se=2155-08-28T16%3A31%3A48Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL_KERNEL)
