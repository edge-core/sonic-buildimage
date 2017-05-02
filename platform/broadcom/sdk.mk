BRCM_OPENNSL = libopennsl_3.2.2.2-4-20170428181434.34_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.2.2-4-20170428181434.34_amd64.deb?sv=2015-04-05&sr=b&sig=Izxx7%2ByNMXB11E3rdBuEQNOohGMoDKMCZIsVqfdCjSI%3D&se=2031-01-08T20%3A49%3A30Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.2.2-4-20170428181434.34_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.2.2-4-20170428181434.34_amd64.deb?sv=2015-04-05&sr=b&sig=18MkouZ0zMum2CzLz7ut8nXmjn36nqCNg2go9ISCwKU%3D&se=2031-01-08T20%3A52%3A39Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
