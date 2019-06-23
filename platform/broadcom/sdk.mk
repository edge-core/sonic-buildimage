# mock link here, need to be replaced by real link from MSFT

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-9-amd64_3.4.1.11-10_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/opennsl-modules-3.16.0-9-amd64_3.4.1.11-10_amd64.deb?sv=2015-04-05&sr=b&sig=0C%2BKTCaAOngViNcztUUOEPg1IyC4bgQ8ifUYQAd9EtY%3D&se=2033-02-27T18%3A36%3A46Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL_KERNEL)
