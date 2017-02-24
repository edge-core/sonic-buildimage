BRCM_OPENNSL = libopennsl_3.2.1.5-7_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.1.5-7_amd64.deb?sv=2015-04-05&sr=b&sig=DY5BPSDturlcHXfqYcS3Gl89Ypd%2BWMYmMLZ2rlNoC5w%3D&se=2030-11-03T11%3A21%3A53Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.1.5-7_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.1.5-7_amd64.deb?sv=2015-04-05&sr=b&sig=glZblgedvf6uOW5k1YpU7NiBWnIZgX5oWvcVsDsYuXc%3D&se=2030-11-03T11%3A22%3A44Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
