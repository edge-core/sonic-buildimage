BRCM_OPENNSL = libopennsl_3.2.1.5-3-20170118205520.58_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.1.5-3-20170118205520.58_amd64.deb?sv=2015-04-05&sr=b&sig=R3hWzXrbe4IMSBImAUwK30iSSTIfEtXku6ZYWDX5WhI%3D&se=2030-09-27T22%3A45%3A59Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.1.5-3-20170118205520.58_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.1.5-3-20170118205520.58_amd64.deb?sv=2015-04-05&sr=b&sig=RArOfg5ll6uVbrD0a4VLADHvpJktcJsMSOGYwQ7RZnQ%3D&se=2030-09-27T22%3A49%3A11Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
