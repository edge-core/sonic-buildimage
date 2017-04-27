BRCM_OPENNSL = libopennsl_3.2.2.2-3~20170427022824.31_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.2.2-3~20170427022824.31_amd64.deb?sv=2015-04-05&sr=b&sig=z7AoBMtlWjYNEv0q3lTN47mb9OIur4HuUTClUVJWawU%3D&se=2154-03-20T05%3A14%3A41Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.2.2-3~20170427022824.31_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.2.2-3~20170427022824.31_amd64.deb?sv=2015-04-05&sr=b&sig=j3TJGtIudpIFDe6ethxEHdW8j4KALG2GTAaRSMN37CM%3D&se=2154-03-20T05%3A15%3A21Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
