BRCM_OPENNSL = libopennsl_3.2.1.5_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.1.5_amd64.deb?sv=2015-04-05&sr=b&sig=qm6%2BkiGuRGsFKwZcUz6yEtbgbbwQuhxEr0chLM7qJEQ%3D&se=2030-09-02T21%3A41%3A11Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.1.5_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.1.5_amd64.deb?sv=2015-04-05&sr=b&sig=c8hO5PQpvod7IX3aYOiyvFB9rICxDgGiFF5g3GDHx84%3D&se=2030-09-02T21%3A42%3A34Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
