BRCM_OPENNSL = libopennsl_3.2.1.5-6-20170208212127.20_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.1.5-6-20170208212127.20_amd64.deb?sv=2015-04-05&sr=b&sig=VrkDUWofqRz7G70C8%2BGIVtimvNPgnSkCkZccEVPmiIM%3D&se=2030-10-25T02%3A46%3A20Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.1.5-6-20170208212127.20_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.1.5-6-20170208212127.20_amd64.deb?sv=2015-04-05&sr=b&sig=FUNtA7GYpHPoP9QH72VdwLk0yxCUAmEqNmZm%2FEMOUf8%3D&se=2030-10-25T02%3A45%3A34Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
