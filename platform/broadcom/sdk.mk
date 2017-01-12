BRCM_OPENNSL = libopennsl_3.2.1.5-2_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.1.5-2_amd64.deb?sv=2015-04-05&sr=b&sig=dWe5YgQv%2FG5VxC4YaKUQEDtDjIygowNhSHyN0Kv3e78%3D&se=2030-09-21T00%3A31%3A21Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.1.5-2_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.1.5-2_amd64.deb?sv=2015-04-05&sr=b&sig=tupvWh%2FYdPn2%2FlCIfsUBjjbpGYSy5PHQvxHutQ4aMPc%3D&se=2030-09-21T00%3A31%3A47Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
