BRCM_OPENNSL = libopennsl_3.2.2.2-8-20170515203732.42_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.2.2-8-20170515203732.42_amd64.deb?sv=2015-04-05&sr=b&sig=70Ae7gJ9tCEwOiOX4N%2BxJ65uc9W55KmatvW7Yyx2mr8%3D&se=2031-01-23T00%3A01%3A52Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.2.2-8-20170515203732.42_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.2.2-8-20170515203732.42_amd64.deb?sv=2015-04-05&sr=b&sig=K4emi7bcH6UGBukvJJFHo8lgCbK6omuBM16DK4yhRbo%3D&se=2031-01-23T00%3A02%3A19Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
