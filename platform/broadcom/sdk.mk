BRCM_OPENNSL = libopennsl_3.2.2.2-5-20170505212020.37_amd64.deb
$(BRCM_OPENNSL)_URL = "https://sonicstorage.blob.core.windows.net/packages/libopennsl_3.2.2.2-5-20170505212020.37_amd64.deb?sv=2015-04-05&sr=b&sig=wTWOEP8zJE1Jba3M5n8we4x%2Fcpq39%2B00ORByVHhBOuQ%3D&se=2031-01-12T22%3A42%3A51Z&sp=r"

BRCM_OPENNSL_KERNEL = opennsl-modules-3.16.0-4-amd64_3.2.2.2-5-20170505212020.37_amd64.deb
$(BRCM_OPENNSL_KERNEL)_URL = "https://sonicstorage.blob.core.windows.net/packages/opennsl-modules-3.16.0-4-amd64_3.2.2.2-5-20170505212020.37_amd64.deb?sv=2015-04-05&sr=b&sig=QovFF5suqpKxHqZ01r0BiooKw7ik5Kpk6GU0pxf8xmg%3D&se=2031-01-12T22%3A43%3A24Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_OPENNSL) $(BRCM_OPENNSL_KERNEL)
