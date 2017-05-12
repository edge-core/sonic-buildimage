BRCM_OPENNSL = libopennsl_3.2.2.2-7-20170512003351.39_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.2.2-7-20170512003351.39_amd64.deb?sv=2015-04-05&sr=b&sig=YHETYSIxpB6LyTh2vhQ1TrGXommA2NiUdolk5QBJ0PE%3D&se=2031-01-19T01%3A40%3A27Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.2.2-7-20170512003351.39_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.2.2-7-20170512003351.39_amd64.deb?sv=2015-04-05&sr=b&sig=33kv%2F2UogAuvHu3gPQ1rB7TVp9I%2Bjq%2FbmObzEZgfKD4%3D&se=2031-01-19T01%3A39%3A56Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
