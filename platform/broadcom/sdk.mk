BRCM_OPENNSL = libopennsl_3.2.2.2-10-20170707181826.44_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.2.2-10-20170707181826.44_amd64.deb?sv=2015-04-05&sr=b&sig=hc4PbMQvfOu7p7E0MR1kn0OA6vu%2BPIdYOLeDU9hPJMY%3D&se=2031-03-19T21%3A20%3A15Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.2.2-10-20170707181826.44_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.2.2-10-20170707181826.44_amd64.deb?sv=2015-04-05&sr=b&sig=xtGLlxX5SspadCxaObMGGVMQliPGrTkuN0T6A4wLETA%3D&se=2031-03-19T21%3A21%3A43Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
