BRCM_OPENNSL = libopennsl_3.2.1.5-5-20170203072429.19_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.1.5-5-20170203072429.19_amd64.deb?sv=2015-04-05&sr=b&sig=ay3U2TMBqVOlDmT75PlLCn0olcjixH96whjjdPM4IGI%3D&se=2030-10-13T19%3A50%3A48Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.1.5-5-20170203072429.19_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.1.5-5-20170203072429.19_amd64.deb?sv=2015-04-05&sr=b&sig=WttrjSL1EtqPA50ZZEn52pOUojMqmP9e7Gdcrj9a%2FVI%3D&se=2030-10-13T19%3A51%3A16Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
