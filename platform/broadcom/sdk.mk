BRCM_OPENNSL = libopennsl_3.4.1.5-2_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.4.1.5-2_amd64.deb?sv=2015-04-05&sr=b&sig=gdqovE5An%2F3XffSjP%2F5hT9QB4jLfRsO5Ygm3hJbleRI%3D&se=2031-06-05T21%3A54%3A00Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.4.1.5-2_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.4.1.5-2_amd64.deb?sv=2015-04-05&sr=b&sig=yXB53no4GsaUNDJDUBwdP5SYeNiZSjaSh5USlg3YoJ4%3D&se=2031-06-05T21%3A55%3A14Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
